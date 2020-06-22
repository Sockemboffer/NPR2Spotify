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
playlistURI = playlistCreator.CreatePlaylist(jsonFromFile.get("Playlist Name"))

NPRSpotifySearch = NPRSpotifySearch()
searchedTracks = NPRSpotifySearch.GetTrackURIs(interludes)
# How/what should I do with the responses with rechecking in the future
playlistCreator.UpdatePlaylistDescription(searchedTracks, playlistURI, NPRPageParser.nprurl)
playlistCreator.AddCoverArtToPlaylist(searchedTracks, jsonFromFile.get("Day"), playlistURI)
playlistCreator.AddTracksToPlaylist(searchedTracks, playlistURI)