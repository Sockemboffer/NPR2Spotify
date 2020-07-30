class NPRPageData:
    def __init__(self):
        self.PageLink = "Page Link"
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