series_title
series_summary
series_release_date
series_art
series_thumb
episode_videoFrameRate
episode_summary
episode_year
episode_thumb
episode_duration
episode_contentRating, episode_file_):
"""Function to update the json file"""
jsonFile = open("output.json")
global data
data = json.load(jsonFile)
jsonFile.close()
data['updateDate'] = int(time.time()*1000)

## check if series exists
series_exists = 0
series_all = data['groups'][0]['items']
for series in series_all:
    if series['id'] == getHash(series_title):
        series_exists += 1
        # series exists
        ## check if season exists
        season_exists = 0
        seasons_all = data['groups'][0]['items'][0]['seasons']
        for season_ in seasons_all:
            if getHash(series_title + '-' + season_title) == season_['id']:
                season_exists +=1
                ## season exists
                ## check if episode exists
                episodes_all = data['groups'][0]['items'][0]['seasons'][0]['episodes']
                episode_exists = 0
                for episode in episodes_all:
                    if getHash(series_title + '-' + season_title + '-' + episode_title) == episode['id']:
                        episode_exists += 1
                        # episode exists. change the values of this episode to new values
                        ix = episodes.index(episode)
                        episodes[ix] = {
                                      "id": getHash(series_title + '-' + season_title + '-' + episode_title),
                                      "title": episode_title,
                                      "releaseDate": "0000-00-00",
                                      "cloudStorageId": 1,
                                      "posterBaseUrl": getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title)+ "/poster.jpg",
                                      "imageBaseUrl": getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title)+ "/background.jpg",
                                      "rating": "",
                                      "description": {
                                        "basicDescription": episode_summary,
                                        "fieldPairs": []
                                      },
                                      "trailerUrl": "",
                                      "seasonId": getHash(series_title + '-' + season_title),
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
                                  "cloudStorageId": 1,
                                  "posterBaseUrl": getHash(series_title) + '/' + getHash(series_title) + '/' + getHash(episode_title) + '/' + "poster.jpg",
                                  "imageBaseUrl": getHash(series_title) + '/' + getHash(series_title) + '/' + getHash(episode_title) + '/' + "background.jpg",
                                  "rating": "",
                                  "description": {
                                    "basicDescription": episode_summary,
                                    "fieldPairs": []
                                  },
                                  "trailerUrl": "",
                                  "seasonId": getHash(series_title + '-' + season_title),
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
                                  "cloudStorageId": 1,
                                  "posterBaseUrl": getHash(series_title) + '/' + getHash(season_title) + "/poster.jpg",
                                  "imageBaseUrl": getHash(series_title) + '/' + getHash(season_title) + "/background.jpg",
                                  "rating": "",
                                  "description": {
                                    "basicDescription": "",
                                    "fieldPairs": []
                                  },
                                  "trailerUrl": "",
                                  "seriesId": getHash(series_title),
                                  "episodes": [
                                    {
                                      "id":  getHash(series_title + '-' + season_title + '-' + episode_title),
                                      "title": episode_title,
                                      "releaseDate": "0000-00-00",
                                      "cloudStorageId": 1,
                                      "posterBaseUrl": "",
                                      "imageBaseUrl": "",
                                      "rating": "",
                                      "description": {
                                        "basicDescription": episode_summary,
                                        "fieldPairs": []
                                      },
                                      "trailerUrl": "",
                                      "seasonId": getHash(series_title + '-' + season_title),
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
                         

# the series does not exists. Add the series, season, episode level data

if series_exists == 0:
    series_all.append({
      "id": getHash(series_title),
      "title": series_title,
      "releaseDate": series_release_date,
      "cloudStorageId": 1,
      "posterBaseUrl": getHash(series_title) + '/' + 'poster.jpg',
      "imageBaseUrl": getHash(series_title) + '/' + 'background.jpg',
      "rating": "",
      "description": {
        "basicDescription": series_summary,
        "fieldPairs": []
      },
      "trailerUrl": "",
      "seasons": [
        {
          "id": getHash(series_title + '-' + season_title),
          "title": season_title,
          "releaseDate": "0000-00-00",
          "cloudStorageId": 1,
          "posterBaseUrl": getHash(series_title) + '/' + getHash(season_title) + 'poster.jpg',
          "imageBaseUrl": getHash(series_title) + '/' + getHash(season_title) + 'background.jpg',
          "rating": "",
          "description": {
            "basicDescription": "",
            "fieldPairs": []
          },
          "trailerUrl": "",
          "seriesId": getHash(series_title),
          "episodes": [
            {
              "id": getHash(series_title + '-' + season_title + '-' + episode_title),
              "title": episode_title,
              "releaseDate": "0000-00-00",
              "cloudStorageId": 1,
              "posterBaseUrl": getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title) + 'poster.jpg',
              "imageBaseUrl": getHash(series_title) + '/' + getHash(season_title) + '/' + getHash(episode_title) + 'background.jpg',
              "rating": "",
              "description": {
                "basicDescription": episode_summary,
                "fieldPairs": []
              },
              "trailerUrl": "",
              "seasonId": getHash(series_title + '-' + season_title),
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

