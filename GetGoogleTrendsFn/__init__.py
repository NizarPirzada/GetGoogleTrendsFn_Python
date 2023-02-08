import azure.functions as func
import pandas as pd
from pytrends.request import TrendReq
import json
import uuid
import time
import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
monthly_delta = 6
today = datetime.today()

def get_trends_fromkeyword(keyword):
    trends_data = {}
    try:
        tz = 0
        hl = 'es-US'
        pytrends = TrendReq(hl=hl, tz=tz)
        start_date = datetime(2020, 1, 1)
        end_date = min(start_date + relativedelta(months=+monthly_delta), today)
        result_df = pd.DataFrame()

        while end_date <= today:
            end_date_str = end_date.strftime('%Y-%m-%d')
            start_date_str = start_date.strftime('%Y-%m-%d')

            pytrends.build_payload(kw_list=[keyword], timeframe=start_date_str + ' ' + end_date_str)
            interest_over_time_df = pytrends.interest_over_time()
            result_df = pd.concat([result_df, interest_over_time_df])
            if end_date == today:
                break
            start_date = end_date + timedelta(days=1)
            end_date = min(start_date + relativedelta(months=+monthly_delta), today)
            time.sleep(3)
        if not result_df.empty:
            result_df.reset_index(inplace=True)
            result_df["date"] = result_df["date"].dt.strftime('%Y-%m-%d')
            result_df.drop('isPartial', inplace=True, axis=1)
            result_df = result_df.rename(columns={keyword:"value"})

            trends_data = result_df.to_dict('records')
        
    except ValueError:
        pass
    return trends_data

def TrendingSearches():
    trendingsearches = []
    tz = 0
    hl = 'es-US'
    pytrends = TrendReq(hl=hl, tz=tz)
    trending_df = pytrends.trending_searches(pn='united_states')
    trending_df.columns = ["topics"]
    trendingsearches = trending_df['topics'].tolist()
    return trendingsearches
def main(req: func.HttpRequest) -> func.HttpResponse:
    kind = req.params.get('kind')
    if not kind:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            kind = req_body.get('kind')
    keyword = req.params.get('keyword')
    if not keyword:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            keyword = req_body.get('keyword')
    if kind == "InterestOverTime" and keyword:
        trends = get_trends_fromkeyword(keyword)
        data = {
            'Trends':trends
        }
        return func.HttpResponse( json.dumps(data, indent=4, sort_keys=True, default=str),status_code=200 )
    elif kind == "TrendingSearches":
        trends = TrendingSearches()
        data = {
            'Trends':trends
        }
        return func.HttpResponse( json.dumps(data, indent=4, sort_keys=True, default=str),status_code=200 )
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
