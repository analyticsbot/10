# import the Flask class from the flask module and other required modules
from bs4 import BeautifulSoup
from threading import Thread
from text_unidecode import unidecode
from amazon.api import AmazonAPI
from selenium import webdriver
import pandas as pd
from amazon_api_data1 import *
import time, requests, csv

def getAmazonProducts(asin, amazon):
    data = []
    
    product = amazon.lookup(ItemId=asin, Condition='All', MerchantId='All')
    
    try:
        asin = product.asin
    except:
        asin = 'NA'
    url = 'http://www.amazon.de/dp/' + unidecode(asin)    
    try:
        salesRank = product.sales_rank
    except:
        salesRank = 'NA'
    try:
        Main_Image = product.large_image_url #ok
    except:
        Main_Image = 'NA'
    try:
        Title = unidecode(product.title)#ok
    except:
        Title = 'NA'
    try:
        Price = product.price_and_currency[0]#ok
    except:
        Price = 'NA'

    Stars_and_numbers = {}
    Average_Customer_Review = 'NA'
    Num_of_reviews = 'NA'
    try:
        review = product.reviews[1]
        headers={'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0', 'Content-Type':'application/x-www-form-urlencoded'}
        time.sleep(1)
        response = requests.get(review, headers=headers)
        soup1 = BeautifulSoup(response.content)
        try:
            Average_Customer_Review = soup1.find(attrs={'class':'asinReviewsSummary'}).find('img')['title'].replace('von 5 Sternen','').strip()
        except:
            Average_Customer_Review = 'NA'
        try:
            ReviewCount = unidecode(soup1.find(attrs = {'class':'crIFrameNumCustReviews'}).getText()).replace('\n','').replace('.','').replace('Kundenrezensionen','').strip()[1:-1]
        except:
            ReviewCount = 'NA'
        try:
            ratings_ = soup1.find(attrs={'class':'txtsmaller histogramPPD'}).findAll('div')
            
            Stars_and_numbers = {}
            for i in ratings_:
                try:
                    f = i['title'].replace('der Rezensionen','').strip().split('haben')
                    key = f[0]
                    value= f[1]
                    Stars_and_numbers[key] = value
                except:
                    pass
        except:
            Stars_and_numbers = {}
        try:
            Num_of_reviews = soup1.find(attrs={'class':'crIFrameHeaderHistogram'}).find('b').getText()
        except:
            Num_of_reviews = 'NA'
    except:
        pass
    Stars_and_numbers = str(Stars_and_numbers)
    Product_Link = url
    
    
    Main_Cat = ''#ok
    try:
        ancestors = product.browse_nodes[0].ancestors[::-1]
        current_cat = product.browse_nodes[0].name
        cat_count =0
        for i in ancestors:
            if cat_count == 0:
                Main_Cat= i.name
    except:
        pass
    Main_Cat = unidecode(Main_Cat.text).replace('[','').replace(']','')
    try:
        brand = product.brand#ok
    except:
        brand = 'NA'
    try:
        Shipping_Weight = float(product.get_attribute('PackageDimensions.Weight'))*0.16 
    except:
        Shipping_Weight = 'NA'
    ASIN = asin#ok
    try:
        Sold_and_shipped_by = product.publisher
    except:
        Sold_and_shipped_by = ''
    
    time.sleep(1)
    Amazon_Best_Seller_Rank = salesRank
    product = amazon.lookup(ItemId=asin, ResponseGroup='Offers', Condition='All', MerchantId='All')
    try:
        TotalRefurbished = int(product.parsed_response.OfferSummary.TotalRefurbished)
    except:
        TotalRefurbished = 0
    try:
        TotalNew = product.parsed_response.OfferSummary.TotalNew
    except:
        TotalNew = 0
    TotalOffers = TotalNew + TotalRefurbished
    time.sleep(1)
    g=amazon.lookup(ItemId=asin,  ResponseGroup='OfferFull')

    try:
        Special_Seller = g.parsed_response.Offers.Offer.Merchant.Name
        if Special_Seller == 'Amazon.de':
            Special_Seller = 'Verkauf und Versand durch Amazon.'
        else:
            response = requests.get(url, headers=headers)
            soup2 = BeautifulSoup(response.content)
            Special_Seller = soup2.find(attrs = {'id':'merchant-info'}).getText().replace('\n','').replace('  ','')
    except:
        Special_Seller = 'NA'

    return([Main_Image, Title, brand, asin, Sold_and_shipped_by, Main_Cat, Price,\
                 '', Shipping_Weight, ReviewCount,  Average_Customer_Review, Amazon_Best_Seller_Rank, \
                 TotalOffers, '', '', '', '',\
                             'Ounces', Special_Seller])
   

f=open('I_2.csv', 'rb')
asins = f.read().split('\n')
asins = [d.strip() for d in asins]
num_threads = 2

def downloadData(i, data_, amz):
    df = pd.DataFrame(columns = ['Image' ,'Product Title' , 'Brand', 'ASIN', 'Seller', 'Category', \
                             'Price' , 'Net', 'Weight', 'ReviewCount', 'ReviewsRating', 'Rank',\
                             'Number of Sellers', 'LQS', 'Est. Monthly Sales', 'Est. Rev', 'Fees',\
                             'Weight Type', 'Special Seller Col'])
    f = open('noData_'+str(i)+'.csv', 'wb')
    writer = csv.writer(f)
    for d in data_:
        time.sleep(1)
        searchterm = d.strip()
        #print 'getting data for ', searchterm, ' using thread', i, '\n'
        

        try:
            data = getAmazonProducts(searchterm, amz)
            nrows = df.shape[0]
            if nrows%100==0:
                print 'getting data for ', searchterm, ' using thread', i, nrows, '\n'
            df.loc[nrows+1] = data
        except Exception,e:
            print 'no data for ', searchterm, str(e), '\n'
            writer.writerow([searchterm])
            continue

        

    df.to_csv('data_' + str(i)+'.csv', index = False, encoding = 'utf-8')
    f.close()
    print 'work completed by scraper', i

def split(a, n):
    """Function to split data evenly among threads"""
    k, m = len(a) / n, len(a) % n
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]
            for i in xrange(n))
distributed_ids = list(split(asins, num_threads))
threads = []
for i in range(num_threads):
    data_thread = distributed_ids[i]
    amzn = amazon_api_list1[i]
    threads.append(Thread(target = downloadData, args=(i+1, data_thread,amzn, )))

j=1
for thread in threads:
    print 'starting scraper ##', j
    j+=1
    thread.start()

for thread in threads:
    thread.join()

