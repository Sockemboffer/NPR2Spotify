# Includes
from lxml import html
import requests
import json
from parsel import Selector
import datetime
#import pprint
# Child itteration setup

# NPR Page String Data
pageLink = ""
pageDateText = ""
pageDateNumbered = ""
pageDay = ""
pageLastScannedDate = ""
# NPR Article Data
articleTitle = ""
articleLink = ""
articleSlug = ""
articleByLine = ""
# NPR Segment Data
segmentArtistSong = ""
#NPR Story List Data
storyList = ""
# NPR Request Data
nprURL = "https://www.npr.org/programs/morning-edition/2018/10/29/661661069/morning-edition-for-october-29-2018"
# Dictionary Layout
NPRPage = {                 'Page Link' :               nprURL,
                            'Page Date Text' :          pageDateText,
                            'Page Date Numbered' :      pageDateNumbered,
                            'Page Day' :                pageDay,
                            'Page Last Scanned Date' :  pageLastScannedDate}
NPRArticle = {              'Article Title' :           articleTitle,
                            'Article Link' :            articleLink,
                            'Article Slug' :            articleSlug,
                            'Article Byline' :          articleByLine}
NPRSegmentArtistSong = {    'Segment Artist & Song' :   segmentArtistSong}
NPRArticlesAndMusic = {}
def RequestNPRPage(linkToPage):
    request = requests.get(linkToPage)
    return request.text
def SelectNPRPage(pageToSelectOn):
    selector = Selector(text=pageToSelectOn)
    NPRPage['Page Link'] = nprURL
    NPRPage['Page Date Text'] = selector.xpath('//div[@id="episode-core"]//nav[@class="program-nav program-nav--one"]//time/b/text()[2]').get().strip()
    NPRPage['Page Date Numbered'] = selector.xpath('//div[@id="episode-core"]//nav[@class="program-nav program-nav--one"]//time/@datetime').get()
    NPRPage['Page Day'] = selector.xpath('//div[@id="episode-core"]//nav[@class="program-nav program-nav--one"]//time/b[@class="date"]//b[@class="day"]/text()').get()
    NPRPage['Page Last Scanned Date'] = str(datetime.datetime.now())
def SegmentByLineRequest(byLineSelector):
    byLineSelector.xpath('.//span[@class="byline byline--inline"]/text()').getall()
def SongMetaRequest(songMetaSelector):
    for songMetaItem in songMetaSelector.xpath('.//*/div[@class="song-meta-wrap"]'):
        NPRSegmentArtistSong['Segment Artist & Song'] = songMetaItem.xpath('./span[@class="song-meta-artist"]/text()').get() + ', ' + songMetaItem.xpath('./span[@class="song-meta-title"]/text()').get()
        with open('NPRMorningEdition.txt', 'a') as json_file:
            json.dump(NPRSegmentArtistSong, json_file, ensure_ascii=False, indent=2, sort_keys=True)
def ProcesNPRStoryList(pageToSelectOn):
    SelectNPRPage(pageToSelectOn)
    with open('NPRMorningEdition.txt', 'w') as json_file:
        json.dump(NPRPage, json_file, ensure_ascii=False, indent=2, sort_keys=True)
    selector = Selector(text=pageToSelectOn)
    count = selector.xpath('count(//div[@id="story-list"]/*)')
    for itemSelector in selector.xpath('//div[@id="story-list"]/*'):
        if itemSelector.attrib['class'] == 'rundown-segment':
            print('=====found rundown=====')
            NPRArticle['Article Title'] = itemSelector.xpath('./div/h3[@class="rundown-segment__title"]/a/text()').get()
            NPRArticle['Article Link'] = itemSelector.xpath('./div/h3[@class="rundown-segment__title"]/a/@href').get()
            NPRArticle['Article Slug'] = itemSelector.xpath('./div/h4[@class="rundown-segment__slug"]/a/text()').get()
            NPRArticle['Article Byline'] = SegmentByLineRequest(itemSelector)
            with open('NPRMorningEdition.txt', 'a') as json_file:
                json.dump(NPRArticle, json_file, ensure_ascii=False, indent=2, sort_keys=True)
        elif itemSelector.attrib['class'] == 'music-interlude responsive-rundown':
            print('^^^^^found music interlude^^^^^')
            SongMetaRequest(itemSelector)
    return count
# Function Calling
ProcesNPRStoryList(RequestNPRPage(nprURL))

'''
person_dict = {"name": "Bob", "languages": ["English", "Fench"], "married": True, "age": 32}

with open('person.txt', 'w') as json_file:
  json.dump(person_dict, json_file)
'''
'''
Global Page Data //body[@id='news']//main
    Page Link
    Page Date
    Page Text Date
    Page Text Day
    Page Last Scanned Date

Article Segement Data //div[@id='story-list']
    Segement Title
    Segement Link
    Segement Slug(category:politics, health, etc.)
    Segement Byline(author(s))

    Segement SongArtist(s)
    Segement SongTitle(s)


#all_elements = Selector(text=selector)
h4_elements = selector.css('h4')
order = lambda e: int(float(e.xpath('count(preceding::*) \ + count(ancestor::*)').extract+first()))
boundaries = [order(h) for h in h4_elements]
buckets = []

def ProcessStoryLists(string):
    for pos, e in sorted((order(e), e) for e in all_elements):
        if pos in boundaries:
            bucket = []
            buckets.append(bucket)
        bucket.append((e.xpath('name()').extract_first(), 
                        e.xpath('string()').extract_first()))
    buckets

ProcessStoryLists(tree)

def ProcessStoryLists(MorningShowPage) v1.0 data layout
    for article in story-list
        store article details
        while sibling is music-interlood
            store music details

getMorningEditionDayLink = pageLink
getPageDate = tree.xpath('/html/body/main/div[2]/section/div[2]/div/nav/div/time/@datetime')
getPageTextDate = tree.xpath('/html/body/main/div[2]/section/div[2]/div/nav/div/time/b/text()')
getPageTextDay = tree.xpath('/html/body/main/div[2]/section/div[2]/div/nav/div/time/b/b/text()')

getSegmentSlug = tree.xpath('//div/h4[@class="rundown-segment__slug"]/a/text()')
getSegmentTitle = tree.xpath('//div/h3[@class="rundown-segment__title"]/a/text()')
getSegmentByLine = tree.xpath('//div/p[@class="byline-container--inline"]/a/span/text()')
getSegmentLink = tree.xpath('//div/h3[@class="rundown-segment__title"]/a/@href')

getSegmentSongMeta = tree.xpath('//div/div[@class="song-meta-wrap"]/span/text()')

print ('Page Link: ', getMorningEditionDayLink)
print ('Date: ', getPageDate)
print ('Text Date: ', getPageTextDate)
print ('Text Day: ', getPageTextDay)
print ('Segment Slug: ', getSegmentSlug)
print ('Segment Title: ', getSegmentTitle)
print ('Segment ByLine: ', getSegmentByLine)
print ('Segment Link: ', getSegmentLink)
print ('Segment SongMeta: ', getSegmentSongMeta)

http fetch request for html page (full or can I snipe section I need?)
    store html (or maybe scan from memory?)

parse stored html per segment
    store npr segment data
        store Show Date
        store segment slug
        store segment title
        store segment byline
        store segment link
        store segement artist's name
        store segment song title
        ...

Format entries to json file(s) 
'''
