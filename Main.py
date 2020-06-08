from NPRPageParser import NPRPageParser

pageParser = NPRPageParser() # Instance of page parser
pageParser.nprurl = "https://www.npr.org/programs/weekend-edition-sunday/2020/05/10/853414822/" # turn into create url function later
pageHTML = pageParser.RequestURL()
pageData = pageParser.StoryParser(pageHTML)
#pageParser.UpdateJsonDictData("NPRPageParser.json", pageData, "Nassau", "Long Arc")