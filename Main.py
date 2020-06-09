from NPRPageParser import NPRPageParser
from NPRPlaylistCreator import NPRPlaylistCreator
fileName = "NPRPageParser.json"

pageParser = NPRPageParser() # Instance of page parser
pageParser.nprurl = "https://www.npr.org/programs/weekend-edition-sunday/2020/05/10/853414822/" # turn into create url function later
pageHTML = pageParser.RequestURL()
pageParser.StoryParser(pageHTML, fileName) # outputs the file
#pageParser.UpdateJsonDictData("NPRPageParser.json", pageData, "Nassau", "Long Arc")

jsonFromFile = NPRPageParser.GetJsonData(fileName) # loading from file itself
interludeArtists = NPRPageParser.get_artist_data(jsonFromFile)

playlistCreator = NPRPlaylistCreator()
playlistURI = playlistCreator.CreatePlaylist(jsonFromFile.get("Playlist Name"))
playlistDay = playlistCreator.addCoverArtToPlaylist(jsonFromFile.get("Day"), playlistURI)
spotifyURIs = playlistCreator.GetSpotifyURIs(interludeArtists)
# spotifyResponse = playlistCreator.add_song_to_playlist(newPlaylist, spotifyURIs)