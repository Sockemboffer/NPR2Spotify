from lxml import html
import requests
import json
from string import punctuation
from parsel import Selector
import datetime
import re
# note: earlist npr page with songs (it seems) Wednesday, July 26, 2000
# note: https://www.npr.org/programs/morning-edition/2000/07/26/12988271/?showDate=2000-07-26
# todo: generate valid npr page urls for morning and weekend edition
# todo: create timer to gate page scanning
# todo: Organize into folders in some way
# todo: create json file name as playlist name?
# todo: construct playlist name here rather than PlaylistCreator script

class NPRPageParser:
    def __init__(self):
        self.nprurl = "https://www.npr.org/programs/weekend-edition-sunday/2020/05/10/853414822/"

    # Generate a valid date to insert into an npr link
    #def CreateURLDate(self):

    # Request the html at link address
    def RequestURL(self):
        request = requests.get(self.nprurl)
        return request.text

    # Grab the Story block of an npr page to parse article and interulde data into a json file
    def StoryParser(self, pagehtml):
        selector = Selector(text=pagehtml)
        with open('NPRPageParser.json', 'w', encoding='utf-8') as json_file:
            newPageData = list()
            newPageData.append(self.PageRequest(selector))
            print('- Page Info')
            for item in selector.xpath('.//div[@id="story-list"]/*'):
                if item.attrib['class'] == 'rundown-segment':
                    newArticleData = self.ArticleRequest(item)
                    newPageData.append(newArticleData)
                elif item.attrib['class'] == 'music-interlude responsive-rundown':
                    newInterludeInfo = list()
                    for artist in item.xpath('.//div[@class="song-meta-wrap"]'):
                        newInterludeInfo.append(self.InterludeRequest(artist))
                    newPageData.append(newInterludeInfo)
            json.dump(newPageData, json_file, ensure_ascii=False, indent=4)
        print('- Done')

    # Grab various info about the whole NPR article for that date
    def PageRequest(self, pageSelector):
        pageData = dict()
        pageData['Page Link'] = self.nprurl
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
        print(pageData['Playlist Name'])
        pageData['Playlist Link'] = None
        pageData['Playlist URI'] = None
        return pageData

    # Grab multiple by-line authors
    def ArticleByLineRequest(self, article):
        return article.xpath('.//span[@class="byline byline--inline"]/text()').getall()

    # Grab data about each article         
    def ArticleRequest(self, article):
        articleData = dict()
        articleData['Article'] = article.xpath('./div/h3[@class="rundown-segment__title"]/a/text()').get()
        articleData['Link'] = article.xpath('./div/h3[@class="rundown-segment__title"]/a/@href').get()
        articleData['Slug'] = article.xpath('./div/h4[@class="rundown-segment__slug"]/a/text()').get()
        articleData['By'] = self.ArticleByLineRequest(article)
        print('-- Article Info')
        return articleData

    # Grab data about each interlude
    def InterludeRequest(self, interlude):
        artistData = dict()
        # gross trim leading/trailing then duplicate spaces also splitting artists if "&" or "," found into list
        artistData['Interlude Artist'] = re.split('[&,]', re.sub(" +", " ", re.sub("^\s+|\s+$", "", interlude.xpath('.//span[@class="song-meta-artist"]/text()').get())))
        artistData['Interlude Song']  = re.sub(" +", " ", re.sub("^\s+|\s+$", "", interlude.xpath('.//span[@class="song-meta-title"]/text()').get()))
        artistData['Spotify URI'] = None
        artistData['Last Checked'] = None
        print('---- Song Info')
        return artistData

    # Load json file data, check to ensure it's valid first
    def get_json_data(self, filename):
        with open(filename, "r", encoding='utf-8') as json_file:
            try:
                return json.load(json_file)
            except ValueError as e:
                print('invalid json: %s' % e)
                return None # or: raise

    # Insert(?) new data into json file
    def update_json_data(self, filename, jsonData):
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(jsonData, json_file, ensure_ascii=False, indent=4)
            json_file.close()

pageParser = NPRPageParser() # Instance of this class
pageHTML = pageParser.RequestURL()
pageParser.StoryParser(pageHTML)