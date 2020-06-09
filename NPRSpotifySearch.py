# todo: re-check parsed page for missing tracks to research
    # todo: check if playlist exsists
    # todo: notify when previously not found track is found
# todo: organize queries
class NPRSpotifySearch:
        def __init__(self):
            self.query = ""
            self.responseList = list()

    def GetSpotifyURIs(self, artistList):
        # building uri list to use later in playlist fill-up
        for dic in artistList:
            if "Interlude Artist" in dic:
                artists = dic.get("Interlude Artist")
            if "Interlude Song" in dic:
                track = dic.get("Interlude Song")
        # todo: call to NPRSpotifySearch
        return artistURIs

    # Create several ways to chop up and search for target track
    # Initial search raw track and 1st artist name
    def searchTypeTrackTypeArtist(self, track, artists):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=5".format(parse.quote('track:' + '"' + track + '"' + ' ' + 'artist:"' + artists[0] + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.responseList.append(response.json())
        #print(track + " by: " + artists[0])
    
    def searchTrackTypeArtist(self, track, artists):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=5".format(parse.quote('"' + track + '"' + ' ' + 'artist:"' + artists[0] + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.responseList.append(response.json())
        #print(trackNoBracketsAndBraces + ' ' + 'by: ' + artists[0])
    
    def searchTypeTrack(self, track):
        query = "https://api.spotify.com/v1/search?q={}&type=track&market=US&limit=5".format(parse.quote('"' + trackNoBracketsAndBraces + '"'))
        print(trackNoBracketsAndBraces + ' ' + 'by: None')
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.responseList.append(response.json())
    
    def searchTrackArtist(self, track, artist):
        # strip words from songs like featuring, edit, original, etc. + search WITHOUT type artist
        query = "https://api.spotify.com/v1/search?q={}&type=track&market=US&limit=5".format(parse.quote('"' + self.result + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.responseList.append(response.json())

    def removeBrackets(self, track):
        # strip any [] from track names
        return track.translate({ord(i): None for i in '[]'})
    
    def removeParenthesies(self, track):
        # strip any () from track name
        return trackNoBrackets.translate({ord(i): None for i in '()'})

    def stripCommonPhrases(self, track):
        # strip common phrases found in track names
        stopwords = ['feat.','original','edit','featuring','feature']
        result  = [word for word in track if word.lower() not in stopwords]
        return ' '.join(result)

    def compareResponses(self, responseList):
        # When no artist used, double check found track's artist matches npr page artist
        if response_json["tracks"]["total"] == 0:
            if (response_json["tracks"]["total"] == 0):
                print(trackNoBracketsAndBraces + ' ' + 'by: None')
            else:
                print("<!check!> " + response_json["tracks"]["items"][0]["name"] + " by: " + response_json["tracks"]["items"][0]["artists"][0]["name"] + " <=?=> " + trackNoBracketsAndBraces + " by: " + artists[0])
        # When no artist used, double check found track's artist matches npr page artist
        if response_json["tracks"]["total"] == 0:
            if (response_json["tracks"]["total"] == 0):
                print(self.result + ' ' + 'by: None')
            else:
                print("<!check!> " + response_json["tracks"]["items"][0]["name"] + " by: " + response_json["tracks"]["items"][0]["artists"][0]["name"] + " <=?=> " + self.result+ " by: " + artists[0])

    # Function to print found or missing status (todo: decouple from json file update)