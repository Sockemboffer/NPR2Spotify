import os
import time
import json
from urllib.parse import urlparse
from NPRPageParser import NPRPageParser
from NPRSpotifySearch import NPRSpotifySearch
from NPRPlaylistCreator import NPRPlaylistCreator

# # # Create a json file for each year of day links (only need to run one time)
# NPRPageParser.NPRArticleLinkCacheCreator(2018) # 1996 - 2020

# Load year cache data in so we can loop over every day of every month to generate article info to parse
yearToLoad = 1999
jsonLoadedYearCache = NPRPageParser.LoadJSONFile("NPRArticleLinkCache/" + str(yearToLoad) + "-NPRArticleLinkCache.json")
for month, daysList in jsonLoadedYearCache.items():
    for day in daysList:
        time.sleep(5) # Don't hammer their server
        print(day)
        # Parsing an NPR page for it's interlude track data
        NPRPageParser.nprurl = day
        pageHTML = NPRPageParser.RequestURL()
        NPRPageParser.GetNPRStory(pageHTML.text) # outputs gathered article data

editionYear = 1996
editionDayData = list()
editionYearLinkCache = NPRPageParser.LoadJSONFile("NPRArticleData/" + str(editionYear) + "-NPRArticleLinkCache.json")
for month, daylinks in editionYearLinkCache.items():
    for url in daylinks:
        nprSpotifySearch = NPRSpotifySearch()
        nprPlaylistCreator = NPRPlaylistCreator()
        requestedHTML = NPRPageParser.RequestURL(url)
        selectedHTML = NPRPageParser.SelectStory(requestedHTML.text) # select the returned HTML
        editionDayData.append(NPRPageParser.GetEditionData(url, selectedHTML)) # get various article data from this day
        trackResults = list()
        for item in selectedHTML.xpath('.//div[@id="story-list"]/*'):
            if item.attrib['class'] == 'rundown-segment':
                editionDayData.append(NPRPageParser.GetArticleInfo(item))
            elif item.attrib['class'] == 'music-interlude responsive-rundown':
                for track in item.xpath('.//div[@class="song-meta-wrap"]'):
                    trackname = NPRPageParser.GetInterludeSongName(track)
                    artistNames = NPRPageParser.GetInterludeArtistNames(track)
                    editionDayData.append(nprSpotifySearch.SearchSpotify(trackname, artistNames))
        nprPlaylistCreator.AddCoverArtToPlaylist(editionDayData)
        nprPlaylistCreator.AddTracksToPlaylist(editionDayData)
        nprPlaylistCreator.UpdatePlaylistDescription(editionDayData)
        # print(json.dumps(editionDayData, indent=4, sort_keys=True, ensure_ascii=False))