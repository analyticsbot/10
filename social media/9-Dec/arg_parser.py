
def getArgs(arparser):
    arparser.add_argument("-tkn", "--token", help="crowdkast api token")
    arparser.add_argument("-ng", "--ngainers", help="number of top gainers to be posted on social media")
    arparser.add_argument("-nl", "--nlosers", help="number of top losers to be posted on social media")
    arparser.add_argument("-td", "--typeData", help="type of data that would be posted. E.g. 'forecast, index'",\
                          choices = ['forecast', 'volatility','index'])
    arparser.add_argument("-gn", "--granularity", help="granularity of data to be retrieved",\
                          choices = ['daily', 'weekly','quarterly', 'yearly'])
    arparser.add_argument("-tp", "--typePost", help="type of data that would be posted. E.g. 'technology, finance'",\
                          )
    arparser.add_argument("-fn", "--filenames", help="filenames of the industry specific tickers")
    arparser.add_argument("-hd", "--headers", help="headers in filenames of the industry specific tickers")
    arparser.add_argument("-yr", "--year", help="year in which the scheduler should run. 4-digit year number")
    arparser.add_argument("-mm", "--month", help="month in which the scheduler should run. month number (1-12)")
    arparser.add_argument("-dd", "--day", help="day of month in which the scheduler should run. day of the month (1-31)")
    arparser.add_argument("-ww", "--week", help="week of year in which the scheduler should run. ISO week number (1-53)")
    arparser.add_argument("-hh", "--hour", help="hour of day in which the scheduler should run. hour (0-23)")
    arparser.add_argument("-mn", "--minute", help="minute of the hour in which the scheduler should run. minute (0-59)")
    arparser.add_argument("-ss", "--second", help="second in which the scheduler should run. second (0-59)")
    arparser.add_argument("-dw", "--day_of_week", help="day of week in which the scheduler should run. number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)")
    arparser.add_argument("-tak", "--APP_KEY", help="twitter app key")
    arparser.add_argument("-tas", "--APP_SECRET", help="twitter app secret")
    arparser.add_argument("-tot", "--OAUTH_TOKEN", help="twitter oauth token")
    arparser.add_argument("-tots", "--OAUTH_TOKEN_SECRET", help="twitter oauth token secret")
    arparser.add_argument("-fbpg", "--page_id", help="facebook page id")
    arparser.add_argument("-fbat", "--access_token", help="facebook access token")
    arparser.add_argument("-v", "--verbosity", help="verbosity")
    arparser.add_argument('-t','--trigger', nargs='*', help="whether to trigger the argparser")
        
    args = arparser.parse_args()
    return args

##Available fields for the scheduler
##Field	Description
##year	4-digit year number
##month	month number (1-12)
##day	day of the month (1-31)
##week	ISO week number (1-53)
##day_of_week	number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
##hour	hour (0-23)
##minute	minute (0-59)
##second	second (0-59)

## expressions that can be used with scheduler
# # Expression	Field	Description
# # *	any	Fire on every value
# # */a	any	Fire every a values, starting from the minimum
# # a-b	any	Fire on any value within the a-b range (a must be smaller than b)
# # a-b/c	any	Fire every c values within the a-b range
# # xth y	day	Fire on the x -th occurrence of weekday y within the month
# # last x	day	Fire on the last occurrence of weekday x within the month
# # last	day	Fire on the last day within the month
# # x,y,z	any	Fire on any matching expression; can combine any number of any of the above expressions

