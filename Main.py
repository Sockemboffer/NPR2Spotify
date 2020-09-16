from NPRPageParser import NPRPageParser
from NPRSpotifySearch import NPRSpotifySearch
from NPRPlaylistCreator import NPRPlaylistCreator
from urllib.parse import urlparse

# todo: Organize into folders in some way
# todo: create json file name as playlist name?

# urlParse = urlparse("https://www.npr.org/programs/weekend-edition-sunday/2020/05/10/853414822/")
# print(urlParse)

#NPRPageParser.NPRArticleLinkCacheCreator(2019)
# Parsing an NPR page for it's interlude track data
NPRPageParser.nprurl = "https://www.npr.org/programs/morning-edition/1996/01/29/12942543/?showDate=1996-01-29" # turn into create url function later
pageHTML = NPRPageParser.RequestURL()
NPRPageParser.GetNPRStory(pageHTML.text) # outputs the file

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