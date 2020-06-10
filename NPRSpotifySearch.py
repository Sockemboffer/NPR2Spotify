from ResponsesHandle import ResponseHandle
# todo: re-check parsed page for missing tracks to research
    # todo: check if playlist exsists
    # todo: notify when previously not found track is found
# todo: organize queries
class NPRSpotifySearch:

    def __init__(self):
        self.query = ""
        self.responseList = list()
        self.originalTrack = ""
        self.originalArtists = list()
        self.track = ""
        self.artists = list()
        self.ResponseHandle = ResponseHandle()

    def GetTrackURIs(self, artistList):
        # building uri list to use later in playlist fill-up
        for dic in artistList:
            if "Interlude Artist" in dic:
                self.originalArtists = dic.get("Interlude Artist")
                self.artists = dic.get("Interlude Artist")
            if "Interlude Song" in dic:
                self.originalTrack = dic.get("Interlude Song")
                self.track = dic.get("Interlude Song")
            # todo: call to NPRSpotifySearch
            self.SearchExplicitTrackAndArtist(self.track, self.artists[0])
            self.RemoveBrackets(self.track)
            self.SearchExplicitTrackAndArtist(self.track, self.artists[0])
            self.RemoveParenthesis(self.track)
            self.SearchExplicitTrackAndArtist(self.track, self.artists[0])
            self.RemoveCommonPhrases(self.track)
            self.SearchExplicitTrackAndArtist(self.track, self.artists[0])
            self.SearchImplicitTrackExplicitArtist(self.track, self.artists[0])
            self.SearchImplicitTrackNoArtist(self.track)
            self.CompareResponses(self.responseList, self.originalTrack, self.originalArtists[0])
        return artistURIs

    def RemoveBrackets(self, track):
        return track.translate({ord(i): None for i in '[]'})
    
    def RemoveParenthesis(self, track):
        return trackNoBrackets.translate({ord(i): None for i in '()'})

    def RemoveCommonPhrases(self, track):
        stopwords = ['feat.','original','edit','featuring','feature']
        result  = [word for word in track if word.lower() not in stopwords]
        return ' '.join(result)

    def SearchExplicitTrackAndArtist(self, track, artists):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=1".format(parse.quote('track:' + '"' + track + '"' + ' ' + 'artist:"' + artists + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.ResponseHandle.HandleRespone(response)
        self.responseList.append(response.json())
    
    def SearchImplicitTrackExplicitArtist(self, track, artists):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=1".format(parse.quote('"' + track + '"' + ' ' + 'artist:"' + artists + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.ResponseHandle.HandleRespone(response)
        self.responseList.append(response.json())
    
    def SearchImplicitTrackNoArtist(self, track):
        query = "https://api.spotify.com/v1/search?q={}&type=track&market=US&limit=1".format(parse.quote('"' + track + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.ResponseHandle.HandleRespone(response)
        self.responseList.append(response.json())

    def CompareResponses(self, responseList, originalTrack, originalArtist):
        numberOfResponses = len(responseList)
        for response in responseList:
            missedCount = 0
            foundCount = 0
            if response["tracks"]["total"] != 0:
                #thing
                foundCount+=1
            else:
                missedCount+=1
            if (foundCount == numberOfResponses) or (missedCount == numberOfResponses)
                return 0

        # if hit total 0
            # remove response from list
            # missed response +1 (increase missed confidence or maybe lower found confidence?)
            # if response list 0
                # missed track (high confidence)
        # if hit and hit is exact match to original
            # How many exact matches across all responses
                # if 2 or more
                    # found track (high confidence)
                # else 1
                    # found track (medium confidence)
        # if hit and not exact match
            # How many hits match the original artist
                # if 2 or more
                    # found track (high confidence)
                # elif 1
                    # found track (medium confidence)
                # else
                    # missing track (medium confidence)

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