## import all required modules
import requests, logging
import xml.etree.ElementTree as ET
import pandas as pd
import facebook
from twython import Twython
from apscheduler.schedulers.blocking import BlockingScheduler
from ConfigParser import SafeConfigParser

## initializing the config parser
parser = SafeConfigParser()
parser.read('config.cfg')
## initializing the scheduler class
sched = BlockingScheduler()

""" ## setting up static variables ## """
## token for accessing the api from crowdkast
token = parser.get('crowdkast', 'token').replace("'",'')
N = int(parser.get('crowdkast', 'N').replace("'",'')) ## number of tickers to post on social media

## twitter oauth keys
APP_KEY, APP_SECRET = parser.get('twitter', 'APP_KEY').replace("'",''), parser.get('twitter', 'APP_SECRET').replace("'",'')
OAUTH_TOKEN, OAUTH_TOKEN_SECRET = parser.get('twitter', 'OAUTH_TOKEN').replace("'",''), parser.get('twitter', 'OAUTH_TOKEN_SECRET').replace("'",'') 

## facebook oauth tokens and page id
page_id, access_token = parser.get('facebook', 'page_id').replace("'",''), parser.get('facebook', 'access_token').replace("'",'')

## using dataframe to store the values fetched from the api in the following format
## ticker - date - type(forecast/volatility - price
columns = ['ticker','date', 'type', 'price']
df = pd.DataFrame(columns=columns)

## iniatializing another dataframe to store the %change in the ticker price
columns_diff = ['ticker', 'percent-change']
df_diff = pd.DataFrame(columns=columns_diff)

## function to generate the api request url for tickers
## ticker - string - name of the ticker. ex - AAPL
## _type - string - whether forecast or volatility
## _granularity - string - whether daily or monthly - should be supported by the api
## token - string - shared by crowdkast
def generateAPI(ticker, _type, _granularity):
    return 'http://52.32.82.70/'+ _type + '/'+ _granularity + '?token=' + token + '&ticker=' + ticker

## function to get data using the api
## ticker - string - name of the ticker. ex - AAPL
## _type - string - whether forecast or volatility
## _granularity - string - whether daily or monthly - should be supported by the api
def getData(ticker, _type, _granularity):
    url = generateAPI(ticker, _type, _granularity)
    response = requests.get(url)
    nrow = df.shape[0]
    tree = ET.fromstring(response.content) ## parsing the xml response
    children = tree.getchildren()    

    for child in children:
            df.loc[nrow + 1] = [ ticker, child.tag[1:], _type, child.text ]
            nrow += 1

## function to get all unique tickers
def getTickers():
    return ['AAPL', 'GOOG', 'YHOO', 'BAC', 'XOM', 'MSFT']

## function to calculate the %change by applying the condion(current data and previous date present)
## , sort by %change and post 5 handles on social media (fb + twitter)
def calculateDifferenceAndPostSocialMedia(tickers, df_diff):
    for ticker in tickers:
        df_ = df.query('ticker == "' + ticker + '"')
        df_ = df_.sort('date', ascending = False).reset_index(drop=True)
        nrow_diff = df_diff.shape[0]

        ## the next line checks if data for the previous date to the most recent date is available
        ## if yes, calculate the %change, else move to the next ticker
        if int(df_.loc[0,'date'])-int(df_.loc[1,'date']) >= 1:
            nrow_diff += 1
            change = 100*(float(df_.loc[0,'price'])-float(df_.loc[1,'price']))/float(df_.loc[0,'price'])
            df_diff.loc[nrow_diff + 1] = [ ticker, float("%.2f" % change) ]

    ## sort the tickers by % change in descending order    
    df_diff = df_diff.sort('percent-change', ascending = False).reset_index(drop=True)
    print df_diff
    text = 'Crowdkasts top percentage gainers -'
    for i in range(N):
        try:
            text += ' $' + df_diff.loc[i, 'ticker'].lower()
        except:
            text += ''
    print text
    ## post to fb
    #postToFacebook(text)

    ## post to twitter
    #postToTwitter(text)

    print 'top 5 stocks posted on twitter and facebook'

## function to post a message to a facebook page
def postToFacebook(message):
  cnfig = {
    "page_id"      : page_id,
    "access_token" : access_token   
    }

  api = get_api_fb(cnfig)
  status = api.put_wall_post(message)

def get_api_fb(cnfig):
  graph = facebook.GraphAPI(cnfig['access_token'])
  resp = graph.get_object('me/accounts')
  page_access_token = None
  for page in resp['data']:
    if page['id'] == cnfig['page_id']:
      page_access_token = page['access_token']
  graph = facebook.GraphAPI(page_access_token)
  return graph

## function to post a message to twitter
def postToTwitter(status):
    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    twitter.update_status(status=status)

def main():
    _type, _granularity = parser.get('crowdkast', '_type').replace("'",''), parser.get('crowdkast', '_granularity').replace("'",'')    
    tickers = getTickers()   

    for ticker in tickers:
        getData(ticker, _type, _granularity)

    calculateDifferenceAndPostSocialMedia(tickers, df_diff)

if __name__ == "__main__":
    ## initialize the scheduler option. this is based on the local machine time
    ## runs at midnight 01-44-40
    main()
    hour, minute, second = parser.get('scheduler', 'hour'), parser.get('scheduler', 'minute'), parser.get('scheduler', 'second')
    sched.configure({'misfire_grace_time': 100000})
    @sched.scheduled_job('cron', day_of_week='mon-sun', hour=hour, minute=minute, second=second)
    def timed_job():
        logging.basicConfig()
        print 'starting the job'
        main()
        
    sched.start()

    
    
