from NPRPageParser import NPRPageParser
from NPRSpotifySearch import NPRSpotifySearch
from NPRPlaylistCreator import NPRPlaylistCreator
from urllib.parse import urlparse
fileName = "NPRPageParser.json"

# todo: Organize into folders in some way
# todo: create json file name as playlist name?

# datesToSort = [
# "https://www.npr.org/programs/morning-edition/2018/7/31/662433741?showDate=2018-10-31",
# "https://www.npr.org/programs/morning-edition/2018/7/1/661993253/morning-edition-for-october-30-2018?showDate=2018-10-30",
# "https://www.npr.org/programs/morning-edition/2018/7/29/661661069/morning-edition-for-october-29-2018?showDate=2018-10-29",
# "https://www.npr.org/programs/morning-edition/2018/7/26/660850176/morning-edition-for-october-26-2018?showDate=2018-10-26",
# "https://www.npr.org/programs/morning-edition/2018/7/7/660436473/morning-edition-for-october-25-2018?showDate=2018-10-25",
# "https://www.npr.org/programs/morning-edition/2018/7/24/660112704/morning-edition-for-october-24-2018?showDate=2018-10-24",
# "https://www.npr.org/programs/morning-edition/2018/7/2/659744952/morning-edition-for-october-23-2018?showDate=2018-10-23",
# "https://www.npr.org/programs/morning-edition/2018/7/10/659400612/morning-edition-for-october-22-2018?showDate=2018-10-22",
# "https://www.npr.org/programs/morning-edition/2018/7/19/658721177?showDate=2018-10-19",
# "https://www.npr.org/programs/morning-edition/2018/7/4/658364589/morning-edition-for-october-18-2018?showDate=2018-10-18"]
# result = sorted(datesToSort, key=lambda x: int(x.partition("/7/")[2].partition("/")[0]))
# print(result)

# urlParse = urlparse("https://www.npr.org/programs/weekend-edition-sunday/2020/05/10/853414822/")
# print(urlParse)


# Parsing an NPR page for it's interlude track data
#NPRPageParser.nprurl = "https://www.npr.org/programs/morning-edition/archive?date=7-1-2000" # turn into create url function later
#pageHTML = NPRPageParser.RequestURL()
NPRPageParser.NPRArchiveURLDateRange()
# NPRPageParser.GetNPRStory(NPRPageParser.nprurl, fileName) # outputs the file
# jsonFromFile = NPRPageParser.LoadJSONFile(fileName) # loading from file itself
# interludes = NPRPageParser.GetArtistsAndTrack(jsonFromFile) # grabs just the interlude data from json file

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