import xml.etree.ElementTree as ET
import json, argparse, requests, sys, shutil, os, hashlib, time

## static variables
finalOutputDirectory = 'e:\finished'
remotePath = '/media/'
localPath = 'z:\\'
windows = 1
posterFileName = 'poster'
imageBaseName = 'background'

## parsing data from the command line
arparser = argparse.ArgumentParser()
arparser.add_argument("-i", "--seriesid", help="tv show ids. Eg - '1,2,3'")
arparser.add_argument("-s", "--seasonid", help="tv season. Eg - '1,2,3'")
arparser.add_argument("-e", "--episodeid", help="tv show's season's episode. Eg - '1,2,3'")
args = arparser.parse_args()
##series_id = [i.strip() for i in args.seriesid.split()]
##season_id = [i.strip() for i in args.seasonid.split()]
##episode_id = [i.strip() for i in args.episodeid.split()]
season_id = ['1']
#### check whether ids have been passed. Else exit
##if not id or not season or not episode:
##    print ('No TV Show Ids or Season or Episode provided. Nothing to do. Exiting!')
##    sys.exit(1)

def plexURL():
    """Function to add the base url"""
    return 'http://192.168.1.2:32400/'

def getHash(name):
    """Function to hash the movie name"""
    return hashlib.md5(name).hexdigest()
    
## 1. Check response for type==movie. If yes, retrieve required elements
def firstAPICall(id):
    """ function to check if the type==movie for a given id
    id - id passed via the command line
    """
    ##    response = requests.get(plexURL() + 'library/metadata/' + str(id)+ '/children')
    ##    e = ET.fromstring(response.text.encode('ascii', 'ignore'))
    e = ET.parse(open('XML_First_Call_-_TV_Show_-_Main.txt'))
    elements = e.getiterator()

    for elem in elements:
        if elem.tag == 'Directory':
            series_season_id = elem.get('index')
            series_title = elements[0].get('parentTitle')
            series_thumb = elements[0].get('parentTitle')
            series_art = elements[0].get('art')
            season_rating_key = elem.get('ratingKey')
            season_title = elem.get('title')
            series_basicDescription = elements[0].get('summary')
            if season_id in season:                
                return elements, season_rating_key, series_title, series_thumb, series_art, series_basicDescription

elements, season_rating_key, series_title, series_thumb, series_art, series_basicDescription = firstAPICall(3)

def getData(id):
    """Function to retrieve the required elements from the xml response
    id - id passed via command line
    element - parsed xml element
    """
##    response = requests.get(plexURL() + 'library/metadata/' + str(id)+ '/children')
##    e = ET.fromstring(response.text.encode('ascii', 'ignore'))
    e = ET.parse(open('XML_Second_Call_-_TV_Show_-_Season.txt'))
    elements = e.getiterator()

    returnData = []   
    for elem in elements:
        if elem.tag == 'Video':
            episode_key = elem.get('ratingKey')
            if (episode_key in episode) or (episode == 'all'):
                title =  elem.get('title')
                summary =  elem.get('summary')
                year = elem.get('year')
                thumb = plexURL() + elem.get('thumb')[1:]
                duration = elem.get('duration')
                contentRating = elements[0].get('grandparentContentRating')
                videoFrameRate =  elements[elements.index(elem) + 1].get('videoFrameRate')
                if windows==1:
                    file_ = elements[elements.index(elem) + 1].get('file').replace(remotePath, localPath).replace('/', '\\')
                else:
                    file_ = elements[elements.index(elem) + 1].get('file')
                returnData.extend([title, summary, year, thumb, duration, contentRating, videoFrameRate, file_])

    return returnData

## 2. Download art and thumb images and save to same directory as where
##    mp4box will output to
def downloadImage(title, name, url):
    """Function to download the images - art & thumb
    url - url of the image on the server
    """
    # create the directory if it doesn't exists
    if not os.path.exists(getHash(title)):
        os.makedirs(getHash(title))
        
    response = requests.get(url, stream=True)    
    with open(getHash(title)+ "/"+ name +'.jpg', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

## 3. FFMPEG command:
def FFMPEGCommand(file_, videoFrameRate):
    """Function to execute the ffmpeg command
    file_ - parsed from the xml response. Eg."/media/Movies/Polar Express, The (2004)/The Polar Express- Blu-ray 1080p.mkv"
    videoFrameRate - parse from xml response
    """
    command = 'ffmpeg -y -i "'+file_+'" -map 0:1 -c:a aac -ac 2 -ab 320k audio.mp4 -map 0:0 -c:v libx264 -x264opts keyint=' + \
              videoFrameRate[:-1] + ':min-keyint=' + videoFrameRate[:-1] + ':no-scenecut -profile:v baseline -level 4.1 -maxrate 8000k -bufsize 8000k video1080.mp4 -map 0:0 -c:v libx264 -x264opts keyint=' + \
              videoFrameRate[:-1] + ':min-keyint=' + videoFrameRate[:-1] + ':no-scenecut -profile:v baseline -level 4.1 -maxrate 4000k -bufsize 4000k -vf "scale=trunc(oh*a/2)*2:720" video720.mp4 -map 0:0 -c:v libx264 -x264opts keyint=' + videoFrameRate[:-1] + ':min-keyint=' + videoFrameRate[:-1] + ':no-scenecut -profile:v baseline -level 4.1 -maxrate 1500k -bufsize 1500k -vf "scale=trunc(oh*a/2)*2:480" video480.mp4'
    status = os.system(command)
    return status, command

## 4. MP4Box command
def MP4BoxCommand(series_title, season_id, episode_id):
    """Function to run the MP4Box executable"""
    command =  "MP4Box -dash 4000 -rap -frag-rap -profile onDemand -out " + \
              getHash(series_title +'-' + season_id + '-' + episode_id)+ "/dash.mpd video1080.mp4 video720.mp4 video480.mp4 audio.mp4"
    status = os.system(command)
    return status

## 5. Update main json database file adding this item
def updateJsonFile(title, summary, year, art, thumb, duration, contentRating, videoFrameRate, file_):
    """Function to update the json file"""
    jsonFile = open("output.json")
    data = json.load(jsonFile)
    jsonFile.close()
    data['updateDate'] = int(time.time()*1000)

    ## check if series exists
    series_exists = 0
    series_all = data['groups'][0]['items']
    for series in series_all:
        if series['id'] == getHash(series_title):
            series_exists += 1
            ## check if season exists
            season_exists = 0
            seasons_all = data['groups'][0]['items'][0]['seasons']
            for season_ in seasons_all:
                if getHash(series_title + '-' + season) == season_['id']:
                    season_exists +=1
                    ## check if episode exists
                    episodes = data['groups'][0]['items'][0]['seasons'][0]['episodes']
                    episode_exists = 0
                    for episode in episodes:
                        if getHash(series_title + '-' + season + '-' + episode_id) == episode['id']:
                            episode_exists += 1
                            ix = episodes.index(episode)
                            episodes[ix] = {
                                          "id": getHash(series_title + '-' + season_id + '-' + episode_id),
                                          "title": episode_title,
                                          "releaseDate": "0000-00-00",
                                          "cloudStorageId": 1,
                                          "posterBaseUrl": getHash(series_title) + '/' + getHash(series_title + '-' + season) + '/' + getHash(series_title + season +  episode_id)+ "/poster.jpg",
                                          "imageBaseUrl": "",
                                          "rating": "",
                                          "description": {
                                            "basicDescription": episode_summary,
                                            "fieldPairs": []
                                          },
                                          "trailerUrl": "",
                                          "seasonId": getHash(series_title + '-' + season),
                                          "fileProperties": {
                                            "URL": getHash(series_title) + '/' + getHash(season) + '/' + getHash(series_title) + "/dash.mpd",
                                            "resolution": "",
                                            "videoCodec": "",
                                            "audioFormat": "",
                                            "audioChannelsInfo": "",
                                            "runningTime": "",
                                            "languagesList": [],
                                            "subtitleOptionsList": []
                                          }
                                        }

                    if episode_exists == 0:
                         episodes.append({
                                      "id": getHash(series_title + '-' + season_id + '-' + episode_id),
                                      "title": episode_title,
                                      "releaseDate": "0000-00-00",
                                      "cloudStorageId": 1,
                                      "posterBaseUrl": getHash(series_title) + '/' + getHash(series_title + '-' + season) + '/' + getHash(series_title + season +  episode_id)+ "/poster.jpg",
                                      "imageBaseUrl": "",
                                      "rating": "",
                                      "description": {
                                        "basicDescription": episode_summary,
                                        "fieldPairs": []
                                      },
                                      "trailerUrl": "",
                                      "seasonId": getHash(series_title + '-' + season),
                                      "fileProperties": {
                                        "URL": getHash(series_title) + '/' + getHash(season) + '/' + getHash(series_title) + "/dash.mpd",
                                        "resolution": "",
                                        "videoCodec": "",
                                        "audioFormat": "",
                                        "audioChannelsInfo": "",
                                        "runningTime": "",
                                        "languagesList": [],
                                        "subtitleOptionsList": []
                                      }
                                    })
            if season_exists == 0:
                        seasons.append({
                                      "id": "<hash: series title + season number>",
                                      "title": "<FIRST CALL: title after looking up index=>",
                                      "releaseDate": "0000-00-00",
                                      "cloudStorageId": 1,
                                      "posterBaseUrl": "<SECOND CALL: thumb>",
                                      "imageBaseUrl": "<SECOND CALL: art>",
                                      "rating": "",
                                      "description": {
                                        "basicDescription": "",
                                        "fieldPairs": []
                                      },
                                      "trailerUrl": "",
                                      "seriesId": "<hash of series title>",
                                      "episodes": [
                                        {
                                          "id": "<hash: series title + season number + episode number>",
                                          "title": "<SECOND CALL: video - title>",
                                          "releaseDate": "0000-00-00",
                                          "cloudStorageId": 1,
                                          "posterBaseUrl": "",
                                          "imageBaseUrl": "",
                                          "rating": "",
                                          "description": {
                                            "basicDescription": "<SECOND CALL: video - summary>",
                                            "fieldPairs": []
                                          },
                                          "trailerUrl": "",
                                          "seasonId": "<hash: series title + season number>",
                                          "fileProperties": {
                                            "URL": "<output url like in movies>",
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
                             

    
    episodes = data['groups'][0]['items'][0]['seasons'][0]['episodes']
    episode_exists = 0
    
                                                                           
    data['groups'][0]['items'].append({    "id": 23415714,
                                          "orderNo": 0,
                                          "title": title,
                                          "releaseDate": year,
                                          "cloudStorageId": 1,
                                          "posterBaseUrl": getHash(title)+ "/poster.jpg",
                                          "imageBaseUrl": getHash(title)+ "/background.jpg" ,
                                          "rating": contentRating,
                                          "description": {
                                            "basicDescription": summary,
                                            "fieldPairs": []
                                          },
                                          "trailerUrl": "",
                                          "fileProperties": {
                                            "URL": getHash(title)+ "/dash.mpd",
                                            "resolution": "",
                                            "videoCodec": "H.264",
                                            "audioFormat": "",
                                            "audioChannelsInfo": "",
                                            "runningTime": "46",
                                            "languagesList": [],
                                            "subtitleOptionsList": []
                                          },
                                          "type": 0,
                                          "groupId": 318762252
                                        })
    if series_exists == 0:
        series_all.append({
          "id": "<hash of series title>",
          "title": "<FIRST CALL: parentTitle>",
          "releaseDate": "<FIRST CALL: parentYear>",
          "cloudStorageId": 1,
          "posterBaseUrl": "<FIRST CALL: thumb>",
          "imageBaseUrl": "<FIRST CALL: art>",
          "rating": "",
          "description": {
            "basicDescription": "<FIRST CALL: summary>",
            "fieldPairs": []
          },
          "trailerUrl": "",
          "seasons": [
            {
              "id": "<hash: series title + season number>",
              "title": "<FIRST CALL: title after looking up index=>",
              "releaseDate": "0000-00-00",
              "cloudStorageId": 1,
              "posterBaseUrl": "<SECOND CALL: thumb>",
              "imageBaseUrl": "<SECOND CALL: art>",
              "rating": "",
              "description": {
                "basicDescription": "",
                "fieldPairs": []
              },
              "trailerUrl": "",
              "seriesId": "<hash of series title>",
              "episodes": [
                {
                  "id": "<hash: series title + season number + episode number>",
                  "title": "<SECOND CALL: video - title>",
                  "releaseDate": "0000-00-00",
                  "cloudStorageId": 1,
                  "posterBaseUrl": "",
                  "imageBaseUrl": "",
                  "rating": "",
                  "description": {
                    "basicDescription": "<SECOND CALL: video - summary>",
                    "fieldPairs": []
                  },
                  "trailerUrl": "",
                  "seasonId": "<hash: series title + season number>",
                  "fileProperties": {
                    "URL": "<output url like in movies>",
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
    jsonFile = open("output.json", "wb")
    jsonFile.write(json.dumps(data))
    jsonFile.close()

## 6. Delete files from ffmpeg output and move files from mp4box output to <finalOutputDirectory>.
def deleteFiles(title, finalOutputDirectory):
    """Function to delete ffmpeg output amd move files"""
    shutil.move(getHash(title)+ "/", finalOutputDirectory)
    os.remove('video1080.mp4')
    os.remove('video720.mp4')
    os.remove('video480.mp4')
    os.remove('audio.mp4')

if __name__ == "__main__":    
    elements, season_rating_key, series_title, series_thumb, series_art, series_basicDescription = firstAPICall(id)
    downloadImage(series_title, imageBaseName, series_thumb), downloadImage(series_title, imageBaseName, series_art)
    returnData = getData(season_rating_key)
    for item in returnData:
        episode_title, episode_summary, episode_year, episode_thumb, episode_duration, \
                       episode_contentRating, episode_videoFrameRate, episode_file_ = item[0], item[2], item[3], item[4], \
                                                                                           item[5], item[6], item[7]
        downloadImage(title + '-' + season_id + '-' + episode_id, imageBaseName, thumb)
        status = FFMPEGCommand(episode_file_, episode_videoFrameRate)
        if status == 0:
            status1 = MP4BoxCommand(season_title, season_id, episode_id)
            if status1 == 0:
                updateJsonFile(series_title, series_summary, series_year, series_art, series_thumb, series_duration, series_contentRating, \
                               episode_videoFrameRate, episode_summary, episode_year, episode_thumb, episode_duration, \
                               episode_contentRating, episode_file_)
                deleteFiles()
            else:
                print ('Error within the MP4BoxCommand Function')
        else:
            print ('Error within the FFMPEGCommand Function')
    
    print ('Work Done. Finishing')
