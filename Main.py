import time
from urllib.parse import urlparse
from NPRPageParser import NPRPageParser
from NPRSpotifySearch import NPRSpotifySearch
from NPRPlaylistCreator import NPRPlaylistCreator

# Create a json file for each year of day links (only need to run one time)
# NPRPageParser.NPRArticleLinkCacheCreator(2019) # 1996 - 2020

# Load year cache data in so we can loop over every day of every month to generate article info to parse
yearToLoad = 2000
jsonLoadedYearCache = NPRPageParser.LoadJSONFile("NPRArticleLinkCache/" + str(yearToLoad) + "-NPRArticleLinkCache.json")
for month, daysList in jsonLoadedYearCache.items():
    for day in daysList:
        time.sleep(5) # Don't hammer their server
        print(day)
        # Parsing an NPR page for it's interlude track data
        NPRPageParser.nprurl = day
        pageHTML = NPRPageParser.RequestURL()
        NPRPageParser.GetNPRStory(pageHTML.text) # outputs gathered article data

# Start NPR Playlist creation by looping over every month, day, year in /NPRArticleData/
#jsonFromFile = NPRPageParser.LoadJSONFile(fileName) # loading from file itself
#interludes = NPRPageParser.GetArtistsAndTrack(jsonFromFile) # grabs just the interlude data from json file
# Getting a playlist created to add tracks, cover art, and description for
# playlistDetails = NPRPlaylistCreator.CreatePlaylist(jsonFromFile[0]["Playlist Name"]) # need to solution for automation
# Transforming our parsed interlude file data into search result data
# NPRSpotifySearch = NPRSpotifySearch()
# searchedTracks = NPRSpotifySearch.GetTrackURIs(interludes)

# # Updating the playlist with desciption of missing tracks (if any), adding cover art, and adding tracks
# NPRPlaylistCreator.UpdatePlaylistDescription(searchedTracks, playlistDetails["id"], NPRPageParser.nprurl)
# NPRPlaylistCreator.AddCoverArtToPlaylist(searchedTracks, jsonFromFile[0]["Day"], playlistDetails["id"])
# NPRPlaylistCreator.AddTracksToPlaylist(searchedTracks, playlistDetails["id"])

# # Transforming the results data back into the parsed interlude data, updating, and re-saving to file
# NPRPageParser.UpdateJSONFile(fileName, playlistDetails, searchedTracks)