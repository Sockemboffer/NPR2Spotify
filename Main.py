from NPRPageParser import NPRPageParser
from NPRPlaylistCreator import NPRPlaylistCreator
from NPRSpotifySearch import NPRSpotifySearch
fileName = "NPRPageParser.json"

NPRPageParser = NPRPageParser() # Instance of page parser
NPRPageParser.nprurl = "https://www.npr.org/programs/weekend-edition-sunday/2020/05/10/853414822/" # turn into create url function later
pageHTML = NPRPageParser.RequestURL()
NPRPageParser.StoryParser(pageHTML, fileName) # outputs the file
jsonFromFile = NPRPageParser.GetJsonData(fileName) # loading from file itself
interludes = NPRPageParser.GetInterludes(jsonFromFile)

playlistCreator = NPRPlaylistCreator()
playlistDetails = playlistCreator.CreatePlaylist(jsonFromFile[0]["Playlist Name"]) # need to fix for automation

NPRSpotifySearch = NPRSpotifySearch()
searchedTracks = NPRSpotifySearch.GetTrackURIs(interludes)
#print(searchedTracks)
# How/what should I do with the responses with rechecking in the future
playlistCreator.UpdatePlaylistDescription(searchedTracks, playlistDetails["id"], NPRPageParser.nprurl) #'''trying to reduce missed list'''
playlistCreator.AddCoverArtToPlaylist(searchedTracks, jsonFromFile[0]["Day"], playlistDetails["id"])
playlistCreator.AddTracksToPlaylist(searchedTracks, playlistDetails["id"])

# Update json file with playlist details and track statuses
NPRPageParser.UpdateInterludeStatuses(fileName, playlistDetails, searchedTracks)