## required imports
from __future__ import print_function

import xml.etree.ElementTree as ET
import json, argparse, requests, sys, shutil, os, hashlib, time, struct
from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random
from PIL import Image
import os, sys

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import urllib, mimetypes
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
    
## static variables
finalOutputDirectory = 'e:\\finished'
remotePath = '/media/'
localPath = 'z:\\'
windows = 1
posterFileName = 'poster'
imageBaseName = 'background'
# the block size for cipher obj, can be 16 24 or 32. 16 matches 128 bit.
IV_SIZE = 16
BLOCK_SIZE = 32
cipher_mode = 'CBC'
USE_ENCRYPTION = True
GOOGLE_DRIVE_ROOT_DIR = ''
   
## parsing data from the command line
arparser = argparse.ArgumentParser()
arparser.add_argument("-i", "--seriesid", help="tv show ids. Eg - '1,2,3'")
arparser.add_argument("-s", "--seasonid", help="tv season. Eg - '1,2,3'")
arparser.add_argument("-e", "--episodeid", help="tv show's season's episode. Eg - '1,2,3'")
arparser.add_argument("-d", "--drive", help="google drive or local. Eg - 'google, local'")
args = arparser.parse_args()

## parse args from the command line
series_id = [i.strip() for i in args.seriesid.split()][0] ## possible vales 1,2,3,4....
season_id_list = [i.strip() for i in args.seasonid.split()] ## possible values 1,2,3....
episode_list = [i.strip() for i in args.episodeid.split()][0] ## possible values - 1,2,3..... or all
try:
    drive = [i.strip() for i in args.drive.split()][0]
except:
    drive = 'local'
## use this for testing
##season_id_list = ['1']
##series_id = 2529
##episode_list = ['1']#'all'

SCOPES = 'https://www.googleapis.com/auth/drive.file'
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secrets.json', SCOPES)
    creds = tools.run_flow(flow, store, flags) \
            if flags else tools.run(flow, store)
DRIVE = build('drive', 'v3', http=creds.authorize(Http()))

def uploadFiles(filename, mimeType, parentId):
    """Function to upload files"""
    metadata = {'name': filename.split('\\')[-1], 'parents': [parentId]}
    if mimeType:
        metadata['mimeType'] = mimeType
    res = DRIVE.files().create(body=metadata, media_body=filename).execute()
    if res:
        print('UPLOADED "%s"' % (filename))
    return res['id']

def createRemoteFolder(folderName, parentID):
        # Create a folder on Drive, returns the newly created folder ID
        body = {
          'name': folderName,
          'mimeType': "application/vnd.google-apps.folder"
        }
        if parentID:
            body['parents'] = [parentID]
        root_folder = DRIVE.files().create(body = body).execute()
        return root_folder['id']


def encrypt(in_file, out_file, key, iv):
    bs = AES.block_size
    cipher = AES.new(key, AES.MODE_CBC, iv)
    finished = False
    while not finished:
        chunk = in_file.read(1024 * bs)
        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = bs - (len(chunk) % bs)
            chunk += padding_length * chr(padding_length)
            finished = True
        out_file.write(cipher.encrypt(chunk))
    
#### check whether ids have been passed. Else exit
if not id or not season_id_list or not episode_list:
    print ('No TV Show Ids or Season or Episode provided. Nothing to do. Exiting!')
    sys.exit(1)

def plexURL():
    """Function to add the base url"""
    return 'http://192.168.1.2:32400/'

def getHash(name):
    """Function to hash the movie name"""
    return hashlib.md5(name).hexdigest()
    
## 1. Retrieve required elements
def firstAPICall(id):
    """ function to check if the type==movie for a given id
    id - id passed via the command line
    """
    response = requests.get(plexURL() + 'library/metadata/' + str(id)+ '/children')
    e = ET.fromstring(response.text.encode('ascii', 'ignore'))
    #e = ET.parse(open('XML_First_Call_-_TV_Show_-_Main.txt'))
    elements = e.getiterator()

    for elem in elements:
        if elem.tag == 'Directory':

            # series level data
            series_title = elements[0].get('parentTitle')
            series_thumb = plexURL() + elements[0].get('thumb')[1:]
            series_art = plexURL() + elements[0].get('art')[1:]
            series_basicDescription = elements[0].get('summary')
            series_release_date = elements[0].get('parentYear')

            # season level data
            season_id = elem.get('index')
            
            if season_id in season_id_list:
                season_index = elem.get('ratingKey')
                season_thumb = plexURL() + elem.get('thumb')[1:]
                season_title = elem.get('title')
                break

    return elements, series_title, series_thumb, series_art, series_basicDescription, series_release_date, \
                                    season_index, season_thumb, season_title, season_id

def getData(id):
    """Function to retrieve the required elements from the xml response
    id - id passed via command line
    element - parsed xml element
    """
    response = requests.get(plexURL() + 'library/metadata/' + str(id)+ '/children')
    e = ET.fromstring(response.text.encode('ascii', 'ignore'))
    #e = ET.parse(open('XML_Second_Call_-_TV_Show_-_Season.txt'))
    elements = e.getiterator()

    returnData = []   
    for elem in elements:
        if elem.tag == 'Video':
            episode_index = elem.get('index')
            if (episode_index in episode_list) or (episode_list == 'all'):
                episode_title =  elem.get('title')
                episode_key = elem.get('key')
                episode_summary =  elem.get('summary')
                episode_year = elem.get('year')
                episode_thumb = plexURL() + elem.get('thumb')[1:]
                episode_duration = elem.get('duration')
                episode_contentRating = elements[0].get('grandparentContentRating')
                episode_videoFrameRate =  elements[elements.index(elem) + 1].get('videoFrameRate')
                if windows==1:
                    episode_file_ = elements[elements.index(elem) + 2].get('file').replace(remotePath, localPath).replace('/', '\\')
                else:
                    episode_file_ = elements[elements.index(elem) + 2].get('file')
                returnData.append([episode_title, episode_summary, episode_year, episode_thumb, episode_duration, episode_contentRating, episode_videoFrameRate, episode_file_, episode_index])

    return returnData

## 2. Download art and thumb images and save to same directory as where
##    mp4box will output to
def downloadImage(series_title, season_title, episode_title, name, url, cipher_mode, key, iv, USE_ENCRYPTION):
    """Function to download the images - art & thumb
    url - url of the image on the server
    """
    if series_title and not season_title and not episode_title:
        # create the directory if it doesn't exists
        if not os.path.exists(getHash(series_title)):
            os.makedirs(getHash(series_title))
        # download the image    
        response = requests.get(url, stream=True)    
        with open(getHash(series_title)+ "/"+ name +'_.jpg', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        if USE_ENCRYPTION: encrypt(open(getHash(series_title)+ "/"+ name +'_.jpg', 'rb'), open(getHash(series_title)+ "/"+ name +'.jpg', 'wb'), key, iv)
        if USE_ENCRYPTION: os.remove(getHash(series_title)+ "/"+ name +'_.jpg')
    if series_title and season_title and not episode_title:
        # create the season directory inside the series directory if it doesn't exists
        if not os.path.exists(getHash(series_title) + '/' + getHash(season_title)):
            os.makedirs(getHash(series_title) + '/' + getHash(season_title))

        # download the image    
        response = requests.get(url, stream=True)    
        with open(getHash(series_title) + '/' + getHash(season_title) + "/"+ name +'_.jpg', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        if USE_ENCRYPTION: encrypt(open(getHash(series_title) + '/' + getHash(season_title) + "/"+ name +'_.jpg', 'rb'),  open(getHash(series_title) + '/' + getHash(season_title) + "/"+ name +'.jpg', 'wb'), key, iv)
        if USE_ENCRYPTION: os.remove(getHash(series_title) + '/' + getHash(season_title) + "/"+ name +'_.jpg')
    if series_title and season_title and episode_title:
        # create the episode directory inside the series, season directory if it doesn't exists
        if not os.path.exists(getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title)):
            os.makedirs(getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title))
        # download the image    
        response = requests.get(url, stream=True)    
        with open(getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title)+ "/"+ name +'_.jpg', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        if USE_ENCRYPTION: encrypt(open(getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title)+ "/"+ name +'_.jpg', 'rb'), open(getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title)+ "/"+ name +'.jpg', 'wb'), key, iv)
        if USE_ENCRYPTION: os.remove(getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title)+ "/"+ name +'_.jpg')
## 3. FFMPEG command:
def FFMPEGCommand(file_, videoFrameRate):
    """Function to execute the ffmpeg command
    file_ - parsed from the xml response. Eg."/media/Movies/Polar Express, The (2004)/The Polar Express- Blu-ray 1080p.mkv"
    videoFrameRate - parse from xml response
    """
    command = 'ffmpeg -y -i "'+file_+'" -map 0:1 -c:a copy -t 300 -map_metadata -1 audio0.mp4 -map 0:1 -c:a ac3 -t 300 -map_metadata -1 audio1.mp4 -map 0:1 -c:a aac -ac 2 -ab 320k -t 300 -map_metadata -1 audio2.mp4 -map 0:0 -c:v libx265 -x265-params "profile=main:level=4.1:keyint=' + str(4*int(videoFrameRate[:-1])) + ':min-keyint=' + str(4*int(videoFrameRate[:-1])) + ':scenecut=0" -crf 18 -sc_threshold 0 -flags +cgop -movflags faststart -pix_fmt yuv420p -t 300 -map_metadata -1 video1080hevc.mp4 -map 0:0 -c:v libx265 -x265-params "profile=main:level=4.1:keyint=' + str(4*int(videoFrameRate[:-1])) + ':min-keyint=' + str(4*int(videoFrameRate[:-1])) + ':scenecut=0" -crf 18 -sc_threshold 0 -flags +cgop -movflags faststart -pix_fmt yuv420p -t 300 -map_metadata -1 -vf "scale=min(1280\,iw):trunc(ow/a/2)*2" video720hevc.mp4 -map 0:0 -c:v libx265 -x265-params "profile=main:level=4.1:keyint=' + str(4*int(videoFrameRate[:-1])) + ':min-keyint=' + str(4*int(videoFrameRate[:-1])) + ':scenecut=0" -crf 18 -sc_threshold 0 -flags +cgop -movflags faststart -pix_fmt yuv420p -t 300 -map_metadata -1 -vf "scale=min(480\,iw):trunc(ow/a/2)*2" video480hevc.mp4 -map 0:0 -c:v libx264 -x264opts keyint=' + str(4*int(videoFrameRate[:-1])) + ':min-keyint=' + str(4*int(videoFrameRate[:-1])) + ':no-scenecut -sc_threshold 0 -flags +cgop -profile:v baseline -level 4.1 -crf 18 -maxrate 4000k -bufsize 4000k -vf "scale=min(1280\,iw):trunc(ow/a/2)*2" -movflags faststart -pix_fmt yuv420p -t 300 -map_metadata -1 video720.mp4 -map 0:0 -c:v libx264 -x264opts keyint=' + str(4*int(videoFrameRate[:-1])) + ':min-keyint=' + str(4*int(videoFrameRate[:-1])) + ':no-scenecut -sc_threshold 0 -flags +cgop -profile:v baseline -level 4.1 -crf 18 -maxrate 1500k -bufsize 1500k -vf "scale=min(854\,iw):trunc(ow/a/2)*2" -movflags faststart -pix_fmt yuv420p -t 300 -map_metadata -1 video480.mp4'
    status = os.system(command)
    return status, command

## 4. MP4Box command
def MP4BoxCommand(series_title, season_title, episode_title):
    """Function to run the MP4Box executable"""
    command =  "MP4Box -dash 5000 -rap -frag-rap -profile onDemand -out " + \
              getHash(series_title) +'/' + getHash(season_title) + '/' + getHash(episode_title)+ "/dash.mpd video1080hevc.mp4 video720hevc.mp4 video480hevc.mp4 video720.mp4 video480.mp4 audio0.mp4 audio1.mp4 audio2.mp4"
    status = os.system(command)
    return status, command

## 5. Update main json database file adding this item
def updateJsonFile(series_title, series_summary, series_release_date, series_art, series_thumb, \
                               episode_videoFrameRate, episode_summary, episode_year, episode_thumb, episode_duration, \
                               episode_contentRating, episode_file_, episode_index, key, season_index):
    """Function to update the json file"""
    jsonFile = open("output.json")
    global data
    data = json.load(jsonFile)
    jsonFile.close()
    data['updateDate'] = int(time.time()*1000)
    data['mediaEncryptionKey'] = key

    ## check if series exists
    series_exists = 0
    data['groups'][0]['id'] = "14501699205860001"
    data['groups'][0]['title'] = "Recently Added"
    data['groups'][0]['cloudStorageId'] = "20075775"
    data['groups'][0]['cloudStorageType'] = 1
    data['groups'][0]['orderNo'] = 1
    series_all = data['groups'][0]['items']
    for series in series_all:
        if series['id'] == getHash(series_title):
            series_exists += 1
            ix_series = series_all.index(series)
            
            # series exists
            ## check if season exists
            season_exists = 0
            seasons_all = data['groups'][0]['items'][ix_series]['seasons']
            for season_ in seasons_all:
                if getHash(series_title + '-' + season_title) == season_['id']:
                    season_exists +=1
                    ix_season = seasons_all.index(season_)
                    
                    ## season exists
                    ## check if episode exists
                    episodes_all = data['groups'][0]['items'][ix_series]['seasons'][ix_season]['episodes']
                    episode_exists = 0
                    for episode in episodes_all:
                        if getHash(series_title + '-' + season_title + '-' + episode_title) == episode['id']:
                            episode_exists += 1
                            # episode exists. change the values of this episode to new values
                            ix = episodes_all.index(episode)
                            
                            episodes_all[ix] = {
                                          "id": getHash(series_title + '-' + season_title + '-' + episode_title),
                                          "title": episode_title,
                                          "releaseDate": "0000-00-00",
                                          "cloudStorageId": "20075775",
                                	  "cloudStorageType": 1,
                                          "posterBaseUrl": getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title)+ "/poster.jpg",
                                          "imageBaseUrl": getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title)+ "/background.jpg",
                                          "rating": "",
                                          "description": {
                                            "basicDescription": episode_summary,
                                            "fieldPairs": []
                                          },
                                          "trailerUrl": "",
                                          "seasonId": getHash(series_title + '-' + season_title),
                                          "seriesId": getHash(series_title),
                                          "orderNo": episode_index,
                                          "fileProperties": {
                                            "URL": getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title) + "/dash.mpd",
                                            "resolution": "",
                                            "videoCodec": "",
                                            "audioFormat": "",
                                            "audioChannelsInfo": "",
                                            "runningTime": "",
                                            "languagesList": [],
                                            "subtitleOptionsList": []
                                          }
                                        }
                    # add the episode since it does not exist
                    if episode_exists == 0:
                         episodes_all.append({
                                      "id": getHash(series_title + '-' + season_title + '-' + episode_title),
                                      "title": episode_title,
                                      "releaseDate": "0000-00-00",
                                      "cloudStorageId": "20075775",
                                      "cloudStorageType": 1,
                                      "posterBaseUrl": getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title) + '/' + "poster.jpg",
                                      "imageBaseUrl": getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title) + '/' + "background.jpg",
                                      "rating": "",
                                      "description": {
                                        "basicDescription": episode_summary,
                                        "fieldPairs": []
                                      },
                                      "trailerUrl": "",
                                      "seasonId": getHash(series_title + '-' + season_title),
                                      "seriesId": getHash(series_title),
                                      "orderNo": episode_index,
                                      "fileProperties": {
                                        "URL": getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title) + "/dash.mpd",
                                        "resolution": "",
                                        "videoCodec": "",
                                        "audioFormat": "",
                                        "audioChannelsInfo": "",
                                        "runningTime": "",
                                        "languagesList": [],
                                        "subtitleOptionsList": []
                                      }
                                    })
            # add the season since it does not exist
            if season_exists == 0:
                        seasons_all.append({
                                      "id": getHash(series_title + '-' + season_title),
                                      "title": season_title,
                                      "releaseDate": "0000-00-00",
                                      "cloudStorageId": "20075775",
                                      "cloudStorageType": 1,
                                      "posterBaseUrl": getHash(series_title) + '/' + getHash(season_title) + "/poster.jpg",
                                      "imageBaseUrl": getHash(series_title) + '/' + getHash(season_title) + "/background.jpg",
                                      "rating": "",
                                      "description": {
                                        "basicDescription": "",
                                        "fieldPairs": []
                                      },
                                      "trailerUrl": "",
                                      "seriesId": getHash(series_title),
                                      "orderNo": season_index,
                                      "episodes": [
                                        {
                                          "id":  getHash(series_title + '-' + season_title + '-' + episode_title),
                                          "title": episode_title,
                                          "releaseDate": "0000-00-00",
                                          "cloudStorageId": "20075775",
                                          "cloudStorageType": 1,
                                          "posterBaseUrl": getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title) + '/' + "poster.jpg",
                                          "imageBaseUrl": getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title) + '/' + "background.jpg",
                                          "rating": "",
                                          "description": {
                                            "basicDescription": episode_summary,
                                            "fieldPairs": []
                                          },
                                          "trailerUrl": "",
                                          "seasonId": getHash(series_title + '-' + season_title),
                                          "seriesId": getHash(series_title),
                                          "orderNo": 1,
                                          "fileProperties": {
                                            "URL": getHash(series_title)+ '/' + getHash(season_title) + '/' + getHash(episode_title) + "/dash.mpd",
                                            "resolution": "",
                                            "videoCodec": "",
                                            "audioFormat": "",
                                            "audioChannelsInfo": "",
                                            "runningTime": "",
                                            "languagesList": [],
                                            "subtitleOptionsList": []
                                          }
                                        }
                                      ]
                                    })
                             

    # the series does not exists. Add the series, season, episode level datas
    if series_exists == 0:
        series_all.append({
          "id": getHash(series_title),
          "title": series_title,
          "releaseDate": series_release_date,
          "cloudStorageId": "20075775",
          "cloudStorageType": 1,
          "posterBaseUrl": getHash(series_title) + '/' + 'poster.jpg',
          "imageBaseUrl": getHash(series_title) + '/' + 'background.jpg',
          "rating": "",
          "description": {
            "basicDescription": series_summary,
            "fieldPairs": []
          },
          "trailerUrl": "",
          "orderNo": 1,
          "seasons": [
            {
              "id": getHash(series_title + '-' + season_title),
              "title": season_title,
              "releaseDate": "0000-00-00",
              "cloudStorageId": "20075775",
              "cloudStorageType": 1,
              "posterBaseUrl": getHash(series_title) + '/' + getHash(season_title) + '/poster.jpg',
              "imageBaseUrl": getHash(series_title) + '/' + getHash(season_title) + '/background.jpg',
              "rating": "",
              "description": {
                "basicDescription": "",
                "fieldPairs": []
              },
              "trailerUrl": "",
              "seriesId": getHash(series_title),
              "orderNo": season_index,
              "episodes": [
                {
                  "id": getHash(series_title + '-' + season_title + '-' + episode_title),
                  "title": episode_title,
                  "releaseDate": "0000-00-00",
                  "cloudStorageId": "20075775",
                  "cloudStorageType": 1,
                  "posterBaseUrl": getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title) + '/poster.jpg',
                  "imageBaseUrl": getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title) + '/background.jpg',
                  "rating": "",
                  "description": {
                    "basicDescription": episode_summary,
                    "fieldPairs": []
                  },
                  "trailerUrl": "",
                  "seasonId": getHash(series_title + '-' + season_title),
                  "seriesId": getHash(series_title),
                  "orderNo": episode_index,
                  "fileProperties": {
                    "URL": getHash(series_title)+ '/' + getHash(season_title) + '/' + getHash(episode_title) + "/dash.mpd",
                    "resolution": "",
                    "videoCodec": "",
                    "audioFormat": "",
                    "audioChannelsInfo": "",
                    "runningTime": "",
                    "languagesList": [],
                    "subtitleOptionsList": []
                  }
                }
              ]
            }
          ],
          "type": 1,
          "groupId": "14501699205860001"
        })
    # write back to the file
    jsonFile = open("output.json", "wb")
    jsonFile.write(json.dumps(data))
    jsonFile.close()

## 6. Delete files from ffmpeg output and move files from mp4box output to <finalOutputDirectory>.
def deleteFiles(title, finalOutputDirectory, drive):
    """Function to delete ffmpeg output amd move files"""
    file_dict = {}
    
    if drive == 'local':
        ## move the contents to the final output directory. overwrite if possible
        if not os.path.exists(finalOutputDirectory + '/' + getHash(title)+ "/"):
            try:
                shutil.move(getHash(title)+ "/", finalOutputDirectory + '/' + getHash(title)+ "/")
            except:
                pass
        else:
            try:
                shutil.move(getHash(title)+ "/", finalOutputDirectory + '/')
            except:
                pass
        try:
            shutil.move(getHash(series_title) + '/' + getHash(season_title) + '/', finalOutputDirectory + '/' + getHash(series_title) + '/' + getHash(season_title) + '/')
        except:
            pass
        try:
            shutil.move(getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title) + '/', finalOutputDirectory + '/' +getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title) + '/')
        except:
            pass
    elif drive == 'google':
        # static variables
        MAIN_FOLDER = getHash(title)+ "/" # main root folder
        if GOOGLE_DRIVE_ROOT_DIR == '':
            MAIN_FOLDER_PARENT_ID = None #id of the parent folder for root folder
        else:
            MAIN_FOLDER_PARENT_ID = GOOGLE_DRIVE_ROOT_DIR
        folder_id = {}     

        # create the root folder and store the id
        id = createRemoteFolder(MAIN_FOLDER, MAIN_FOLDER_PARENT_ID)
        folder_id[MAIN_FOLDER] = id

        curFolder = os.path.abspath(MAIN_FOLDER)
        # recursive function
        for dirname, dirnames, filenames in os.walk(MAIN_FOLDER):
            for subdirname in dirnames:
                print ("FOUND DIRECTORY: ", os.path.join(dirname, subdirname))
                print (dirname, subdirname)
                parentId = folder_id.get(dirname.split('\\')[-1], None)
                id = createRemoteFolder(subdirname, parentId)
                folder_id[subdirname] = id
            for filename in filenames:
                print ("FOUND FILE: ", os.path.join(dirname, filename))
                parentId = folder_id.get(dirname.split('\\')[-1], None)
                file_id = uploadFiles(os.path.join(dirname, filename), None, parentId)
                file_dict[dirname.split('\\')[-1] + '_' + filename] = file_id
        os.remove(MAIN_FOLDER)
        
    os.remove('video1080hevc.mp4')
    os.remove('video720hevc.mp4')
    os.remove('video480hevc.mp4')
    os.remove('video720.mp4')
    os.remove('video480.mp4')
    os.remove('audio0.mp4')
    os.remove('audio1.mp4')
    os.remove('audio2.mp4')

    return file_dict

## 7. Get the encryption key if exists
def getEncryptionKey():
    """Function to get the encryption key form the json file"""
    jsonFile = open("output.json")
    data = json.load(jsonFile)
    jsonFile.close()
    try:
        return data['mediaEncryptionKey']
    except:
        return False

## 8. Update main json database file after uploading to GoogleDrive
def updateJsonFilePostGD(series_title, season_title, episode_title, file_dict):
    """Function to update the json file"""
    jsonFile = open("output.json")
    global data
    data = json.load(jsonFile)
    jsonFile.close()

    ## check if series exists
    series_exists = 0
    series_all = data['groups'][0]['items']
    for series in series_all:
        if series['id'] == getHash(series_title):
            series_exists += 1
            ix_series = series_all.index(series)
            series['posterBaseUrl'] = file_dict[getHash(series_title)+'_poster.jpg']
            series['imageBaseUrl'] = file_dict[getHash(series_title)+'_thumb.jpg']
            # series exists
            ## check if season exists
            season_exists = 0
            seasons_all = data['groups'][0]['items'][ix_series]['seasons']
            for season_ in seasons_all:
                if getHash(series_title + '-' + season_title) == season_['id']:
                    season_exists +=1
                    season_['posterBaseUrl'] = file_dict[getHash(series_title + '-' + season_title)+'_poster.jpg']
                    season_['imageBaseUrl'] = file_dict[getHash(series_title + '-' + season_title)+'_thumb.jpg']
                    ix_season = seasons_all.index(season_)
                    
                    ## season exists
                    ## check if episode exists
                    episodes_all = data['groups'][0]['items'][ix_series]['seasons'][ix_season]['episodes']
                    episode_exists = 0
                    for episode in episodes_all:
                        if getHash(series_title + '-' + season_title + '-' + episode_title) == episode['id']:
                            episode_exists += 1
                            # episode exists. change the values of this episode to new values
                            ix = episodes_all.index(episode)
                            episodes_all[ix]["posterBaseUrl"] = file_dict[getHash(series_title + '-' + season_title + '-' + episode_title)+'_poster.jpg']
                            episodes_all[ix]["imageBaseUrl"] = file_dict[getHash(series_title + '-' + season_title + '-' + episode_title)+'_thumb.jpg']
                            episodes_all[ix]["URL"] = file_dict[getHash(series_title + '-' + season_title + '-' + episode_title)+'_thumb.jpg']
                             
    # write back to the file
    jsonFile = open("output.json", "wb")
    jsonFile.write(json.dumps(data))
    jsonFile.close()
    
if __name__ == "__main__":    
    elements, series_title, series_thumb, series_art, series_basicDescription, series_release_date, \
                                    season_index, season_thumb, season_title, season_id = firstAPICall(series_id)
    
    # get encryption key or set encryption key
    key = getEncryptionKey()
    if not key:
        key = os.urandom(BLOCK_SIZE)
    iv = getHash(series_title).decode('hex')
    # download images for series
    downloadImage(series_title, '', '', posterFileName, series_thumb, cipher_mode, key, iv, USE_ENCRYPTION), downloadImage(series_title, '', '', imageBaseName, series_art, cipher_mode, key, iv, USE_ENCRYPTION)     
    # dowmload images for season
    iv = getHash(series_title + '-' + season_title).decode('hex')
    downloadImage(series_title, season_title, '', posterFileName, season_thumb, cipher_mode, key, iv, USE_ENCRYPTION), downloadImage(series_title, season_title, '', imageBaseName, series_art, cipher_mode, key, iv, USE_ENCRYPTION)
    # get data from the second api call on episodes
    returnData = getData(season_index)
    # iterate and do the ffmpeg, mp4box
    for item in returnData:
        episode_title, episode_summary, episode_year, episode_thumb, episode_duration, \
                       episode_contentRating, episode_videoFrameRate, episode_file_, episode_index = item[0], item[1], item[2], item[3], item[4], \
                                                                                         item[5], item[6], item[7],item[8]
        # download images for episode
        iv = getHash(series_title + '-' + season_title + '-' + episode_title).decode('hex')
        downloadImage(series_title, season_title, episode_title, posterFileName, episode_thumb, cipher_mode, key, iv, USE_ENCRYPTION), downloadImage(series_title, season_title, episode_title, imageBaseName, episode_thumb, cipher_mode, key, iv, USE_ENCRYPTION)
    
        status, stat_dict = FFMPEGCommand(episode_file_, episode_videoFrameRate)
        #status = 0
        if status == 0:
            status1, stat_dict = MP4BoxCommand(series_title, season_title, episode_title)
            #status1 = 0
            if status1 == 0:
                updateJsonFile(series_title, series_basicDescription, series_release_date, series_art, series_thumb, \
                               episode_videoFrameRate, episode_summary, episode_year, episode_thumb, episode_duration, \
                               episode_contentRating, episode_file_, episode_index, key, season_id)
    
            else:
                print ('Error within the MP4BoxCommand Function')
        else:
            print ('Error within the FFMPEGCommand Function')

    
    # move the files after everything is done. Either to Google Drive or to local
    file_dict = deleteFiles(series_title, finalOutputDirectory, drive)
    # update json if drive was Google Drive
    if drive == 'google':
        updateJsonFilePostGD(series_title, season_title, episode_title, file_dict)
    print ('Work Done. Finishing')

