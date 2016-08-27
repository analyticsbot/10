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

## function to get technology tickers
## techCSVName -- filename
## _header_tech -- header name of the ticker. Must be present
def getTechTickers(techCSVName, _header_tech, verbosity):
    return pd.unique(pd.read_csv(techCSVName)[_header_tech])

## function to get consumer services tickers
## cnsmrCSVName -- filename. CSV
## _header_cnsmr -- header name of the ticker. Must be present
def getCnsmrSrvcsTickers(cnsmrCSVName, _header_cnsmr, verbosity):
    return pd.unique(pd.read_csv(cnsmrCSVName)[_header_cnsmr])

## function to get finance tickers
## finCSVName -- filename. CSV
## _header_fin -- header name of the ticker. Must be present
def getFinTickers(finCSVName, _header_fin, verbosity):
    return pd.unique(pd.read_csv(finCSVName)[_header_fin])

## function to get NASDAQ tickers
## nsdqCSVName -- filename. CSV
## _header_nsdq -- header name of the ticker. Must be present
def getNasdaqTickers(nsdqCSVName, _header_nsdq, verbosity):
    return pd.unique(pd.read_csv(nsdqCSVName)[_header_nsdq])

## function to get DOW tickers
## dowCSVName -- filename. CSV
## _header_dow -- header name of the ticker. Must be present
def getDOWTickers(dowCSVName, _header_dow, verbosity):
    return pd.unique(pd.read_csv(dowCSVName)[_header_dow])

## function to get SNP tickers
## snpCSVName -- filename. CSV
## _header_snp -- header name of the ticker. Must be present
def getSnPTickers(snpCSVName, _header_snp, verbosity):
    return pd.unique(pd.read_csv(snpCSVName)[_header_snp])
