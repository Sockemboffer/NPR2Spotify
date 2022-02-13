import enum
import os
import time
import json
import calendar
from datetime import datetime
from datetime import timedelta
from turtle import left
from urllib.parse import urlparse
from NPRPageParser import NPRPageParser
from NPRSpotifySearch import NPRSpotifySearch
from dateutil.relativedelta import relativedelta
from NPRPlaylistCreator import NPRPlaylistCreator

# Pitfall sometimes matches the wrong rendition than the one NPR choose (Maybe there is a Shazam API?)
# TODO Create a dependiencies manifest.
# TODO Make more pythonic all around.
# TODO Automate to run daily.
# TODO catch and handle badgateway error that happens seldomly
# TODO figure out 10054 error with Stopiy

# Understand what day we left off or if left off is new year
def createLeftOffDate(today: datetime, projectName: str):
    leftOffDate = today
    editionYearLinkCache = dict()
    isLeftOffYear = False
    # Checking if we're ahead of left off date
    if leftOffDate.year >= datetime.today().year:
        while isLeftOffYear != True:
            editionYearLinkCache = NPRPageParser.LoadJSONFile(projectName + " Article Link Cache/" + str(leftOffDate.year) + " " + projectName + " Article Link Cache.json")
            if editionYearLinkCache == None:
                leftOffDate = datetime(leftOffDate.year-1, 1, 1)
            else:
                isLeftOffYear = True
    else:
        while isLeftOffYear != True:
            editionYearLinkCache = NPRPageParser.LoadJSONFile(projectName + " Article Link Cache/" + str(leftOffDate.year) + " " + projectName + " Article Link Cache.json")
            if editionYearLinkCache == None:
                return leftOffDate
            else:
                isLeftOffYear = True
    # # left off month will be first entry in the dictionary or a new entry for new year
    # if editionYearLinkCache != None:
    for month, links in editionYearLinkCache.items():
        # ATC check if no entry yet (new year)
        if len(links) != 0:
            leftOffDate = datetime(leftOffDate.year, int(month), len(links))
            leftOffDate = leftOffDate + timedelta(days=+1)
            return leftOffDate
        elif len(links) == leftOffDate.day:
            leftOffDate = datetime(leftOffDate.year, int(month), 1)
            return leftOffDate
    else:
        return leftOffDate

# Step 2
# Weekend edition shows up 1998 Jan
# July 25th 2000's seems to be when some morning edition interlude data is being documented
# Used to create json output for each day with various article and track data
# TODO Gotta be a cleaner way than this
def ParseDayLinks(leftOffDate: datetime, today: str, projectName: str):
    while leftOffDate <= today:
        leftOffYear = leftOffDate
        editionDayData = list() 
        editionYearLinkCache = NPRPageParser.LoadJSONFile(projectName + " Article Link Cache/" + str(leftOffDate.year) + " " + projectName + " Article Link Cache.json")
        if editionYearLinkCache != None:
            year = editionYearLinkCache # editionYearLinkCache[str(leftOffDate.month).zfill(2)]
            for month, links in year.items():
                for i, link in enumerate(links):
                    requestedHTML = NPRPageParser.RequestURL(link)
                    while requestedHTML == None:
                        requestedHTML = NPRPageParser.RequestURL(link)
                    selectedHTML = NPRPageParser.SelectStory(requestedHTML.text) # select the returned HTML
                    editionDayData.append(NPRPageParser.GetEditionData(link, selectedHTML)) # get various article data from this day
                    for story in selectedHTML.xpath('.//div[@id="story-list"]/*'):
                        if story.attrib['class'] == 'rundown-segment':
                            editionDayData.append(NPRPageParser.GetArticleInfo(story))
                        elif story.attrib['class'] == 'music-interlude responsive-rundown':
                            for songMETA in story.xpath('.//div[@class="song-meta-wrap"]'):
                                interlude = dict()
                                # ATCNPR Pass project names for keys
                                interlude["ATC Track"] = NPRPageParser.GetInterludeSongName(songMETA)
                                interlude["ATC Artists"] = NPRPageParser.GetInterludeArtistNames(songMETA)
                                editionDayData.append(interlude)
                                print(json.dumps(interlude, indent=4, sort_keys=True, ensure_ascii=False))
                    editionYear = editionDayData[0]['Date Numbered'][0:4]
                    editionMonth = editionDayData[0]['Date Numbered'].partition("-")[2].partition("-")[0]
                    editionDate = editionDayData[0]['Date Numbered']
                    editionDay = editionDayData[0]['Day']
                    editionEdition = editionDayData[0]["Edition"][0:15]
                    fileType = ".json"
                    fileName = projectName + " " + editionDate + " " + editionDay + " " + editionEdition + " Considered" + fileType
                    directoryPath = projectName + " Article Data/{0}/{1}/".format(editionYear, editionMonth)
                    NPRPageParser.SaveJSONFile(editionDayData, directoryPath, fileName)
                    editionDayData.clear()
                    leftOffDate = leftOffDate + timedelta(days=+1)
        # else:
        #     NPRPageParser.CreateLinkCacheJSONFile(projectName)
        leftOffDate = datetime(leftOffYear.year+1, 1, 1)


# Step 3
# Used to parse a range of dates, load the json for those days, and make playlists on spotify
# TODO Refactor janky two whiles, messy all around
def createPlaylists(leftOffDate: datetime, today: datetime, projectName: str, user_id):
    startDate = leftOffDate
    weekendEdition = "Weekend Edition"
    morningEdition = "Morning Edition"
    allThingsConsidered = "All Things Considered"
    nprPlaylistCreator = NPRPlaylistCreator()
    nprSpotifySearch = NPRSpotifySearch()
    # nprPageParser = NPRPageParser()
    # spotifyTracks = list()
    startTime = datetime.now()
    while startDate <= today and projectName == "MoWeEd":
        processedTime = datetime.now()
        # ATCNPR Rework how path and file are created
        projectPath = projectName + " Article Data/{0}/{1}/".format(startDate.year, startDate.strftime("%m"))
        morningEditionFileName = projectName + " {0} {1} {2}".format(startDate.strftime("%Y-%m-%d"), startDate.strftime("%a"), morningEdition)
        weekendEditionFileName = projectName + " {0} {1} {2}".format(startDate.strftime("%Y-%m-%d"), startDate.strftime("%a"), weekendEdition)
        fileType = ".json"
        # Load article data from disk
        if startDate.weekday() <= 4:
            editionDay = NPRPageParser.LoadJSONFile(projectPath + morningEditionFileName + fileType)
            filename = morningEditionFileName
        else:
            editionDay = NPRPageParser.LoadJSONFile(projectPath + weekendEditionFileName + fileType)
            filename = weekendEditionFileName
        # check if edition data is present
        if editionDay == None:
            print(">> No data for {0} ".format(startDate.date()))
            startDate = startDate + timedelta(days=+1)
            break
        else:
            playlistKey = "Playlist URI"
            playlistEntry = False
            if editionDay[0].get(playlistKey) != None:
                playlistEntry = True # would only be in the first entry currently
            trackKey = "MoWeEd Track"
            trackEntry = False
            for item in editionDay:
                if item.get(trackKey) == None:
                    continue
                else:
                    trackEntry = True
                    break
            if playlistEntry == True and trackEntry == True:
                # Search interlude tracks and add results back into edition data
                for story, entry in enumerate(editionDay):
                    if trackKey in entry:
                        track = nprSpotifySearch.SearchSpotify(entry["MoWeEd Track"], entry["MoWeEd Artists"])
                        entry.update(track)
                editionDay = nprPlaylistCreator.ReplaceTracksInPlaylist(editionDay)
                nprPlaylistCreator.UpdatePlaylistDescription(editionDay)
                NPRPageParser.SaveJSONFile(editionDay, projectPath, filename + fileType)
                print("{0} finished updating {1}".format(startDate.date(), editionDay[0]['Playlist Link']))
                print(editionDay[0]["Page Link"])
                editionDay.clear()
                startDate = startDate + timedelta(days=+1)
            elif playlistEntry == False and trackEntry == True:
                # Create a new playlist
                for story, entry in enumerate(editionDay):
                    if entry.get(trackKey):
                        track = nprSpotifySearch.SearchSpotify(entry["MoWeEd Track"], entry["MoWeEd Artists"])
                        entry.update(track)
                response = nprPlaylistCreator.CreatePlaylist(filename)
                editionDay[0]["Playlist URI"] = response["id"]
                editionDay[0]["Playlist Link"] = response["external_urls"]["spotify"]
                editionDay[0]["Snapshot ID"] = response["snapshot_id"]
                editionDay[0]["Playlist Name"] = filename
                nprPlaylistCreator.AddCoverArtToPlaylist(editionDay)
                nprPlaylistCreator.AddTracksToPlaylist(editionDay)
                nprPlaylistCreator.UpdatePlaylistDescription(editionDay)
                NPRPageParser.SaveJSONFile(editionDay, projectPath, filename + fileType)
                print("{0} finished {1}".format(startDate.date(), editionDay[0]['Playlist Link']))
                print(editionDay[0]["Page Link"])
                editionDay.clear()
                startDate = startDate + timedelta(days=+1)
            else:
                # we create an empty playlist with a description noting tracks are not detailed
                # Some articles have no track data and we still make a playlist
                response = nprPlaylistCreator.CreatePlaylist(filename)
                editionDay[0]["Playlist URI"] = response["id"]
                editionDay[0]["Playlist Link"] = response["external_urls"]["spotify"]
                editionDay[0]["Snapshot ID"] = response["snapshot_id"]
                editionDay[0]["Playlist Name"] = filename
                nprPlaylistCreator.AddCoverArtToPlaylist(editionDay)
                nprPlaylistCreator.UpdatePlaylistDescription(editionDay)
                NPRPageParser.SaveJSONFile(editionDay, projectPath, filename + fileType)
                print(">> No interlude Tracks for {0} ".format(startDate.date()))
                editionDay.clear()
                startDate = startDate + timedelta(days=+1)
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%I:%M %p")
            print("Current time: {0}, Process time: {1}, Run time: {2}".format(timestampStr, datetime.now() - processedTime, datetime.now() - startTime))
            print("\n")
    while startDate <= today and projectName == "ATC":
        processedTime = datetime.now()
        projectPath = projectName + " Article Data/{0}/{1}/".format(startDate.year, startDate.strftime("%m"))
        ATCPathFileName = projectName + " {0} {1} {2}".format(startDate.strftime("%Y-%m-%d"), startDate.strftime("%a"), allThingsConsidered)
        filename = ATCPathFileName
        fileType = ".json"
        editionDay = NPRPageParser.LoadJSONFile(projectPath + ATCPathFileName + fileType)
        if editionDay == None:
            print(">> No data for {0} ".format(startDate.date()))
            startDate = startDate + timedelta(days=+1)
        else:
            playlistKey = "Playlist URI"
            playlistEntry = False
            if editionDay[0].get(playlistKey) != None:
                playlistEntry = True # would only be in the first entry currently
            trackKey = "ATC Track"
            trackEntry = False
            for item in editionDay:
                if item.get(trackKey) == None:
                    continue
                else:
                    trackEntry = True
                    break
            if playlistEntry == True and trackEntry == True:
                # Search interlude tracks and add results back into edition data
                for story, entry in enumerate(editionDay):
                    if trackKey in entry:
                        track = nprSpotifySearch.SearchSpotify(entry["ATC Track"], entry["ATC Artists"], user_id)
                        entry.update(track)
                editionDay = nprPlaylistCreator.ReplaceTracksInPlaylist(editionDay, user_id)
                nprPlaylistCreator.UpdatePlaylistDescription(editionDay, user_id)
                NPRPageParser.SaveJSONFile(editionDay, projectPath, filename + fileType)
                print("{0} finished updating {1}".format(startDate.date(), editionDay[0]['Playlist Link']))
                print(editionDay[0]["Page Link"])
                editionDay.clear()
                startDate = startDate + timedelta(days=+1)
            elif playlistEntry == False and trackEntry == True:
                # Create a new playlist
                for story, entry in enumerate(editionDay):
                    if entry.get(trackKey):
                        track = nprSpotifySearch.SearchSpotify(entry["ATC Track"], entry["ATC Artists"], user_id)
                        entry.update(track)
                response = nprPlaylistCreator.CreatePlaylist(filename, user_id)
                editionDay[0]["Playlist URI"] = response["id"]
                editionDay[0]["Playlist Link"] = response["external_urls"]["spotify"]
                editionDay[0]["Snapshot ID"] = response["snapshot_id"]
                editionDay[0]["Playlist Name"] = filename
                nprPlaylistCreator.AddCoverArtToPlaylist(editionDay, user_id)
                nprPlaylistCreator.AddTracksToPlaylist(editionDay, user_id)
                nprPlaylistCreator.UpdatePlaylistDescription(editionDay, user_id)
                NPRPageParser.SaveJSONFile(editionDay, projectPath, filename + fileType)
                print("{0} finished {1}".format(startDate.date(), editionDay[0]['Playlist Link']))
                print(editionDay[0]["Page Link"])
                editionDay.clear()
                startDate = startDate + timedelta(days=+1)
            else:
                # we create an empty playlist with a description noting tracks are not detailed
                # Some articles have no track data and we still make a playlist
                response = nprPlaylistCreator.CreatePlaylist(filename, user_id)
                editionDay[0]["Playlist URI"] = response["id"]
                editionDay[0]["Playlist Link"] = response["external_urls"]["spotify"]
                editionDay[0]["Snapshot ID"] = response["snapshot_id"]
                editionDay[0]["Playlist Name"] = filename
                nprPlaylistCreator.AddCoverArtToPlaylist(editionDay, user_id)
                nprPlaylistCreator.UpdatePlaylistDescription(editionDay, user_id)
                NPRPageParser.SaveJSONFile(editionDay, projectPath, filename + fileType)
                print(">> No interlude Tracks for {0} ".format(startDate.date()))
                editionDay.clear()
                startDate = startDate + timedelta(days=+1)
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%I:%M %p")
            print("Current time: {0}, Process time: {1}, Run time: {2}".format(timestampStr, datetime.now() - processedTime, datetime.now() - startTime))
            print("\n")


# ATC has music listed starting from January 2nd, 1996
# projectPrefix = "MoWeEd"
projectPrefix = "ATC"
projectName = "All Things Considered"
user_id = "SPOTIFY_USER_ID_ATC"
today = datetime(2004, 12, 31)
leftOffDate = datetime(2004, 4, 1)# createLeftOffDate(today, projectName)
# NPRPageParser.NPRArticleLinkCacheCreator(leftOffDate, projectName)
# ParseDayLinks(leftOffDate, today, projectName)
createPlaylists(leftOffDate, today, projectPrefix, user_id)
# nprPlaylistCreator = NPRPlaylistCreator()
# nprPlaylistCreator.ChangePlaylistToPublic(leftOffDate, today, projectPrefix, projectName, user_id)