import os
import re
import json
import time
import requests
import datetime
from parsel import Selector
from NPRPlaylistCreator import NPRPlaylistCreator

class NPRPageParser:
    def __init__(self):
        self.nprurl = ""

    # Request the html at link address
    def RequestURL(url):
        request = requests.get(url)
        if request.reason != "OK":
            print("Link: " + url + "\n" + request.reason)
        else:
            print("-- URL Request Successful.")
            return request

    # Grab the HTML Story block
    def SelectStory(html):
        selector = Selector(text=html)
        print("-- NPR Page Selected.")
        return selector

    # Grab various info about the whole NPR article for that date
    # TODO use shortened 3 letter month names for playlist name
    # TODO store playlist track order numbering for use when making updates from helpers?
    def GetEditionData(url, selectedHTML):
        nprPlaylistCreator = NPRPlaylistCreator()
        dayDetails = dict()
        dayDetails['Page Link'] = url.partition("https://")[2].partition("?")[0]
        dayDetails['Edition'] = selectedHTML.xpath('//header[@class="contentheader contentheader--one"]//h1/b/text()').get()
        dayDetails['Date Text'] = selectedHTML.xpath('//div[@id="episode-core"]//nav[@class="program-nav program-nav--one"]//time/b/text()[2]').get().strip()
        dayDetails['Date Numbered'] = selectedHTML.xpath('//div[@id="episode-core"]//nav[@class="program-nav program-nav--one"]//time/@datetime').get()
        dayDetails['Day'] = selectedHTML.xpath('//div[@id="episode-core"]//nav[@class="program-nav program-nav--one"]//time/b[@class="date"]//b[@class="day"]/text()').get().strip(' ,')
        dt = str(datetime.datetime.now().__format__("%Y-%m-%d %H:%M:%S"))
        dayDetails['Scanned Date'] = dt
        if (dayDetails['Day'] == 'Saturday') or (dayDetails['Day'] == 'Sunday'):
            dayDetails['Playlist Name'] = "NPR " + dayDetails['Date Text'] + " - Interludes for " + dayDetails['Edition']
        else:
            dayDetails['Playlist Name'] = "NPR " + dayDetails['Date Text'] + " - Interludes for " + dayDetails['Edition'] + " " + dayDetails['Day']
        playlistName = dayDetails['Playlist Name']
        responseJSON = nprPlaylistCreator.CreatePlaylist(playlistName)
        dayDetails['Playlist Link'] = responseJSON["external_urls"]["spotify"]
        dayDetails['Playlist URI'] = responseJSON["id"]
        print("-- Edition Data Found.")
        return dayDetails

    # Grab data about each article         
    def GetArticleInfo(articleHTML):
        articleInfo = dict()
        articleInfo['Title'] = articleHTML.xpath('.//div/h3[@class="rundown-segment__title"]/a/text()').get()
        articleInfo['Link'] = articleHTML.xpath('.//div/h3[@class="rundown-segment__title"]/a/@href').get()
        articleInfo['Slug'] = articleHTML.xpath('.//div/h4[@class="rundown-segment__slug"]/a/text()').get()
        articleInfo['By'] = articleHTML.xpath('.//span[@class="byline byline--inline"]/text()').get()
        print("-- Article Info Found.")
        return articleInfo

    # Grab data about each interlude
    def GetInterludeSongName(songHTML):
        if songHTML.xpath('.//span[@class="song-meta-title"]/text()').get() == None:
            return " "
        else: 
            return re.sub(" +", " ", re.sub("^\s+|\s+$", "", songHTML.xpath('.//span[@class="song-meta-title"]/text()').get()))
    
    def GetInterludeArtistNames(songHTML):
        if songHTML.xpath('.//span[@class="song-meta-artist"]/text()').get() == None:
            return " "
        else:
            artists = re.split('[,;&/]', re.sub(" +", " ", re.sub("^\s+|\s+$", "", songHTML.xpath('.//span[@class="song-meta-artist"]/text()').get())))
            artists[:] = [s.strip() for s in artists]
            return artists

    # Load json file data, check to ensure it's valid first
    def LoadJSONFile(filename):
        with open(filename, "r", encoding='utf-8') as json_file:
            try:
                loadedJson = json.load(json_file)
                return loadedJson
            except ValueError as e:
                print('invalid json: %s' % e)
                return None # or: raise
    
    def SaveJSONFile(self, editionData):
        playlistPath = os.path.join("NPRArticleData", editionData[0]['Date Numbered'][:4], editionData[0]['Date Numbered'][5:7], "")
        if not os.path.exists(playlistPath):
            os.makedirs(playlistPath)
        with open(str(playlistPath + editionData[0]['Playlist Name'] + ".json"), 'w', encoding='utf-8') as json_file:
            json.dump(editionData, json_file, ensure_ascii=False, indent=4)

    # request/fetch artist data from json file
    def GetArtistsAndTrack(jsonData):
        interludes = list()
        for entry in jsonData:
            for value in entry:
                if isinstance(value, dict):
                    interludes.append(value)
        return interludes

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