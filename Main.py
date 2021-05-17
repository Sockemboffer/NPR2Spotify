import os
import time
import json
from urllib.parse import urlparse
from NPRPageParser import NPRPageParser
from NPRSpotifySearch import NPRSpotifySearch
from NPRPlaylistCreator import NPRPlaylistCreator

# # # Create a json file for each year of day links (only need to run one time)
# NPRPageParser.NPRArticleLinkCacheCreator(2018) # 1996 - 2020

# July 28th 2000's seems to be when some interlude data is being documented
# Used to create complete years
editionYear = 1999
editionDayData = list()
editionYearLinkCache = NPRPageParser.LoadJSONFile("MoWeEd Article Link Cache/" + str(editionYear) + " MoWeEd Article Link Cache.json")
for month, daylinks in editionYearLinkCache.items():
    for url in daylinks:
        nprSpotifySearch = NPRSpotifySearch()
        nprPlaylistCreator = NPRPlaylistCreator()
        nprPageParser = NPRPageParser()
        requestedHTML = NPRPageParser.RequestURL(url)
        selectedHTML = NPRPageParser.SelectStory(requestedHTML.text) # select the returned HTML
        editionDayData.append(NPRPageParser.GetEditionData(url, selectedHTML)) # get various article data from this day
        for story in selectedHTML.xpath('.//div[@id="story-list"]/*'):
            if story.attrib['class'] == 'rundown-segment':
                editionDayData.append(NPRPageParser.GetArticleInfo(story))
            elif story.attrib['class'] == 'music-interlude responsive-rundown':
                for songMETA in story.xpath('.//div[@class="song-meta-wrap"]'):
                    interlude = dict()
                    interlude["MoWeEd Track"] = NPRPageParser.GetInterludeSongName(songMETA)
                    interlude["MoWeEd Artists"] = NPRPageParser.GetInterludeArtistNames(songMETA)
                    editionDayData.append(interlude)
                    print(json.dumps(interlude, indent=4, sort_keys=True, ensure_ascii=False))
        nprPageParser.SaveJSONFile(editionDayData)
        print("Finished {0}\n".format(editionDayData[0]['Page Link']))
        editionDayData.clear()
        time.sleep(1) # Don't hammer their server

# # Read in Article Data and create a playlist out of it
#   if (dayDetails['Day'] == 'Saturday') or (dayDetails['Day'] == 'Sunday'):
#       dayDetails['Playlist Name'] = "MoWeEd " + dayDetails['Date Text'] + " - " + dayDetails['Day'] + " " + dayDetails['Edition'] + " Interludes"
#   else:
#       dayDetails['Playlist Name'] = "MoWeEd " + dayDetails['Date Text'] + " - " + dayDetails['Day'] + " " + dayDetails['Edition'] + " Interludes"
#   nprPlaylistCreator.AddCoverArtToPlaylist(editionDayData)
#   nprPlaylistCreator.AddTracksToPlaylist(editionDayData)
#   nprPlaylistCreator.UpdatePlaylistDescription(editionDayData)

# # For testing single days
# def SpotCheckSinglePage(url):
#     editionDayData = list()
#     nprSpotifySearch = NPRSpotifySearch()
#     nprPlaylistCreator = NPRPlaylistCreator()
#     nprPageParser = NPRPageParser()
#     requestedHTML = NPRPageParser.RequestURL(url)
#     selectedHTML = NPRPageParser.SelectStory(requestedHTML.text) # select the returned HTML
#     editionDayData.append(NPRPageParser.GetEditionData(url, selectedHTML)) # get various article data from this day
#     trackResults = list()
#     for item in selectedHTML.xpath('.//div[@id="story-list"]/*'):
#         if item.attrib['class'] == 'rundown-segment':
#             editionDayData.append(NPRPageParser.GetArticleInfo(item))
#         elif item.attrib['class'] == 'music-interlude responsive-rundown':
#             for track in item.xpath('.//div[@class="song-meta-wrap"]'):
#                 trackname = NPRPageParser.GetInterludeSongName(track)
#                 artistNames = NPRPageParser.GetInterludeArtistNames(track)
#                 editionDayData.append(nprSpotifySearch.SearchSpotify(trackname, artistNames))
#     nprPlaylistCreator.AddCoverArtToPlaylist(editionDayData)
#     nprPlaylistCreator.AddTracksToPlaylist(editionDayData)
#     nprPlaylistCreator.UpdatePlaylistDescription(editionDayData)
#     nprPageParser.SaveJSONFile(editionDayData)
#     print("Finished {0}.\n".format(editionDayData[0]["Date Text"]))
#     editionDayData.clear()
#     # time.sleep(5) # Don't hammer their server
#     # print(json.dumps(editionDayData, indent=4, sort_keys=True, ensure_ascii=False))

# spotURL = "https://www.npr.org/programs/morning-edition/2015/12/01/457973985?showDate=2015-12-01"
# SpotCheckSinglePage(spotURL)

