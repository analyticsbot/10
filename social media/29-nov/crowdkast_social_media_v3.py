## import all required modules
import logging
import pandas as pd
from social_media import *
from apscheduler.schedulers.blocking import BlockingScheduler
from config_parser import *
from arg_parser import *
import argparse
from utils import *

arparser = argparse.ArgumentParser()
args = getArgs(arparser)

if verbosity:
    print 'All arguments from config file loaded'
    
if args:
    print 'All arguments from command line loaded'
    if args.token:
        token = args.token
    if args.ngainers:
        ngainers = args.ngainers
    if args.nlosers:
        nlosers = args.nlosers
    if args.typeData:
        typeData = args.typeData
    if args.granularity:
        granularity = args.granularity
    if args.typePost:
        typePost = args.typePost
    if args.filenames:
        filenames = args.filenames
        headers = args.headers
    if args.year:
        year = args.year
    if args.month:
        month = args.month
    if args.day:
        day = args.day
    if args.week:
        week = args.week
    if args.hour:
        hour = args.hour
    if args.minute:
        minute = args.minute
    if args.second:
        second = args.second
    if args.day_of_week:
        day_of_week = args.day_of_week
    if args.APP_KEY:
        APP_KEY = args.APP_KEY
    if args.APP_SECRET:
        APP_SECRET = args.APP_SECRET
    if args.OAUTH_TOKEN:
        OAUTH_TOKEN = args.OAUTH_TOKEN
    if args.OAUTH_TOKEN_SECRET:
        OAUTH_TOKEN_SECRET = args.OAUTH_TOKEN_SECRET
    if args.page_id:
        page_id = args.page_id
    if args.access_token:
        access_token = args.access_token
    if args.verbosity:
        verbosity = args.verbosity

## initializing the scheduler class
sched = BlockingScheduler()

## iniatializing dataframe to store the %change in the ticker price
columns_diff = ['ticker', 'percent-change']

## function to calculate the %change by applying the condion(current data and previous date present)
## , sort by %change and post 5 handles on social media (fb + twitter)
def calculateDifferenceAndPostSocialMedia(N_gainers, N_losers, columns_diff, _granularity, _type_post, _filenames, _headers, verbosity):
    """Function to calculate the %change in difference for tickers and post to twitter
    N_gainers: top n gainers to be posted. integer
    N_losers: top n losers to be posted. integer
    columns_diff: names of column in the difference dataframe
    _granularity: granularity of data required
    _type_post: industry specific tickers
    _filenames: filenames of the industry tickers
    _headers: headers of the filenames that have tickers
    verbosity: should the code be verbose
    """    
    for _filename in _filenames:
        df_diff = pd.DataFrame(columns=columns_diff)
        ix = _filenames.index(_filename)
        if _type_post[ix] == 'technology':
            tickers = getTechTickers(_filename, _headers[ix], verbosity)
            if verbosity:
                print 'technology gainers and losers tickers being calculated'
        elif _type_post[ix] == 'finance':
            tickers = getFinTickers(_filename, _headers[ix], verbosity)
            if verbosity:
                print 'finance gainers and losers tickers being calculated'
        elif _type_post[ix] == 'consumer_services':
            tickers = getCnsmrSrvcsTickers(_filename, _headers[ix], verbosity)
            if verbosity:
                print 'consumer services gainers and losers tickers being calculated'
        elif _type_post[ix] == 'nasdaq':
            tickers = getNasdaqTickers(_filename, _headers[ix], verbosity)
            if verbosity:
                print 'Nasdaq gainers and losers tickers being calculated'
        elif _type_post[ix] == 'dow':
            tickers = getDOWTickers(_filename, _headers[ix], verbosity)
            if verbosity:
                print 'DOW gainers and losers tickers being calculated'
        elif _type_post[ix] == 'snp':
            tickers = getSnPTickers(_filename, _headers[ix], verbosity)
            if verbosity:
                print 'SNP gainers and losers tickers being calculated'
    
        for ticker in tickers:
            df_ = df.query('ticker == "' + ticker + '"')
            if df_.shape[0] > 0:
                df_ = df_.sort('date', ascending = False).reset_index(drop=True)
                nrow_diff = df_diff.shape[0]
                if verbosity:
                    print 'calculating data for :: ', ticker, ' for granularity :: ', _granularity
                ## the next line checks if data for the previous date to the most recent date is available
                ## if yes, calculate the %change, else move to the next ticker
                if _granularity =='daily' and int(df_.loc[0,'date'])-int(df_.loc[1,'date']) == 1:
                    _granularity_retrieved = 'daily'
                    nrow_diff += 1
                    change = 100*(float(df_.loc[0,'price'])-float(df_.loc[1,'price']))/float(df_.loc[0,'price'])
                    df_diff.loc[nrow_diff + 1] = [ ticker, float("%.2f" % change) ]
                elif _granularity =='weekly' and int(df_.loc[0,'date'])-int(df_.loc[1,'date']) == 7:
                    _granularity_retrieved = 'weekly'
                    nrow_diff += 1
                    change = 100*(float(df_.loc[0,'price'])-float(df_.loc[1,'price']))/float(df_.loc[0,'price'])
                    df_diff.loc[nrow_diff + 1] = [ ticker, float("%.2f" % change) ]
                elif _granularity =='quarterly' and int(df_.loc[0,'date'])-int(df_.loc[1,'date']) in [299, 300]:
                    _granularity_retrieved = 'quarterly'
                    nrow_diff += 1
                    change = 100*(float(df_.loc[0,'price'])-float(df_.loc[1,'price']))/float(df_.loc[0,'price'])
                    df_diff.loc[nrow_diff + 1] = [ ticker, float("%.2f" % change) ]
                elif _granularity =='yearly' and int(df_.loc[0,'date'])-int(df_.loc[1,'date']) in [10000, 10001]:
                    _granularity_retrieved = 'yearly'
                    nrow_diff += 1
                    change = 100*(float(df_.loc[0,'price'])-float(df_.loc[1,'price']))/float(df_.loc[0,'price'])
                    df_diff.loc[nrow_diff + 1] = [ ticker, float("%.2f" % change) ]
                else:
                    _granularity_retrieved = None
                    print 'the granularity entered does not match the granularity received. Sticking to whatever received'
                    nrow_diff += 1
                    change = 100*(float(df_.loc[0,'price'])-float(df_.loc[df_.shape[0],'price']))/float(df_.loc[0,'price'])
                    df_diff.loc[nrow_diff + 1] = [ ticker, float("%.2f" % change) ]

        ## sort the tickers by % change in descending order    
        df_diff = df_diff.sort('percent-change', ascending = False).reset_index(drop=True)
        
        if _granularity_retrieved:
            ## to be used later when daily, weekly posting is to be done
            text = generateText(N_gainers, N_losers, df_diff, _type_post[ix])
        else:
            text = generateText(N_gainers, N_losers, df_diff, _type_post[ix])

        print text[0], '\n', text[1], '\n'
        ## post to fb
        postToFacebook(text[0], pageid, accesstoken) ## gainers
        postToFacebook(text[1], pageid, accesstoken) ## losers
        ## post to twitter
        postToTwitter(text[0], APPKEY, APPSECRET, OAUTHTOKEN, OAUTHTOKENSECRET) ## gainers
        postToTwitter(text[1], APPKEY, APPSECRET, OAUTHTOKEN, OAUTHTOKENSECRET) ## losers

    if verbosity:
        print 'Top 5 gainers and losers for ', _type_post, ' posted to twitter and facebook'

def main():
    tickers = getTickers(verbosity)
    df = getData(token, tickers, typeData, granularity, verbosity)
    calculateDifferenceAndPostSocialMedia(Ngainers, Nlosers, columns_diff, granularity, typePost, filenames, headers, verbosity)

if __name__ == "__main__":
    ## initialize the scheduler option. this is based on the local machine time
    ## runs at midnight 01-44-40
    sched.configure({'misfire_grace_time': 100000})
    @sched.scheduled_job('cron', year= year, month= month, day=day, week=week, day_of_week=day_of_week, hour=hour, minute=minute, second=second)
    def timed_job():
        logging.basicConfig()
        print 'starting the job'
        main()
        
    sched.start()

    
    
