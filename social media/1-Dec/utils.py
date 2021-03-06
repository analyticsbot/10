import pandas as pd
import requests
import xml.etree.ElementTree as ET

## function to generate the api request url for tickers
## ticker - string - name of the ticker. ex - AAPL
## _type - string - whether forecast or volatility
## _granularity - string - whether daily or monthly - should be supported by the api
## token - string - shared by crowdkast
def generateAPI(token, ticker, _type, _granularity, verbosity):
    return 'http://52.32.82.70/'+ _type + '/'+ _granularity + '?token=' + token + '&ticker=' + ticker

## using dataframe to store the values fetched from the api in the following format
## ticker - date - type(forecast/volatility - price
columns = ['ticker', 'date', 'type', 'price']
df = pd.DataFrame(columns=columns)

## function to get data using the api
## ticker - string - name of the ticker. ex - AAPL
## _type - string - whether forecast or volatility
## _granularity - string - whether daily or monthly - should be supported by the api
def getData(token, tickers, _type, _granularity, verbosity):
    for ticker in tickers:
        url = generateAPI(token, ticker, _type, _granularity, verbosity)
        response = requests.get(url)
        nrow = df.shape[0]
        tree = ET.fromstring(response.content) ## parsing the xml response
        children = tree.getchildren()    

        for child in children:
                df.loc[nrow + 1] = [ ticker, child.tag[1:], _type, child.text ]
                nrow += 1
    return df

## function to get all unique tickers from crowdkast database
def  loadUniqueAvailableForecastTickers():    
    return pd.unique(pd.read_csv('Tickers.csv')['Symbol'])

## function to get industry specific tickers
## csvName -- filename
## _header_ -- header name of the ticker. Must be present
def getIndustryTickers(csvName, _header_, verbosity):
    return pd.unique(pd.read_csv(csvName)[_header_])

## generate the gainer and loser text
def generateText(N_gainers, N_losers, df_diff, _type_post):
    """Function to generate relevant text
    Required params: N_gainers, N_losers, df_diff, _type_post
    """
    text_gainers = 'Crowdkast\'s top(' + str(N_gainers)+ ') ' + _type_post + ' percentage gainers -'
    text_losers = 'Crowdkast\'s top(' + str(N_losers)+ ') ' + _type_post + ' percentage losers -'

    max_row = df_diff.shape[0]
    count_gainers = 0
    count_losers = 0
    for i in range(N_gainers):
        try:
            text_gainers += ' $' + df_diff.loc[i, 'ticker'].lower() + ' ' + str(df_diff.loc[i, 'percent-change'])+ '%,'
            count_gainers +=1
        except:
            text_gainers += ''

    for i in range(N_losers):
        try:
            text_losers += ' $' + df_diff.loc[max_row - i -1, 'ticker'].lower() + ' ' +  str(df_diff.loc[max_row - i -1, 'percent-change'])+ '%,'
            count_losers +=1
        except:
            text_losers += ''

    return text_gainers[:-1].replace('(5)','('+str(count_gainers)+')'), text_losers[:-1].replace('(5)','('+str(count_losers)+')')


