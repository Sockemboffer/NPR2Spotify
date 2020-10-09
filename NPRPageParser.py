import os
import re
import json
import time
import requests
import datetime
from parsel import Selector

class NPRPageParser:
    def __init__(self):
        self.nprurl = ""

    # Request the html at link address
    def RequestURL():
        request = requests.get(NPRPageParser.nprurl)
        if request.reason != "OK":
            print("Link: " + NPRPageParser.nprurl + "\n" + request.reason)
        else:
            return request

    # Grab the Story block and grab the article and interlude data I want, organize into folders on disk
    def GetNPRStory(pagehtml):
        selector = Selector(text=pagehtml)
        pageData = list()
        pageData.append(NPRPageParser.GetStoryInfo(selector))
        for item in selector.xpath('.//div[@id="story-list"]/*'):
            if item.attrib['class'] == 'rundown-segment':
                newArticleData = NPRPageParser.GetArticleInfo(item)
                pageData.append(newArticleData)
            elif item.attrib['class'] == 'music-interlude responsive-rundown':
                newInterludeInfo = list()
                for artist in item.xpath('.//div[@class="song-meta-wrap"]'):
                    newInterludeInfo.append(NPRPageParser.GetInterludeInfo(artist))
                pageData.append(newInterludeInfo)
        playlistPath = os.path.join("NPRArticleData", pageData[0]['Date Numbered'][:4], pageData[0]['Date Numbered'][5:7], "")
        if not os.path.exists(playlistPath):
            os.makedirs(playlistPath)
        with open(playlistPath + pageData[0]['Playlist Name'] + ".json", 'w', encoding='utf-8') as json_file:
            json.dump(pageData, json_file, ensure_ascii=False, indent=4)
        print("-- NPR Page file created.")

    # Grab various info about the whole NPR article for that date
    def GetStoryInfo(pageSelector):
        pageData = dict()
        pageData['Page Link'] = NPRPageParser.nprurl
        pageData['Edition'] = pageSelector.xpath('//header[@class="contentheader contentheader--one"]//h1/b/text()').get()
        pageData['Date Text'] = pageSelector.xpath('//div[@id="episode-core"]//nav[@class="program-nav program-nav--one"]//time/b/text()[2]').get().strip()
        pageData['Date Numbered'] = pageSelector.xpath('//div[@id="episode-core"]//nav[@class="program-nav program-nav--one"]//time/@datetime').get()
        pageData['Day'] = pageSelector.xpath('//div[@id="episode-core"]//nav[@class="program-nav program-nav--one"]//time/b[@class="date"]//b[@class="day"]/text()').get().strip(' ,')
        dt = str(datetime.datetime.now().__format__("%Y-%m-%d %H:%M:%S"))
        pageData['Scanned Date'] = dt
        if (pageData['Day'] == 'Saturday') or (pageData['Day'] == 'Sunday'):
            pageData['Playlist Name'] = "NPR " + pageData['Date Text'] + " - Interludes for " + pageData['Edition']
        else:
            pageData['Playlist Name'] = "NPR " + pageData['Date Text'] + " - Interludes for " + pageData['Edition'] + " " + pageData['Day']
        pageData['Playlist Link'] = None
        pageData['Playlist URI'] = None
        return pageData

    # Grab multiple by-line authors
    def GetArticleAuthors(article):
        return article.xpath('.//span[@class="byline byline--inline"]/text()').getall()

    # Grab data about each article         
    def GetArticleInfo(article):
        articleData = dict()
        articleData['Article'] = article.xpath('./div/h3[@class="rundown-segment__title"]/a/text()').get()
        articleData['Link'] = article.xpath('./div/h3[@class="rundown-segment__title"]/a/@href').get()
        articleData['Slug'] = article.xpath('./div/h4[@class="rundown-segment__slug"]/a/text()').get()
        articleData['By'] = NPRPageParser.GetArticleAuthors(article)
        return articleData

    # Grab data about each interlude
    def GetInterludeInfo(interlude):
        artistData = dict()
        # gross trim leading/trailing then duplicate spaces also splitting artists if "&" or "," found into list
        if interlude.xpath('.//span[@class="song-meta-artist"]/text()').get() == None:
            artistDataList = None
        else:
            artistDataList = re.split('[&,]', re.sub(" +", " ", re.sub("^\s+|\s+$", "", interlude.xpath('.//span[@class="song-meta-artist"]/text()').get())))
            strippedArtistList = list()
            for artist in artistDataList:
                strippedArtist = artist.strip()
                strippedArtistList.append(strippedArtist)
                artistDataList = strippedArtistList
        artistData['Interlude Artist'] = artistDataList
        if interlude.xpath('.//span[@class="song-meta-title"]/text()').get() == None:
            songTitle = None
        else: 
            songTitle = re.sub(" +", " ", re.sub("^\s+|\s+$", "", interlude.xpath('.//span[@class="song-meta-title"]/text()').get()))
        artistData['Interlude Song'] = songTitle
        artistData['Spotify URI'] = None
        artistData['Last Checked'] = None
        return artistData

    # Load json file data, check to ensure it's valid first
    def LoadJSONFile(filename):
        with open(filename, "r", encoding='utf-8') as json_file:
            try:
                loadedJson = json.load(json_file)
                return loadedJson
            except ValueError as e:
                print('invalid json: %s' % e)
                return None # or: raise

    # request/fetch artist data from json file
    def GetArtistsAndTrack(jsonData):
        interludes = list()
        for entry in jsonData:
            for value in entry:
                if isinstance(value, dict):
                    interludes.append(value)
        return interludes

    # After we've searched spotify and found our results, push some data back into the json file for future rescans
    def UpdateJSONFile(filename, playlistDetails, searchedTracks):
        jsonData = NPRPageParser.LoadJSONFile(filename)
        with open(filename, 'w', encoding='utf-8') as json_file:
            for pageItem in jsonData: # pageItem has keys and lists
                if isinstance(pageItem, dict): #for item in pageItem: # loop over key
                    for pageItemKey, pageItemValue in pageItem.items():
                        if pageItemKey == "Playlist Link":
                            pageItem["Playlist Link"] = playlistDetails["external_urls"]["spotify"]
                        if pageItemKey == "Playlist URI":
                            pageItem["Playlist URI"] = playlistDetails["uri"]
            for pageItemKey in jsonData:
                if isinstance(pageItemKey, list): # confirm we are in a pageItemKey that has an interlude list
                    for searchedTrack in searchedTracks: # Now loop over our searchedTracks looking for a matching interlude
                        for interlude in pageItemKey: # loop over each interlude track
                            if interlude["Interlude Song"] == searchedTrack["NPR Track Name"]: # we have a match to update
                                if searchedTrack["Found Match Type"] == "HitExactMatch" or searchedTrack["Found Match Type"] == "HitPartialMatch":
                                    interlude['Spotify URI'] = searchedTrack["Found Track URI"]
                                    interlude['Last Checked'] = str(datetime.datetime.now().__format__("%Y-%m-%d %H:%M:%S"))
                                else:
                                    interlude['Last Checked'] = str(datetime.datetime.now().__format__("%Y-%m-%d %H:%M:%S"))
            json.dump(jsonData, json_file, ensure_ascii=False, indent=4)
            json_file.close()

    # Cache every day's link across NPR Morning, Saturday, and Sunday Weekend Editions for 1 year.
    # Only need to run once for every archive year
    def NPRArticleLinkCacheCreator(yearEntry):
        with open("NPRArticleLinkCache/" + str(yearEntry) + "-NPRArticleLinkCache.json", 'w', encoding='utf-8') as json_file:
            currentYear = dict()
            monthCount = 12
            while monthCount >= 1:
                articleDayLinks = list()
                currentMonth = dict()
                print(monthCount)
                time.sleep(5) # No need to hammer their servers
                # Any archive date seems to set us at the last day of the month (handy)
                # Generate archive month link - use the 1st of every month
                # Grab all Sunday Editions for this month 
                sunday = "https://www.npr.org/programs/weekend-edition-sunday/archive?date={}-{}-{}".format(monthCount, 1, yearEntry)
                request = requests.get(sunday).text
                selector = Selector(text=request)
                for item in selector.xpath('.//div[@id="episode-list"]/*'):
                    if item.attrib['class'] != 'episode-list__header':
                        articleDayLinks.append(item.xpath('./h2[@class="program-show__title"]/a/@href').get())
                articleDayLinks = list(filter(lambda x: "/" + str(monthCount).zfill(2) + "/" in x, articleDayLinks))
                # Grab all Saturday Edition links for this month
                saturday = "https://www.npr.org/programs/weekend-edition-saturday/archive?date={}-{}-{}".format(monthCount, 1, yearEntry)
                time.sleep(2.5)
                request = requests.get(saturday).text
                selector = Selector(text=request)
                for item in selector.xpath('.//div[@id="episode-list"]/*'):
                    if item.attrib['class'] != 'episode-list__header':
                        articleDayLinks.append(item.xpath('./h2[@class="program-show__title"]/a/@href').get())
                articleDayLinks = list(filter(lambda x: "/" + str(monthCount).zfill(2) + "/" in x, articleDayLinks))
                # Grab intial amount of Morning Edition links for this month
                weekday = "https://www.npr.org/programs/morning-edition/archive?date={}-{}-{}".format(monthCount, 1, yearEntry)
                time.sleep(3.5) # maybe put in some random range to help spamming
                request = requests.get(weekday).text
                selector = Selector(text=request)
                for item in selector.xpath('.//div[@id="episode-list"]/*'):
                    if item.attrib['class'] != 'episode-list__header':
                        articleDayLinks.append(item.xpath('./h2[@class="program-show__title"]/a/@href').get())
                articleDayLinks = list(filter(lambda x: "/" + str(monthCount).zfill(2) + "/" in x, articleDayLinks))
                # NPR only loads more days once the user scrolls to the bottom of their page,
                # we need to fetch the "scrolllink" link to grab more days untill a new month is found
                nextMonthNotFound = True
                checkMonth = str(yearEntry) + "/" + str(monthCount).zfill(2) + "/"
                while nextMonthNotFound:
                    loadMoreDaysLink = selector.xpath('//div[@id="scrolllink"]/a/@href').get()
                    # Check we have more days to load
                    if loadMoreDaysLink == None:
                        break
                    moreDaysLink = "https://www.npr.org" + loadMoreDaysLink
                    time.sleep(2)
                    request = requests.get(moreDaysLink).text
                    selector = Selector(text=request)
                    for item in selector.xpath('.//div[@id="episode-list"]/*'):
                        if item.attrib['class'] != 'episode-list__header':
                            newLink = item.xpath('./h2[@class="program-show__title"]/a/@href').get()
                            if checkMonth in newLink:
                                articleDayLinks.append(newLink)
                            else:
                                nextMonthNotFound = False
                articleDayLinks = list(filter(lambda x: "/" + str(monthCount).zfill(2) + "/" in x, articleDayLinks))
                articleDayLinks = sorted(articleDayLinks, key=lambda x: int(x.partition("/" + str(monthCount).zfill(2) + "/")[2].partition("/")[0]))
                print(articleDayLinks)
                currentMonth[str(monthCount).zfill(2)] = articleDayLinks
                currentYear.update(currentMonth)
                monthCount -= 1
            # Dump all months with all day's links into a year json file
            json.dump(currentYear, json_file, ensure_ascii=False, indent=4)
        return