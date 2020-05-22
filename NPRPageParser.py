from lxml import html
import requests
import json
from string import punctuation
from parsel import Selector
import datetime

# note: earlist npr page with songs (it seems) Wednesday, July 26, 2000
# note: https://www.npr.org/programs/morning-edition/2000/07/26/12988271/?showDate=2000-07-26

# todo: generate valid npr page urls for morning and weekend edition
# todo: create timer to gate page scanning
# todo: Organize into folders in some way

nprURL = ""

def RequestURL(URL):
    request = requests.get(URL)
    return request.text

def NPRStoryParser(nprURL):
    selector = Selector(text=RequestURL(nprURL))
    with open('NPRPageParser.json', 'w', encoding='utf-8') as json_file:
        newPageData = list()
        newPageData.append(PageRequest(selector))
        print('- Page Info')
        for item in selector.xpath('.//div[@id="story-list"]/*'):
            if item.attrib['class'] == 'rundown-segment':
                newArticleData = ArticleRequest(item)
                newPageData.append(newArticleData)
            elif item.attrib['class'] == 'music-interlude responsive-rundown':
                newInterludeInfo = list()
                for artist in item.xpath('.//div[@class="song-meta-wrap"]'):
                    newInterludeInfo.append(InterludeRequest(artist))
                newPageData.append(newInterludeInfo)
        json.dump(newPageData, json_file, ensure_ascii=False, indent=4)
    print('- Done')

def PageRequest(pageSelector):
    pageData = dict()
    pageData['Page Link'] = nprURL
    pageData['Edition'] = pageSelector.xpath('//header[@class="contentheader contentheader--one"]//h1/b/text()').get()
    pageData['Date Text'] = pageSelector.xpath('//div[@id="episode-core"]//nav[@class="program-nav program-nav--one"]//time/b/text()[2]').get().strip()
    pageData['Date Numbered'] = pageSelector.xpath('//div[@id="episode-core"]//nav[@class="program-nav program-nav--one"]//time/@datetime').get()
    pageData['Day'] = pageSelector.xpath('//div[@id="episode-core"]//nav[@class="program-nav program-nav--one"]//time/b[@class="date"]//b[@class="day"]/text()').get().strip(' ,')
    dt = str(datetime.datetime.now().__format__("%Y-%m-%d %H:%M:%S"))
    pageData['Scanned Date'] = dt
    pageData['Playlist Link'] = None
    pageData['Playlist URI'] = None
    return pageData

def ArticleByLineRequest(article):
    return article.xpath('.//span[@class="byline byline--inline"]/text()').getall()
                
def ArticleRequest(article):
    articleData = dict()
    articleData['Article'] = article.xpath('./div/h3[@class="rundown-segment__title"]/a/text()').get()
    articleData['Link'] = article.xpath('./div/h3[@class="rundown-segment__title"]/a/@href').get()
    articleData['Slug'] = article.xpath('./div/h4[@class="rundown-segment__slug"]/a/text()').get()
    articleData['By'] = ArticleByLineRequest(article)
    print('-- Article Info')
    return articleData

def InterludeRequest(interlude):
    artistData = dict()
    artistData['Interlude Artist'] = interlude.xpath('.//span[@class="song-meta-artist"]/text()').get()
    artistData['Interlude Song']  = interlude.xpath('.//span[@class="song-meta-title"]/text()').get()
    artistData['Spotify URI'] = None
    artistData['Last Checked'] = None
    print('---- Song Info')
    return artistData

nprURL = "https://www.npr.org/programs/weekend-edition-sunday/2020/05/10/853414822/"
NPRStoryParser(nprURL)