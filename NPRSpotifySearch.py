from ResponsesHandle import ResponseHandle
# todo: re-check parsed page for missing tracks to research
    # todo: check if playlist exsists
    # todo: notify when previously not found track is found
# todo: organize queries
class NPRSpotifySearch:

    def __init__(self):
        self.nprTrackName = ""
        self.nprArtistsName = list()
        self.track = ""
        self.artists = list()
        self.ResponseHandle = ResponseHandle()

    def GetTrackURIs(self, artistList):
        # building uri list to use later in playlist fill-up
        for dic in artistList:
            if "Interlude Artist" in dic:
                self.nprArtistsName = dic.get("Interlude Artist")
                self.artists = dic.get("Interlude Artist")
            if "Interlude Song" in dic:
                self.nprTrackName = dic.get("Interlude Song")
                self.track = dic.get("Interlude Song")
            # get spotify responses and convert to json
            responsesJSON = list()
            responsesJSON.append(self.SearchExplicitTrackAndArtist(self.track, self.artists[0]))
            self.RemoveBrackets(self.track)
            responsesJSON.append(self.SearchExplicitTrackAndArtist(self.track, self.artists[0]))
            self.RemoveParenthesis(self.track)
            responsesJSON.append(self.SearchExplicitTrackAndArtist(self.track, self.artists[0]))
            self.RemoveCommonPhrases(self.track)
            responsesJSON.append(self.SearchExplicitTrackAndArtist(self.track, self.artists[0]))
            responsesJSON.append(self.SearchImplicitTrackExplicitArtist(self.track, self.artists[0]))
            responsesJSON.append(self.SearchImplicitTrackNoArtist(self.track))
            # parse responses
            parsedResponses = list()
            for response in responsesJSON:
                parsedResponses.append(self.ParseResponseJSON(response))
            # compare responses

        return artistURIs

    def RemoveBrackets(self, track):
        return track.translate({ord(i): None for i in '[]'})
    
    def RemoveParenthesis(self, track):
        return trackNoBrackets.translate({ord(i): None for i in '()'})

    def RemoveCommonPhrases(self, track):
        stopwords = ['feat.', 'feat', 'original', 'edit', 'featuring', 'feature']
        result  = [word for word in track if word.lower() not in stopwords]
        return ' '.join(result)

    def SearchExplicitTrackAndArtist(self, track, artists):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=1".format(parse.quote('track:' + '"' + track + '"' + ' ' + 'artist:"' + artists + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.ResponseHandle.HandleRespone(response)
        return response.json()
    
    def SearchImplicitTrackExplicitArtist(self, track, artists):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=1".format(parse.quote('"' + track + '"' + ' ' + 'artist:"' + artists + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.ResponseHandle.HandleRespone(response)
        return response.json()
    
    def SearchImplicitTrackNoArtist(self, track):
        query = "https://api.spotify.com/v1/search?q={}&type=track&market=US&limit=1".format(parse.quote('"' + track + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.ResponseHandle.HandleRespone(response)
        return response.json()

    def ParseResponseJSON(self, responseJSON):
        if responseJSON["tracks"]["total"] == 0:
            parsed["Track Name"] = None
            parsed["Track URI"] = None
            parsed["Artist Name"] = None
            return parsed
        else:
            parsed["Track Name"] = responseJSON["tracks"]["items"][0]["name"]
            parsed["Track URI"] = responseJSON["tracks"]["items"][0]["uri"]
            parsed["Artist Name"] = responseJSON["tracks"]["items"][0]["artists"][0]["name"]
            return parsed

    def CompareParsedResponses(self, parsedResponsesJSON)
        parsedResponsesCount = len(ParseResponseJSON)
        foundScore = 0.0
        noHit = list()
        hitExactMatch = list()
        hitPartialMatch = list()
        hitButNoMatch = list()
        for response in parsedResponsesJSON:
            if response["Track Name"] == None:
                # no track found at all from spotify
                noHit.append(response)
                foundScore+=(-2.0)
            elif (response["Track Name"] == self.nprTrackName) and (response["Artist Name"] == self.nprArtistsName):
                # hit exact match found to what npr had
                hitExactMatch.append(response)
                foundScore+=1.0
            elif response["Artist Name"] == self.originalArtists:
                # hit but song name may be slightly different than what npr has
                hitPartialMatch.append(response)
                foundScore+=0.5
            else:
                # hit but matches neither the track or artist exactly
                hitButNoMatch.append(response)
                foundScore+=(-1.0)
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
        # if response_json["tracks"]["total"] == 0:
        #     if (response_json["tracks"]["total"] == 0):
        #         print(trackNoBracketsAndBraces + ' ' + 'by: None')
        #     else:
        #         print("<!check!> " + response_json["tracks"]["items"][0]["name"] + " by: " + response_json["tracks"]["items"][0]["artists"][0]["name"] + " <=?=> " + trackNoBracketsAndBraces + " by: " + artists[0])
        # if response_json["tracks"]["total"] == 0:
        #     if (response_json["tracks"]["total"] == 0):
        #         print(self.result + ' ' + 'by: None')
        #     else:
        #         print("<!check!> " + response_json["tracks"]["items"][0]["name"] + " by: " + response_json["tracks"]["items"][0]["artists"][0]["name"] + " <=?=> " + self.result+ " by: " + artists[0])