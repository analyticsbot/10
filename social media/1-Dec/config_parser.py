from ConfigParser import SafeConfigParser
import sys

## initializing the config parser
parser = SafeConfigParser()
parser.read('config.cfg')

""" ## setting up static variables ## """
## token for accessing the api from crowdkast
token = parser.get('crowdkast', 'token').replace("'",'')
## number of tickers to post on social media
Ngainers, Nlosers = int(parser.get('crowdkast', 'Ngainers').replace("'",'')), \
                       int(parser.get('crowdkast', 'Nlosers').replace("'",'')) 

## posting schedule
year, month, day, week, day_of_week, hour, minute, second = parser.get('scheduler', 'year'), \
                                                            parser.get('scheduler', 'month'), \
                                                            parser.get('scheduler', 'day'), \
                                                            parser.get('scheduler', 'week'),\
                                                            parser.get('scheduler', 'day_of_week'), \
                                                            parser.get('scheduler', 'hour'), \
                                                            parser.get('scheduler', 'minute'), \
                                                            parser.get('scheduler', 'second')

## other settings
typeData, granularity, typePost = parser.get('crowdkast', 'typeData').replace("'",''), \
                      parser.get('crowdkast', 'granularity').replace("'",''),\
                      [t.strip() for t in parser.get('crowdkast', 'typePost').replace("'",'').split(',')]

filenames, headers = [f.strip() for f in parser.get('crowdkast', 'filenames').replace("'",'').split(',')], \
                     [h.strip() for h in parser.get('crowdkast', 'headers').replace("'",'').split(',')]

## twitter oauth keys
APPKEY, APPSECRET = parser.get('twitter', 'APP_KEY').replace("'",''), \
                      parser.get('twitter', 'APP_SECRET').replace("'",'')
OAUTHTOKEN, OAUTHTOKENSECRET = parser.get('twitter', 'OAUTH_TOKEN').replace("'",''), \
                                  parser.get('twitter', 'OAUTH_TOKEN_SECRET').replace("'",'') 

## facebook oauth tokens and page id
pageid, accesstoken = parser.get('facebook', 'page_id').replace("'",''), \
                        parser.get('facebook', 'access_token').replace("'",'')

## general settings
verbosity = int(parser.get('settings', 'verbosity').replace("'",''))

## necessary checks
if len(filenames)>=1:
    if len(filenames)!= len(headers):
        raise Exception('Filenames for tickers and header names don\'t match. Check the config file')
        sys.exit(1)
else:
    raise Exception('Filenames for tickers and header names not provided. Check the config file')
    sys.exit(1)

