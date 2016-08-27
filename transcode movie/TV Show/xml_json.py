import xml.etree.ElementTree as ET
import json, argparse, requests, sys, shutil, os, hashlib, time

## static variables
finalOutputDirectory = ''
remotePath = '/media/'
localPath = 'z:\media\\'
windows = 1 

## parsing data from the command line
arparser = argparse.ArgumentParser()
arparser.add_argument("-id", "--ids", help="movie ids. Eg - '1,2,3'")
args = arparser.parse_args()
ids = [i.strip() for i in args.ids.split(',')]

## check whether ids have been passed. Else exit
if len(ids)==0:
    print 'No Movie Ids provided. Nothing to do. Exiting!'
    sys.exit(1)

def plexURL():
    """Function to add the base url"""
    return 'https://localhost:32400/'

def getHash(movieName):
    """Function to hash the movie name"""
    return hashlib.md5(movieName).hexdigest()

## 1. Check response for type==movie. If yes, retrieve required elements
def checkIfMovie(id):
    """ function to check if the type==movie for a given id
    id - id passed via the command line
    """
    response = requests.get(plexURL() + 'library/metadata/' + str(id))
    e = ET.parse(response.text).getroot()
    elements = e.getiterator()
    return elements[1].get('type') == 'movie', elements
    
def getData(id, elements):
    """Function to retrieve the required elements from the xml response
    id - id passed via command line
    element - parsed xml element
    """
    title =  elements[1].get('title')
    summary =  elements[1].get('summary')
    year = elements[1].get('year')
    art = plexURL() + elements[1].get('art')
    thumb = plexURL() + elements[1].get('thumb')
    duration = elements[1].get('duration')
    contentRating = elements[1].get('contentRating')
    videoFrameRate =  elements[2].get('videoFrameRate')
    if windows==1:
        file_ = elements[3].get('file').replace(remotePath, localPath).replace('/', '\\')
    else:
        file_ = elements[3].get('file')
    return title, summary, year, art, thumb, duration, contentRating, videoFrameRate, file_

## 2. Download art and thumb images and save to same directory as where
##    mp4box will output to
def downloadImage(title, url):
    """Function to download the images - art & thumb
    url - url of the image on the server
    """
    response = requests.get(url, stream=True)
    with open(getHash(title)+ "/"+ url.split('/')[-1] +'.jpg', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

## 3. FFMPEG command:
def FFMPEGCommand(file_, videoFrameRate):
    """Function to execute the ffmpeg command
    file_ - parsed from the xml response. Eg."/media/Movies/Polar Express, The (2004)/The Polar Express- Blu-ray 1080p.mkv"
    videoFrameRate - parse from xml response
    """
    command = "ffmpeg -y -i " + file_ + " \
-c:a libfdk_aac -ac 2 -ab 192k audio.mp4 \
-c:v libx265 -x265opts 'keyint=" + videoFrameRate + ":min-keyint=" +videoFrameRate + ":no-scenecut' -profile:v \
main -level 4.1 -b:v 8000k -maxrate 8000k -bufsize 8000k -vf \"scale=-1:1080\" video1080.mp4 \
-c:v libx264 -x264opts 'keyint=" + videoFrameRate + ":min-keyint=" + videoFrameRate + ":no-scenecut' -profile:v baseline -level\
3.0 -b:v 4000k -maxrate 4000k -bufsize 4000k -vf \"scale=-1:720\" video720.mp4 \
-c:v libx264 -x264opts 'keyint=" + videoFrameRate + ":min-keyint=" + videoFrameRate + ":no-scenecut' -profile:v baseline -level \
3.0 -b:v 1500k -maxrate 1500k -bufsize 1500k -vf \"scale=-1:480\" video480.mp4"

    status = os.system(command)
    return status, command

## 4. MP4Box command
def MP4BoxCommand(title):
    """Function to run the MP4Box executable"""
    command =  "MP4Box -dash 4000 -rap -frag-rap -profile onDemand -out " + getHash(title)+ "/dash.mpd video1080.mp4 video720.mp4 video480.mp4 audio.mp4"
    status = os.system(command)
    return status

## 5. Update main json database file adding this item
def updateJsonFile(title, summary, year, art, thumb, duration, contentRating, videoFrameRate, file_):
    """Function to update the json file"""
    jsonFile = open("examplejson.txt")
    data = json.load(jsonFile)
    jsonFile.close()
    data['updateDate'] = int(time.time())
    data['groups'][0]['items'].append({    "id": 23415714,
                                          "orderNo": 0,
                                          "title": title,
                                          "releaseDate": year,
                                          "cloudStorageId": 1,
                                          "posterBaseUrl": thumb,
                                          "imageBaseUrl": art,
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

    jsonFile = open("examplejson.txt", "wb")
    jsonFile.write(json.dumps(data))
    jsonFile.close()

## 6. Delete files from ffmpeg output and move files from mp4box output to <finalOutputDirectory>.
def deleteMoveFiles(title, finalOutputDirectory):
    """Function to delete ffmpeg output amd move files"""
    shutil.move(getHash(title)+ "/", finalOutputDirectory)
    os.remove('video1080.mp4')
    os.remove('video720.mp4')
    os.remove('video480.mp4')
    os.remove('audio.mp4')

if __name__ == "__main__":
    ## iterate through the ids and do as required
    for id in ids:
        status, elements = checkIfMovie(id)
        if status:            
            title, summary, year, art, thumb, duration, contentRating, videoFrameRate, file_ = getData(id, elements)
            downloadImage(title, art), downloadImage(title, thumb)
            status = FFMPEGCommand(file_, videoFrameRate)
            if status == 0:
                status1 = MP4BoxCommand(title)
                if status1 == 0:
                    updateJsonFile(title, summary, year, art, thumb, duration, contentRating, videoFrameRate, file_)
                    deleteMoveFiles()
                else:
                    print 'Error within the MP4BoxCommand Function'
            else:
                print 'Error within the FFMPEGCommand Function'
        else:
            print 'type is not movie for id = ', id
    print 'Work Done. Finishing'
