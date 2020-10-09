import os
import time
from urllib.parse import urlparse
from NPRPageParser import NPRPageParser
from NPRSpotifySearch import NPRSpotifySearch
from NPRPlaylistCreator import NPRPlaylistCreator

# # # Create a json file for each year of day links (only need to run one time)
# NPRPageParser.NPRArticleLinkCacheCreator(2018) # 1996 - 2020

# # Load year cache data in so we can loop over every day of every month to generate article info to parse
# yearToLoad = 1998
# jsonLoadedYearCache = NPRPageParser.LoadJSONFile("NPRArticleLinkCache/" + str(yearToLoad) + "-NPRArticleLinkCache.json")
# for month, daysList in jsonLoadedYearCache.items():
#     for day in daysList:
#         time.sleep(5) # Don't hammer their server
#         print(day)
#         # Parsing an NPR page for it's interlude track data
#         NPRPageParser.nprurl = day
#         pageHTML = NPRPageParser.RequestURL()
#         NPRPageParser.GetNPRStory(pageHTML.text) # outputs gathered article data

nprArticleDataPath = "NPRArticleData"
NPRSpotifySearch = NPRSpotifySearch()
for subdir, dirs, files in os.walk(nprArticleDataPath):
    if subdir == str(nprArticleDataPath + "\\1998\\06"):
        for subdir, dirs, files in os.walk(subdir):
            #files = list(filter(lambda x: "/" + str(monthCount).zfill(2) + "/" in x, articleDayLinks))
            files = sorted(files, key=lambda x: int(x.partition("NPR ")[2].partition(" ")[2].partition(",")[0]))
            for file in files:
                print(file)
                time.sleep(5)
                # Start NPR Playlist creation by looping over every month, day, year in /NPRArticleData/
                jsonFromFile = NPRPageParser.LoadJSONFile(subdir + "\\" + file)
                interludes = NPRPageParser.GetArtistsAndTrack(jsonFromFile) # grabs just the interlude data from json files
                # Getting a playlist created to add tracks, cover art, and description (except when no interludes are found)
                if interludes.__len__() != 0:
                    nprPlaylistCreator = NPRPlaylistCreator()
                    playlistDetails = nprPlaylistCreator.CreatePlaylist(jsonFromFile[0]["Playlist Name"]) # need to solution for automation
                    # Transforming our parsed interlude data into Spotify search result data
                    searchedTracks = NPRSpotifySearch.GetTrackURIs(interludes)
                    # Updating the playlist with desciption of missing tracks (if any), adding cover art, and adding tracks
                    nprPlaylistCreator.UpdatePlaylistDescription(searchedTracks, playlistDetails["id"], jsonFromFile[0]["Page Link"])
                    nprPlaylistCreator.AddCoverArtToPlaylist(searchedTracks, jsonFromFile[0]["Day"], playlistDetails["id"])
                    nprPlaylistCreator.AddTracksToPlaylist(searchedTracks, playlistDetails["id"])
                    # Transforming the results data back into the parsed interlude data, updating, and re-saving to file
                    NPRPageParser.UpdateJSONFile(subdir + "\\" + file, playlistDetails, searchedTracks)
                else:
                    print("-- No interludes found, skipping.")

# # Start NPR Playlist creation by looping over every month, day, year in /NPRArticleData/
# testFileName = "NPRArticleData/2019/08/August 18, 2019 - Interlude(s) for NPR Weekend Edition Sunday.json"
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