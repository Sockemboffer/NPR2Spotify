from datetime import datetime
from datetime import timedelta
import enum
import os
import time
import json
from urllib.parse import urlparse
from NPRPageParser import NPRPageParser
from NPRSpotifySearch import NPRSpotifySearch
from NPRPlaylistCreator import NPRPlaylistCreator

# # # Create a json file for each year of day links (only need to run one time)
# NPRPageParser.NPRArticleLinkCacheCreator(2018) # 1996 - 2020

# # Jan 1th 2000's seems to be when some interlude data is being documented
# # Used to create complete years
# editionYear = 2000
# editionDayData = list()
# editionYearLinkCache = NPRPageParser.LoadJSONFile("MoWeEd Article Link Cache/" + str(editionYear) + " MoWeEd Article Link Cache.json")
# for month, daylinks in editionYearLinkCache.items():
#     for idx, link in enumerate(daylinks):
#         nprSpotifySearch = NPRSpotifySearch()
#         nprPlaylistCreator = NPRPlaylistCreator()
#         nprPageParser = NPRPageParser()
#         requestedHTML = NPRPageParser.RequestURL(link)
#         selectedHTML = NPRPageParser.SelectStory(requestedHTML.text) # select the returned HTML
#         editionDayData.append(NPRPageParser.GetEditionData(link, selectedHTML)) # get various article data from this day
#         for story in selectedHTML.xpath('.//div[@id="story-list"]/*'):
#             if story.attrib['class'] == 'rundown-segment':
#                 editionDayData.append(NPRPageParser.GetArticleInfo(story))
#             elif story.attrib['class'] == 'music-interlude responsive-rundown':
#                 for songMETA in story.xpath('.//div[@class="song-meta-wrap"]'):
#                     interlude = dict()
#                     interlude["MoWeEd Track"] = NPRPageParser.GetInterludeSongName(songMETA)
#                     interlude["MoWeEd Artists"] = NPRPageParser.GetInterludeArtistNames(songMETA)
#                     editionDayData.append(interlude)
#                     print(json.dumps(interlude, indent=4, sort_keys=True, ensure_ascii=False))
#         nprPageParser.SaveJSONFile(editionDayData)
#         print("Finished {0}\n".format(editionDayData[0]['Page Link']))
#         editionDayData.clear()
#         time.sleep(1.5) # Don't hammer their server

startDate = datetime(1995, 12, 31)
directoryBase = "MoWeEd Article Data"
projectName = "MoWeEd"
weekendEdition = "Weekend Edition"
morningEdition = "Morning Edition"
nprPlaylistCreator = NPRPlaylistCreator()
nprSpotifySearch = NPRSpotifySearch()
nprPageParser = NPRPageParser()
spotifyTracks = list()
while startDate.month != 11:
    directoryYearMonth = "{0}/{1}".format(startDate.year, startDate.strftime("%m"))
    dateAndDay = "{0} {1}".format(startDate.strftime("%Y-%m-%d"), startDate.strftime("%a"))
    fileType = ".json"
    playlistName = ""
    # Load article data from disk
    if startDate.weekday() <= 4:
        playlistName = projectName + " " + dateAndDay + " " + morningEdition
        pathAndFile = directoryBase + "/" + directoryYearMonth + "/" + playlistName + fileType
        editionDay = NPRPageParser.LoadJSONFile(pathAndFile)
        #
    else:
        playlistName = projectName + " " + dateAndDay + " " + weekendEdition
        pathAndFile = directoryBase + "/" + directoryYearMonth + "/" + playlistName + fileType
        editionDay = NPRPageParser.LoadJSONFile(pathAndFile)
    playlistURI = "Playlist URI"
    # Create or update playlist
    if editionDay != None:
        for story, entry in enumerate(editionDay):
            if playlistURI in entry:
                print("-- Update Playlist --")
            else:
                print("-- Create Playlist --")
                response = nprPlaylistCreator.CreatePlaylist(playlistName) # should I deal with passing in my editionDay or manage updates/changes out here?
                editionDay[0]["Playlist URI"] = response["id"]
                editionDay[0]["Playlist Link"] = response["external_urls"]["spotify"]
                editionDay[0]["Snapshot ID"] = response["snapshot_id"]
                editionDay[0]["Playlist Name"] = playlistName
                nprPlaylistCreator.AddCoverArtToPlaylist(editionDay)
                break
        searchKey = "MoWeEd Track"
        # Search interlude tracks and add results back into edition data
        for story, entry in enumerate(editionDay):
            if searchKey in entry:
                trackEntry = nprSpotifySearch.SearchSpotify(entry["MoWeEd Track"], entry["MoWeEd Artists"])
                entry.update(trackEntry)
        # Add matched tracks to playlist
        nprPlaylistCreator.AddTracksToPlaylist(editionDay)
        # Update playlist description
        nprPlaylistCreator.UpdatePlaylistDescription(editionDay)
        # Create or update json edition data
        nprPageParser.SaveJSONFile(editionDay, pathAndFile)
        print("{0} finished {1}".format(startDate.date(), editionDay[0]['Playlist Link']))
        print("https://" + editionDay[0]["Page Link"])
        print("\n")
        editionDay.clear()
        startDate = startDate + timedelta(days=+1)
        time.sleep(1.5) # Don't hammer their server
    else:
        startDate = startDate + timedelta(days=+1)

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

