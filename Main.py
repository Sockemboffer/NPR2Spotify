from NPRPageParser import NPRPageParser
from NPRPlaylistCreator import NPRPlaylistCreator
fileName = "NPRPageParser"

pageParser = NPRPageParser() # Instance of page parser
pageParser.nprurl = "https://www.npr.org/programs/weekend-edition-sunday/2020/05/10/853414822/" # turn into create url function later
pageHTML = pageParser.RequestURL()
pageData = pageParser.StoryParser(pageHTML)
#pageParser.UpdateJsonDictData("NPRPageParser.json", pageData, "Nassau", "Long Arc")

newJsonData = NPRPageParser.GetJsonData(fileName)
playlistCreator = NPRPlaylistCreator()
newPlaylist = playlistCreator.create_playlist(pageData.get("Playlist Name"))
interludeList = playlistCreator.get_artist_data(newJsonData)
# spotifyURIs = playlistCreator.get_spotify_uri(interludeList)
# spotifyResponse = playlistCreator.add_song_to_playlist(newPlaylist, spotifyURIs)