'''
    #author = ""
    #authorList = list()
    #for author in article.xpath('.//p[@class="byline-container--inline"]/*'):
        #author = author.xpath('.//span[@class="byline byline--inline"]/text()').getall()
        #authorList.append(author)

     #= selector.xpath('//body[@id="news"]')
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
