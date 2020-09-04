import re
import json
import time
import requests
import datetime
from parsel import Selector
#import urllib.parse import urlparse
# todo: generate valid npr page urls for morning and weekend edition
    # https://www.npr.org/programs/morning-edition/archive?date=6-1-2020 26th seems to be first where interludes are entered
    # https://www.npr.org/programs/morning-edition/2000/07/31/12993145/
    # https://www.npr.org/programs/morning-edition/archive?date=1-2-1996 first entry

    # https://www.npr.org/programs/weekend-edition-saturday/archive?date=6-1-2020
    # https://www.npr.org/programs/weekend-edition-saturday/2000/07/29/13066500/
    # https://www.npr.org/programs/weekend-edition-saturday/archive?date=3-11-1995 # first entry

    # https://www.npr.org/programs/weekend-edition-sunday/archive?date=6-1-2020
    # https://www.npr.org/programs/weekend-edition-sunday/2000/07/30/12993115/
    # https://www.npr.org/programs/weekend-edition-sunday/archive?date=1-4-1998 # first entry
    # page links contain a unique article data ID that'll need to be captured for a correctly formated link
    # 
# todo: create timer to gate page scanning

datesToSort1 = [
"https://www.npr.org/programs/morning-edition/2018/5/2/661993253/morning-edition-for-october-30-2018?showDate=2018-10-30",
"https://www.npr.org/programs/morning-edition/2018/7/3/661661069/morning-edition-for-october-29-2018?showDate=2018-10-29",
"https://www.npr.org/programs/morning-edition/2018/12/4/660850176/morning-edition-for-october-26-2018?showDate=2018-10-26",
"https://www.npr.org/programs/morning-edition/2018/10/8/659400612/morning-edition-for-october-22-2018?showDate=2018-10-22",
"https://www.npr.org/programs/morning-edition/2018/7/9/658721177?showDate=2018-10-19",
"https://www.npr.org/programs/morning-edition/2018/7/5/660436473/morning-edition-for-october-25-2018?showDate=2018-10-25",
"https://www.npr.org/programs/morning-edition/2018/11/6/660112704/morning-edition-for-october-24-2018?showDate=2018-10-24",
"https://www.npr.org/programs/morning-edition/2018/7/1/662433741?showDate=2018-10-31",
"https://www.npr.org/programs/morning-edition/2018/7/10/658364589/morning-edition-for-october-18-2018?showDate=2018-10-18"]
"https://www.npr.org/programs/morning-edition/2018/7/7/659744952/morning-edition-for-october-23-2018?showDate=2018-10-23",

datesToSort2 = [
"https://www.npr.org/programs/morning-edition/2018/6/11/662433741?showDate=2018-10-31",
"https://www.npr.org/programs/morning-edition/2018/7/14/660850176/morning-edition-for-october-26-2018?showDate=2018-10-26",
"https://www.npr.org/programs/morning-edition/2018/7/12/661993253/morning-edition-for-october-30-2018?showDate=2018-10-30",
"https://www.npr.org/programs/morning-edition/2018/1/13/661661069/morning-edition-for-october-29-2018?showDate=2018-10-29",
"https://www.npr.org/programs/morning-edition/2018/4/15/660436473/morning-edition-for-october-25-2018?showDate=2018-10-25",
"https://www.npr.org/programs/morning-edition/2018/7/16/660112704/morning-edition-for-october-24-2018?showDate=2018-10-24"]

datesToSort3 = [
"https://www.npr.org/programs/morning-edition/2018/2/1/661993253/morning-edition-for-october-30-2018?showDate=2018-10-30",
"https://www.npr.org/programs/morning-edition/2018/7/29/661661069/morning-edition-for-october-29-2018?showDate=2018-10-29",
"https://www.npr.org/programs/morning-edition/2018/3/26/660850176/morning-edition-for-october-26-2018?showDate=2018-10-26",
"https://www.npr.org/programs/morning-edition/2018/7/10/662433741?showDate=2018-10-31",
"https://www.npr.org/programs/morning-edition/2018/7/28/660436473/morning-edition-for-october-25-2018?showDate=2018-10-25"]

class Weekday():
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

class Months():
    JANUARY = 1
    FEBUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12

class NPRPageParser:
    def __init__(self):
        self.nprurl = ""

    # Cache all article links (1 per day) for a year across NPR Morning, Saturday, and Sunday Weekend Editions
    def NPRArticleLinkCacheCreator(yearEntry):
        # Any archive date always returns the last day of the month as the starting point to scroll from to get more days
        # Generate archive month link - choose 1st date so no need to check 28th - 31st
            # get each article day link until no more or 1st day of next month
                # if 1st of month, generate new archive link
                # if not 1st of following month, get xpath to <a rel="nofollow" href="/programs/morning-edition/archive?date=2000-08-25&amp;eid=13001962">More from Morning Edition</a> UTF-8 decode
                    # create new page to continue getting current month day links
        with open("NPRArticleLinkCache/" + str(yearEntry) + "-NPRArticleLinkCache.json", 'w', encoding='utf-8') as json_file:
            currentYear = dict()
            monthCount = 12
            while monthCount >= Months.JANUARY:
                articleDayLinks = list()
                currentMonth = dict()
                print(monthCount)
                time.sleep(5)
                # Archive link always starts the articles at the last valid day-type of that month
                # Rather than trying to figure out if month ends in 29-31 date, hard code the 1st,
                # since every month has a 1st
                # Grab all Sunday Edition links for this month
                sunday = "https://www.npr.org/programs/weekend-edition-sunday/archive?date={}-{}-{}".format(monthCount, 1, yearEntry)
                request = requests.get(sunday).text
                selector = Selector(text=request)
                for item in selector.xpath('.//div[@id="episode-list"]/*'):
                    if item.attrib['class'] != 'episode-list__header':
                        articleDayLinks.append(item.xpath('./h2[@class="program-show__title"]/a/@href').get())
                articleDayLinks = list(filter(lambda x: "/" + str(monthCount).zfill(2) + "/" in x, articleDayLinks))
                print(articleDayLinks)
                # Grab all Saturday Edition links for this month
                saturday = "https://www.npr.org/programs/weekend-edition-saturday/archive?date={}-{}-{}".format(monthCount, 1, yearEntry)
                time.sleep(2.5) # maybe put in some random range to help spamming
                request = requests.get(saturday).text
                selector = Selector(text=request)
                for item in selector.xpath('.//div[@id="episode-list"]/*'):
                    if item.attrib['class'] != 'episode-list__header':
                        articleDayLinks.append(item.xpath('./h2[@class="program-show__title"]/a/@href').get())
                articleDayLinks = list(filter(lambda x: "/" + str(monthCount).zfill(2) + "/" in x, articleDayLinks))
                print(articleDayLinks)
                # Grab all Morning Edition links for this month
                # NPR only loading more days once user scrolls to the bottom,
                # we need to fetch the "scrolllink" data to grab more days till a new month is found
                weekday = "https://www.npr.org/programs/morning-edition/archive?date={}-{}-{}".format(monthCount, 1, yearEntry)
                time.sleep(3.5) # maybe put in some random range to help spamming
                request = requests.get(weekday).text
                selector = Selector(text=request)
                for item in selector.xpath('.//div[@id="episode-list"]/*'):
                    if item.attrib['class'] != 'episode-list__header':
                        articleDayLinks.append(item.xpath('./h2[@class="program-show__title"]/a/@href').get())
                articleDayLinks = list(filter(lambda x: "/" + str(monthCount).zfill(2) + "/" in x, articleDayLinks))
                print(articleDayLinks)
                # load more days
                nextMonthNotFound = True
                checkMonth = str(yearEntry) + "/" + str(monthCount).zfill(2) + "/"
                print(checkMonth)
                while nextMonthNotFound:
                    #print(selector.xpath('//div[@id="scrolllink"]/a/@href').get())
                    loadMoreDaysLink = selector.xpath('//div[@id="scrolllink"]/a/@href').get()
                    #print(loadMoreDaysLink)
                    moreDaysLink = "https://www.npr.org" + loadMoreDaysLink
                    time.sleep(2) # maybe put in some random range to help spamming
                    request = requests.get(moreDaysLink).text
                    selector = Selector(text=request)
                    for item in selector.xpath('.//div[@id="episode-list"]/*'):
                        if item.attrib['class'] != 'episode-list__header':
                            newLink = item.xpath('./h2[@class="program-show__title"]/a/@href').get()
                            if checkMonth in newLink:
                                print(newLink)
                                articleDayLinks.append(newLink)
                            else:
                                nextMonthNotFound = False
                                #print(newLink)
                # Prune out non-matching months
                articleDayLinks = list(filter(lambda x: "/" + str(monthCount).zfill(2) + "/" in x, articleDayLinks))
                #print(articleDayLinks)
                #print(filteredDays)
                # Sort remaining days 
                articleDayLinks = sorted(articleDayLinks, key=lambda x: int(x.partition("/" + str(monthCount).zfill(2) + "/")[2].partition("/")[0]))
                #print(currentMonth)
                print(articleDayLinks)
                currentMonth[str(monthCount).zfill(2)] = articleDayLinks
                # add month to year dictionary value
                currentYear.update(currentMonth)
                monthCount -= 1
            # Dump year that contains all months into a year json file
            json.dump(currentYear, json_file, ensure_ascii=False, indent=4)
        return

    # Request the html at link address
    def RequestURL():
        request = requests.get(NPRPageParser.nprurl)
        if request.reason != "OK":
            print("Link: " + NPRPageParser.nprurl + "\n" + request.reason)

    # Grab the Story block of an npr page to parse article and interulde data into a json file
    def GetNPRStory(pagehtml, filename):
        selector = Selector(text=pagehtml)
        with open(filename, 'w', encoding='utf-8') as json_file:
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
            pageData['Playlist Name'] = pageData['Date Text'] + " - Interlude(s) for NPR " + pageData['Edition']
        else:
            pageData['Playlist Name'] = pageData['Date Text'] + " - Interlude(s) for NPR " + pageData['Edition'] + " " + pageData['Day']
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
        artistDataList = re.split('[&,]', re.sub(" +", " ", re.sub("^\s+|\s+$", "", interlude.xpath('.//span[@class="song-meta-artist"]/text()').get())))
        strippedArtistList = list()
        for artist in artistDataList:
            strippedArtist = artist.strip()
            strippedArtistList.append(strippedArtist)
        artistData['Interlude Artist'] = strippedArtistList
        artistData['Interlude Song']  = re.sub(" +", " ", re.sub("^\s+|\s+$", "", interlude.xpath('.//span[@class="song-meta-title"]/text()').get()))
        artistData['Spotify URI'] = None
        artistData['Last Checked'] = None
        return artistData

    # Load json file data, check to ensure it's valid first
    def LoadJSONFile(filename):
        with open(filename, "r", encoding='utf-8') as json_file:
            try:
                loadedJson = json.load(json_file)
                json_file.close()
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