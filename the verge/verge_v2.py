# import all necessary modules
import mechanize
import json
import urllib2
import os
import sys
import string
import time
import random
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
from multiprocessing import Process, Queue
from text_unidecode import unidecode
import logging
import multiprocessing
import math
import os
import boto
from filechunkio import FileChunkIO
from boto.s3.connection import S3Connection
import subprocess
from datetime import datetime
import warnings
from dateutil import parser
from newspaper import Article
warnings.filterwarnings("ignore")

logging.basicConfig(
    filename='verge.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG)

AWS_Access_Key = ''
AWS_Secret_Access_Key = ''
S3_BUCKET_NAME = ''

# Connect to S3
##c = S3Connection(AWS_Access_Key, AWS_Secret_Access_Key)
##b = c.get_bucket(S3_BUCKET_NAME)
b = ''
# if debug is set as True, updates will be printed on sysout
debug = True

if not os.path.exists('success'):
    os.makedirs('success')

if not os.path.exists('failures'):
    os.makedirs('failures')

# read the id name file made after running get_research_id_name.py
# and add to a dictionary which will be used to the name of
# the research field the script is currently working on
# itertate through all the rows of the dataframe
ids = ['longform', 'reviews', 'tech', 'science', 'entertainment',\
       'cars', 'tldr', 'circuitbreaker', 'business/archives', 'business',\
       'design/archives', 'design', 'us-world/archives', 'us-world']


logging.info('Read the put file for research id and name')

# declare all the static variables
num_threads = 2  # number of parallel threads
valid_chars = "-_.() %s%s" % (string.ascii_letters,
                              string.digits)  # valid chars for file names

logging.info('Number of threads ' + str(num_threads))

minDelay = 3  # minimum delay between get requests to www.nist.gov
maxDelay = 7  # maximum delay between get requests to www.nist.gov

logging.info('Minimum delay between each request =  ' + str(minDelay))
logging.info('Maximum delay between each request =  ' + str(maxDelay))

# search_base_urls have the same pattern
# just need to change the research field and page on the first and
search_base_url = 'http://www.theverge.com/{topic}/{page}'

def trimArticle(articleText, DIVIDE_ARTICLE):
    article_distributed = articleText.split()
    len_article = len(article_distributed)
    if len_article>DIVIDE_ARTICLE:
        new_article = ''
        for i in range(DIVIDE_ARTICLE):
            new_article = new_article + ' ' + article_distributed[i]
        
        while True:
            i+=1
            new_article = new_article + ' ' + article_distributed[i]
            if new_article.endswith('.'):
                break
    else:
        new_article = articleText
    return new_article.strip()

def uploadDataS3(source_path, b):
    # Get file info
    source_size = os.stat(source_path).st_size

    # Create a multipart upload request
    mp = b.initiate_multipart_upload(os.path.basename(source_path))

    # Use a chunk size of 50 MiB (feel free to change this)
    chunk_size = 52428800
    chunk_count = int(math.ceil(source_size / float(chunk_size)))

    # Send the file parts, using FileChunkIO to create a file-like object
    # that points to a certain byte range within the original file. We
    # set bytes to never exceed the original file size.
    for i in range(chunk_count):
        offset = chunk_size * i
        bytes = min(chunk_size, source_size - offset)
        with FileChunkIO(source_path, 'r', offset=offset,
                         bytes=bytes) as fp:
            mp.upload_part_from_file(fp, part_num=i + 1)

    # Finish the upload
    mp.complete_upload()


def split(a, n):
    """Function to split data evenly among threads"""
    k, m = len(a) / n, len(a) % n
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]
            for i in xrange(n))

def getLinks(
        i,
        data,
        queue,
        debug,
        minDelay,
        maxDelay):
    """ Function to pull out all publication links from nist
    data - research ids pulled using a different script
    queue  -  add the publication urls to the list
    research_name_id - dictionary with research id as key and name as value
    proxies - scraped proxies
    """
    for d in data:

        # pg_idx is the page index for the research search results.
        # break the while loop if there are no more search results
        # add the links to a local list, and the length to another list
        pg_idx = 1
        local_queue = []
        len_local_queue = [1111, 222, 333, 4444]

        while True:
            url = search_base_url.replace(
                '{topic}', str(d)).replace(
                '{page}', str(pg_idx))
            if debug:
                sys.stdout.write('Visting url :: ' + url + '\n')

            logging.info('Visting url :: ' + url + '\n')
            pg_idx += 1
            len_local_queue.append(len(local_queue))

            # if the last 2 elements of the local queue are same it means
            # no new data is being added. Exit the loop
            if len_local_queue[-2] == len_local_queue[-1]:
                break

            # intatiate mechanize browser, read the response and pass it to
            # soup
            br = mechanize.Browser()
            logging.info(
                'Intantiated a browser for thread :: ' +
                str(i) +
                '\n')

            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:14.0) Gecko/20100101 Firefox/14.0.1',
                'Referer': 'http://www.nist.com'}

            # wrap the request.
            request = urllib2.Request(url, None, header)

            try:
                br.open(request)
            except:
                logging.info('url does not exist' + url)
                break

            html = br.response().read()
            soup = BeautifulSoup(html, 'lxml')

            a = soup.findAll('a')
            count_links = 0
            for i in a:
                try:
                    if 'theverge.com' in i['href'] and i['href'].count('/') >4:
                        count_links+=1
                        queue.put(i['href'])
                        logging.info(
                            'Added publication to queue :: ' + str(i['href']) + '\n')
                        if i['href'] not in local_queue:
                            local_queue.append(i['href'])
                except:
                    pass
            if count_links ==0 :
                logging.info('Breaking. No more articles found for topic : ' + str(d))
                break
            else:
                logging.info('Number of articles found for topic : ' + str(count_links))
            wait_time = random.randint(minDelay, maxDelay)
            if debug:
                sys.stdout.write('Sleeping for :: ' + str(wait_time) + '\n')

            logging.info('Sleeping for :: ' + str(wait_time) + '\n')
            time.sleep(wait_time)


def thevergeArticles(i, queue, debug, minDelay, maxDelay, b):
    while True:
        try:
            url = queue.get()
        except:
            time.sleep(1)
            continue
        if url is None:
            break
            sys.exit(1)

        if debug:
            sys.stdout.write('Visting publication url :: ' + url + '\n' + '\n')

        logging.info('Visting publication url :: ' + url + '\n' + '\n')

        article = Article(url)
        article.download()
        article.parse()
        try:
            authors = article.authors
        except:
            authors = ''
        try:
            publish_date = str(article.publish_date.replace(second=0).isoformat().replace(':00+00:00', '+00:00'))
            publish_date = article.publish_date
        except:
            publish_date = ''
        try:
            date = str(datetime(publish_date.year, publish_date.month, publish_date.day).isoformat())[:-3] +'+00:00' # .replace(':00+00:00', '+00:00')
        except Exception,e:
            date = ''
        try:
            text = article.text
        except:
            text = ''
        try:
            top_image = article.top_image
        except:
            top_image = ''
        try:
            movies = article.movies
        except:
            movies = ''
        article.nlp()
        try:
            keywords = article.keywords
        except:
            keywords = ''
        try:
            summary = article.summary
        except:
            summary = ''
        if summary == '':
            summary = trimArticle(text, 50)
        images = {}
        try:
            all_images = article.images
            if len(all_images)>0:
                for i in range(len(all_images)):
                    images['image_' + str(i)] = all_images[i]
                
        except:
            pass
        try:
            abstract = article.meta_description
        except:
            abstract = ''
        try:
            title = article.title
        except:
            title = ''

        # write the fellow summary to file
        file_name = 'theverge_' + title.replace(' ', '_') + '.json'
        file_name = ''.join(c for c in file_name if c in valid_chars)
        
        if os.name == 'nt':
            f = open('success//' + file_name , 'wb')
        else:
            f = open('success/' + file_name , 'wb')
        folder = 'success'
        logging.info(
            'Opened ' +
            'success//' +
            file_name +
            '.json' +
            ' for writing')
        
        data = {
            'abstract': summary,
            'external_id': 'theverge_' + title.replace(' ', '-'),
            'date': str(date),
            'url': url,
            'title': title,
            'words': text,
            'meta': {'theverge': {
                             'keywords': str(keywords),
                             'top_image': top_image,
                             'authors': authors,
                             'allImages': str(images)
                             }
                     }
            }

        f.write(json.dumps(data))
        f.close()
        logging.info('File written ' + file_name)
##        if os.name == 'nt':
##            uploadDataS3(folder + '//' + file_name, b)
##        else:
##            uploadDataS3(folder + '/' + file_name, b)
        if debug:
            sys.stdout.write(file_name + ' has been written to S3 bucket' + '\n')
        logging.info(file_name + ' has been written to S3 bucket' + '\n')
        
        if debug:
            sys.stdout.write(file_name + ' written' + '\n')
        wait_time = random.randint(minDelay, maxDelay)
        sys.stdout.write('Sleeping for :: ' + str(wait_time) + '\n')
        logging.info('Sleeping for :: ' + str(wait_time) + '\n')
        sys.stdout.write(
            '******************************************' + '\n')
        sys.stdout.write(
            '******************************************' + '\n')
        time.sleep(wait_time)

distributed_ids = list(split(list(ids), num_threads))
if __name__ == "__main__":
    # declare an empty queue which will hold the publication ids
    manager = multiprocessing.Manager()
    queue = manager.Queue()

    logging.info('Initialized an empty queue')

    threads = []
    for i in range(num_threads):
        data_thread = distributed_ids[i]
        threads.append(
            Process(
                target=getLinks,
                args=(
                    i + 1,
                    data_thread,
                    queue,
                    debug,
                    minDelay,
                    maxDelay,

                )))

    dataThreads = []
    for i in range(2*num_threads):
        dataThreads.append(
            Process(
                target=thevergeArticles,
                args=(
                    i + 1,
                    queue,
                    debug,
                    minDelay,
                    maxDelay,
                    b,

                )))

    j = 1
    for thread1 in threads:
        sys.stdout.write('starting link scraper ##' + str(j) + '\n')
        logging.info('starting link scraper ##' + str(j) + '\n')
        j += 1
        thread1.start()

    time.sleep(10)
    j = 1
    for thread in dataThreads:
        sys.stdout.write('starting verge scraper ##' + str(j) + '\n')
        logging.info('starting verge scraper ##' + str(j) + '\n')
        j += 1
        thread.start()

    try:
        for worker in threads:
            worker.join(10)

    except KeyboardInterrupt:
        print 'Received ctrl-c'
        for worker in threads:
            worker.terminate()
            worker.join(10)
    queue.put(None)
    try:
        for worker in dataThreads:
            worker.join(10)
    except KeyboardInterrupt:
        print 'Received ctrl-c'
        for worker in dataThreads:
            worker.terminate()
            worker.join(10)
