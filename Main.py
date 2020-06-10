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
playlistDay = playlistCreator.AddCoverArtToPlaylist(jsonFromFile.get("Day"), playlistURI)

NPRSpotifySearch = NPRSpotifySearch()
trackURIs = NPRSpotifySearch.GetTrackURIs(interludes)
# spotifyResponse = playlistCreator.add_song_to_playlist(newPlaylist, spotifyURIs)