import os
import time
import json
from urllib.parse import urlparse
from NPRPageParser import NPRPageParser
from NPRSpotifySearch import NPRSpotifySearch

# # # Create a json file for each year of day links (only need to run one time)
# NPRPageParser.NPRArticleLinkCacheCreator(2018) # 1996 - 2020

editionYear = 2003
editionDayData = list()
editionYearLinkCache = NPRPageParser.LoadJSONFile("NPRArticleLinkCache/" + str(editionYear) + "-NPRArticleLinkCache.json")
for month, daylinks in editionYearLinkCache.items():
    for url in daylinks:
        # if month == "12": # when I need to spot-clean a month
        # time.sleep(5) # Don't hammer their server
        # print(url)
        # Parsing an NPR page for it's interlude track data
        nprSpotifySearch = NPRSpotifySearch()
        requestedHTML = NPRPageParser.RequestURL(url)
        selectedHTML = NPRPageParser.SelectStory(requestedHTML.text) # select the returned HTML
        editionDayData.append(NPRPageParser.GetEditionData(url, selectedHTML)) # get various article data from this day
        # selector = Selector(text=pagehtml)
        trackResults = list()
        for item in selectedHTML.xpath('.//div[@id="story-list"]/*'):
            if item.attrib['class'] == 'rundown-segment':
                editionDayData.append(NPRPageParser.GetArticleInfo(item))
            elif item.attrib['class'] == 'music-interlude responsive-rundown':
                for track in item.xpath('.//div[@class="song-meta-wrap"]'):
                    trackname = NPRPageParser.GetInterludeSongName(track)
                    artistNames = NPRPageParser.GetInterludeArtistNames(track)
                    editionDayData.append(nprSpotifySearch.SearchSpotify(trackname, artistNames))
        # jsonStr = json.dumps(editionDayData)
        print(json.dumps(editionDayData, indent=4, sort_keys=True, ensure_ascii=False))
        break
    break


# playlistPath = os.path.join("NPRArticleData", pageData[0]['Date Numbered'][:4], pageData[0]['Date Numbered'][5:7], "")
# if not os.path.exists(playlistPath):
#     os.makedirs(playlistPath)
# with open(playlistPath + pageData[0]['Playlist Name'] + ".json", 'w', encoding='utf-8') as json_file:
#     json.dump(pageData, json_file, ensure_ascii=False, indent=4)

# for item in selector.xpath('.//div[@id="story-list"]/*'):
#     if item.attrib['class'] == 'rundown-segment':
#     if item.attrib['class'] == 'music-interlude responsive-rundown':

# artistData['Spotify URI'] = None
# artistData['Last Checked'] = None

# if pageItemKey == "Playlist Link":
#     pageItem["Playlist Link"] = playlistDetails["external_urls"]["spotify"]
# if pageItemKey == "Playlist URI":
#     pageItem["Playlist URI"] = playlistDetails["uri"]

# if searchedTrack["Match"] >= 0.5:
#     interlude['Spotify URI'] = searchedTrack["Found Track URI"]
#     interlude['Last Checked'] = str(datetime.datetime.now().__format__("%Y-%m-%d %H:%M:%S"))
# else:
#     interlude['Last Checked'] = str(datetime.d

# EditionObject

# }
# "Page Link": null,
# "Page Edition": null,
# "Date Text": null,
# "Date Numbered": null,
# "Date Day": null,
# }
#     } // loop
#         }
#         "Article Title": null,
#         "Article Link": null,
#         "Article Slug": null,
#         "Article Byline": null,
#         }
#         }
#         "Interlude Song": null,
#         "Interlude Artist": null,
#         "Found Responses": null,
#         "Found Tracks": null, (trackname, artistsname, uri, matchratio)
#         "Choosen URI": null,
#         "Last Checked": null,
#         }
#     }
# }
# "Playlist Name": null,
# "Playlist Link": null,
# "Playlist URI": null,
# }
# }
# "Parsed Date": null,
# }

# Serialize EditionObject

# # Load year cache data in so we can loop over every day of every month to generate article info to parse
# yearToLoad = 2003
# jsonLoadedYearCache = NPRPageParser.LoadJSONFile("NPRArticleLinkCache/" + str(yearToLoad) + "-NPRArticleLinkCache.json")
# for month, daysList in jsonLoadedYearCache.items():
#     for day in daysList:
#         if month == "01": # when I need to spot-clean a month
#             time.sleep(5) # Don't hammer their server
#             print(day)
#             # Parsing an NPR page for it's interlude track data
#             NPRPageParser.nprurl = day
#             pageHTML = NPRPageParser.RequestURL()
#             NPRPageParser.GetNPRStory(pageHTML.text) # outputs gathered article data

# nprArticleDataPath = "NPRArticleData"
# NPRSpotifySearch = NPRSpotifySearch()
# for subdir, dirs, files in os.walk(nprArticleDataPath):
#     if subdir == str(nprArticleDataPath + "\\2001\\10"):
#         for subdir, dirs, files in os.walk(subdir):
#             #files = list(filter(lambda x: "/" + str(monthCount).zfill(2) + "/" in x, articleDayLinks))
#             files = sorted(files, key=lambda x: int(x.partition("NPR ")[2].partition(" ")[2].partition(",")[0]))
#             for file in files:
#                 print(file)
#                 time.sleep(5)
#                 # Start NPR Playlist creation by looping over every month, day, year in /NPRArticleData/
#                 jsonFromFile = NPRPageParser.LoadJSONFile(subdir + "\\" + file)
#                 interludes = NPRPageParser.GetArtistsAndTrack(jsonFromFile) # grabs just the interlude data from json files
#                 # Getting a playlist created to add tracks, cover art, and description (except when no interludes are found)
#                 if interludes.__len__() != 0:
#                     nprPlaylistCreator = NPRPlaylistCreator()
#                     playlistDetails = nprPlaylistCreator.CreatePlaylist(jsonFromFile[0]["Playlist Name"]) # need to solution for automation
#                     # Transforming our parsed interlude data into Spotify search result data
#                     searchedTracks = NPRSpotifySearch.GetTrackURIs(interludes)
#                     # Updating the playlist with desciption of missing tracks (if any), adding cover art, and adding tracks
#                     nprPlaylistCreator.UpdatePlaylistDescription(searchedTracks, playlistDetails["id"], jsonFromFile[0]["Page Link"])
#                     nprPlaylistCreator.AddCoverArtToPlaylist(searchedTracks, jsonFromFile[0]["Day"], playlistDetails["id"])
#                     nprPlaylistCreator.AddTracksToPlaylist(searchedTracks, playlistDetails["id"])
#                     # Transforming the results data back into the parsed interlude data, updating, and re-saving to file
#                     NPRPageParser.UpdateJSONFile(subdir + "\\" + file, playlistDetails, searchedTracks)
#                 else:
#                     print("-- No interludes found, skipping.")

# # Start NPR Playlist creation by looping over every month, day, year in /NPRArticleData/
# testFileName = "NPRArticleData/2001/10/NPR October 1, 2001 - Interludes for Morning Edition Monday.json"
# jsonFromFile = NPRPageParser.LoadJSONFile(testFileName)
# #print(jsonFromFile)
# #print("\n")
# interludes = NPRPageParser.GetArtistsAndTrack(jsonFromFile) # grabs just the interlude data from json files
# #print(interludes)
# # Getting a playlist created to add tracks, cover art, and description (except when no interludes are found)
# if interludes.__len__() != 0:
#     nprPlaylistCreator = NPRPlaylistCreator()
#     playlistDetails = nprPlaylistCreator.CreatePlaylist(jsonFromFile[0]["Playlist Name"]) # need to solution for automation
#     # Transforming our parsed interlude data into Spotify search result data
#     NPRSpotifySearch = NPRSpotifySearch()
#     searchedTracks = NPRSpotifySearch.GetTrackURIs(interludes)
#     #print("\n")
#     #print(searchedTracks)
#     # Updating the playlist with desciption of missing tracks (if any), adding cover art, and adding tracks
#     nprPlaylistCreator.UpdatePlaylistDescription(searchedTracks, playlistDetails["id"], jsonFromFile[0]["Page Link"])
#     nprPlaylistCreator.AddCoverArtToPlaylist(searchedTracks, jsonFromFile[0]["Day"], playlistDetails["id"])
#     nprPlaylistCreator.AddTracksToPlaylist(searchedTracks, playlistDetails["id"])
#     # Transforming the results data back into the parsed interlude data, updating, and re-saving to file
#     NPRPageParser.UpdateJSONFile(testFileName, playlistDetails, searchedTracks)