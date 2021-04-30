import os
import time
import json
from urllib.parse import urlparse
from NPRPageParser import NPRPageParser
from NPRSpotifySearch import NPRSpotifySearch
from NPRPlaylistCreator import NPRPlaylistCreator

# # # Create a json file for each year of day links (only need to run one time)
# NPRPageParser.NPRArticleLinkCacheCreator(2018) # 1996 - 2020

editionYear = 2003
editionDayData = list()
editionYearLinkCache = NPRPageParser.LoadJSONFile("NPRArticleLinkCache/" + str(editionYear) + "-NPRArticleLinkCache.json")
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
        print(json.dumps(editionDayData, indent=4, sort_keys=True, ensure_ascii=False))
        break
    break