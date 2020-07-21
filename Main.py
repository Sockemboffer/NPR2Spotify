from NPRPageParser import NPRPageParser
from NPRSpotifySearch import NPRSpotifySearch
from NPRPlaylistCreator import NPRPlaylistCreator
fileName = "NPRPageParser.json"

# Parsing an NPR page for it's interlude track data
NPRPageParser = NPRPageParser()
NPRPageParser.nprurl = "https://www.npr.org/programs/weekend-edition-sunday/2020/05/10/853414822/" # turn into create url function later
pageHTML = NPRPageParser.RequestURL()
NPRPageParser.GetNPRStory(pageHTML, fileName) # outputs the file
jsonFromFile = NPRPageParser.LoadJSONFile(fileName) # loading from file itself
interludes = NPRPageParser.GetArtistsAndTrack(jsonFromFile) # grabs just the interlude data from json file

# Getting a playlist created to add tracks, cover art, and description for
playlistCreator = NPRPlaylistCreator()
playlistDetails = playlistCreator.CreatePlaylist(jsonFromFile[0]["Playlist Name"]) # need to solution for automation

# Transforming our parsed interlude file data into search result data
NPRSpotifySearch = NPRSpotifySearch()
searchedTracks = NPRSpotifySearch.GetTrackURIs(interludes)

# Updating the playlist with desciption of missing tracks (if any), cover art, and tracks
playlistCreator.UpdatePlaylistDescription(searchedTracks, playlistDetails["id"], NPRPageParser.nprurl)
playlistCreator.AddCoverArtToPlaylist(searchedTracks, jsonFromFile[0]["Day"], playlistDetails["id"])
playlistCreator.AddTracksToPlaylist(searchedTracks, playlistDetails["id"])

# Transforming the results data back into the parsed interlude data, updating, and re-saving to file
NPRPageParser.UpdateJSONFile(fileName, playlistDetails, searchedTracks)