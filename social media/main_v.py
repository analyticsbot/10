## import all required modules
import logging
import pandas as pd
from social_media import *
from apscheduler.schedulers.blocking import BlockingScheduler
from config_parser import *
from arg_parser import *
import argparse
from utils import *
from dateutil.relativedelta import relativedelta

arparser = argparse.ArgumentParser()
args = getArgs(arparser)

if verbosity:
    print 'Default arguments from config file loaded'
    
if args.trigger is not None:
    if verbosity:
        print 'Overwriting arguments from command line'
    if args.token:
        token = args.token
    if args.ngainers:
        ngainers = int(args.ngainers)
    if args.nlosers:
        nlosers = int(args.nlosers)
    if args.typeData:
        typeData = args.typeData
    if args.granularity:
        granularity = args.granularity
    if args.typePost:
        typePost = [t.strip() for t in args.typePost.replace("'",'').split(',')]
    if args.filenames:
        filenames = [f.strip() for f in args.filenames.replace("'",'').split(',')]
        headers = [h.strip() for h in args.headers.replace("'",'').split(',')]
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
        verbosity = int(args.verbosity)

## initializing the scheduler class
sched = BlockingScheduler()

## iniatializing dataframe to store the %change in the ticker price
columns_diff = ['ticker', 'percent-change']

## function to calculate the %change by applying the condion(current data and previous date present)
## , sort by %change and post 5 handles on social media (fb + twitter)
def calculateDifferenceAndPostSocialMedia(df, N_gainers, N_losers, columns_diff, _granularity, _type_post, _filenames, _headers, verbosity):
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
            tickers = getIndustryTickers(_filename, _headers[ix], verbosity)
            if verbosity:
                print 'technology gainers and losers tickers being calculated'
        elif _type_post[ix] == 'finance':
            tickers = getIndustryTickers(_filename, _headers[ix], verbosity)
            if verbosity:
                print 'finance gainers and losers tickers being calculated'
        elif _type_post[ix] == 'consumer_services':
            tickers = getIndustryTickers(_filename, _headers[ix], verbosity)
            if verbosity:
                print 'consumer services gainers and losers tickers being calculated'
        elif _type_post[ix] == 'nasdaq':
            tickers = getIndustryTickers(_filename, _headers[ix], verbosity)
            if verbosity:
                print 'Nasdaq gainers and losers tickers being calculated'
        elif _type_post[ix] == 'dow':
            tickers = getIndustryTickers(_filename, _headers[ix], verbosity)
            if verbosity:
                print 'DOW gainers and losers tickers being calculated'
        elif _type_post[ix] == 'snp':
            tickers = getIndustryTickers(_filename, _headers[ix], verbosity)
            if verbosity:
                print 'SNP gainers and losers tickers being calculated'
    
        for ticker in tickers:
            df_ = df.query('ticker == "' + ticker + '"').reset_index(drop=True)
            if df_.shape[0] > 0:
                nrow_diff = df_diff.shape[0]
                if verbosity:
                    print 'calculating data for :: ', ticker, ' for granularity :: ', _granularity
                ## the next line checks if data for the previous date to the most recent date is available
                ## if yes, calculate the %change, else move to the next ticker
                if _granularity =='daily':
                    try:
                        index = df_[df_['date'] == (df_.loc[0,'date'] + relativedelta(days=-1))].index.tolist()[0]
                        change = 100*(float(df_.loc[0,'price'])-float(df_.loc[index,'price']))/float(df_.loc[index,'price'])
                        df_diff.loc[nrow_diff] = [ ticker, float("%.2f" % change) ]
                        nrow_diff += 1
                        status = 'Job Done'
                    except:
                        status = 'No Data'
                elif _granularity =='weekly':
                    try:
                        index = df_[df_['date'] == (df_.loc[0,'date'] + relativedelta(weeks=-3))].index.tolist()[0]
                        change = 100*(float(df_.loc[0,'price'])-float(df_.loc[index,'price']))/float(df_.loc[index,'price'])
                        df_diff.loc[nrow_diff] = [ ticker, float("%.2f" % change) ]
                        nrow_diff += 1
                        status = 'Job Done'
                    except:
                        status = 'No Data'
                elif _granularity =='quarterly':
                    try:
                        index = df_[df_['date'] == (df_.loc[0,'date'] + relativedelta(months=-3))].index.tolist()[0]
                        change = 100*(float(df_.loc[0,'price'])-float(df_.loc[index,'price']))/float(df_.loc[index,'price'])
                        df_diff.loc[nrow_diff] = [ ticker, float("%.2f" % change) ]
                        nrow_diff += 1
                        status = 'Job Done'
                    except:
                        status = 'No Data'
                elif _granularity =='yearly':
                    try:
                        index = df_[df_['date'] == (df_.loc[0,'date'] + relativedelta(years=-1))].index.tolist()[0]
                        change = 100*(float(df_.loc[0,'price'])-float(df_.loc[index,'price']))/float(df_.loc[index,'price'])
                        df_diff.loc[nrow_diff] = [ ticker, float("%.2f" % change) ]
                        nrow_diff += 1
                        status = 'Job Done'
                    except:
                        status = 'No Data'

        ## sort the tickers by % change in descending order    
        df_diff = df_diff.sort('percent-change', ascending = False).reset_index(drop=True)
        
        text = generateText(N_gainers, N_losers, df_diff, _type_post[ix])
        print text
        
        ## post to fb and twitter
        fb = FacebookPost(pageid, accesstoken)
        tw = TwitterPost(APPKEY, APPSECRET, OAUTHTOKEN, OAUTHTOKENSECRET)

        if 'top(0)' not in text[0]:
            fb.postToFacebook(text[0])## gainers
            tw.postToTwitter(text[0]) ## gainers
        else: 
            print "Nothing to post for {0} top gainers".format(_granularity)

        if 'top(0)' not in text[1]:
            fb.postToFacebook(text[1])## losers
            tw.postToTwitter(text[1]) ## losers
        else: 
            print "Nothing to post for {0} top losers".format(_granularity)
        print "Status: {0}".format(status)
    if verbosity:
        print 'Gainers and losers for ', _type_post, ' posted to twitter and facebook'

    return status

def main():
    tickers = loadUniqueAvailableForecastTickers()
    df = getData(token, tickers, typeData)
    if df.shape[0] > 0:
        status = calculateDifferenceAndPostSocialMedia(df, Ngainers, Nlosers, columns_diff, granularity, typePost, filenames, headers, verbosity)
    else:
        status = 'No Data or Cant fetch via the API'
        
    return status

if __name__ == "__main__":
    ## initialize the scheduler option. this is based on the local machine time
    ## runs at midnight 01-44-40
    sched.configure({'misfire_grace_time': 1000})
    @sched.scheduled_job('cron', year= year, month= month, day=day, week=week, day_of_week=day_of_week, hour=hour, minute=minute, second=second)
    def timed_job():
        logging.basicConfig()
        print 'starting the job'
        status = main()
        print status
 
    sched.start()



