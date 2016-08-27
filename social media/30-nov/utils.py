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
def getTickers(verbosity):
    return ['AAPL', 'GOOG', 'YHOO', 'BAC', 'XOM', 'MSFT', 'GOOGL', 'AMAT',\
            'ADSK', 'BIDU', 'ETN']

## function to get industry specific tickers
## csvName -- filename
## _header_ -- header name of the ticker. Must be present
def getIndustryTickers(csvName, _header_, verbosity):
    return pd.unique(pd.read_csv(csvName)[_header_])

