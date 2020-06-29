from ResponsesHandle import ResponseException
from urllib import parse
import requests
from secrets import spotify_user_id, spotipyUserToken
# todo: re-check parsed page for missing tracks to research
    # todo: check if playlist exsists
    # todo: notify when previously not found track is found
class NPRSpotifySearch:

    def __init__(self):
        self.nprTrackName = ""
        self.nprArtistsName = list()
        self.track = ""
        self.artists = list()

    # GetTrackURIs transforms the data I send in, is that confusing to a user they get back different data?
    def GetTrackURIs(self, artistList):
        # building uri list to use later in playlist fill-up
        choosenResponseForTracks = list()
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
            # Categorize responses
            self.IdentifyResponses(parsedResponses)
            # compare responses
            choosenResponseForTracks.append(self.CompareResponses(parsedResponses))
        return choosenResponseForTracks

    def RemoveBrackets(self, track):
        return track.translate({ord(i): None for i in '[]'})
    
    def RemoveParenthesis(self, track):
        return track.translate({ord(i): None for i in '()'})

    def RemoveCommonPhrases(self, track):
        stopwords = ['feat.', 'feat', 'original', 'edit', 'featuring', 'feature']
        result  = [word for word in track if word.lower() not in stopwords]
        return ' '.join(result)

    def SearchExplicitTrackAndArtist(self, track, artists):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=1".format(parse.quote('track:' + '"' + track + '"' + ' ' + 'artist:"' + artists + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # check for valid response status
        if response.status_code != 200:
            raise ResponseException(response.status_code)
        print(">> Explicit Track and Artist search finished.")
        return response.json()
    
    def SearchImplicitTrackExplicitArtist(self, track, artists):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=1".format(parse.quote('"' + track + '"' + ' ' + 'artist:"' + artists + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # check for valid response status
        if response.status_code != 200:
            raise ResponseException(response.status_code)
        print(">> Implicit Track and Explicit Artist search finished.")
        return response.json()
    
    def SearchImplicitTrackNoArtist(self, track):
        query = "https://api.spotify.com/v1/search?q={}&type=track&market=US&limit=1".format(parse.quote('"' + track + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # check for valid response status
        if response.status_code != 200:
            raise ResponseException(response.status_code)
        print(">> Implicit Track and No Artist search finished.")
        return response.json()

    def ParseResponseJSON(self, responseJSON):
        parsed = dict()
        if responseJSON["tracks"]["total"] == 0:
            # confusing/risky to rely that the correct nprtrackname/artist assigning here?
            parsed["NPR Track Name"] = self.nprTrackName
            parsed["NPR Artist Name"] = self.nprArtistsName
            parsed["Found Track Name"] = None
            parsed["Found Track URI"] = None
            parsed["Found Artist Name"] = None
            parsed["Found Match Type"] = ""
            return parsed
        else:
            parsed["NPR Track Name"] = self.nprTrackName
            parsed["NPR Artist Name"] = self.nprArtistsName
            parsed["Found Track Name"] = responseJSON["tracks"]["items"][0]["name"]
            parsed["Found Track URI"] = responseJSON["tracks"]["items"][0]["uri"]
            parsed["Found Artist Name"] = responseJSON["tracks"]["items"][0]["artists"][0]["name"]
            parsed["Found Match Type"] = ""
            return parsed

    def IdentifyResponses(self, parsedResponsesJSON):
        for response in parsedResponsesJSON:
            if response["Found Track Name"] == None:
                # no track found at all from spotify (Not sure if None is used when no track)
                response["Found Match Type"] = "NoHit"
            elif (response["Found Track Name"] == self.nprTrackName) and (response["Found Artist Name"] == self.nprArtistsName):
                # hit exact match found to what npr had
                # should I use global var or key when comparing to original?
                response["Found Match Type"] = "HitExactMatch"
            elif response["Found Artist Name"] == self.nprArtistsName:
                # hit but track name may be slightly different than what npr has so we compare artist name hoping for an exact
                response["Found Match Type"] = "HitPartialMatch"
            else:
                # hit but matches neither the track or artist exactly
                response["Found Match Type"] = "HitButNoMatch"
        return parsedResponsesJSON

    def CompareResponses(self, parsedResponsesList):
        noHit = list()
        hitExactMatch = list()
        hitPartialMatch = list()
        hitButNoMatch = list()
        for response in parsedResponsesList:
            if response["Found Match Type"] == "NoHit":
                noHit.append(response)
            elif response["Found Match Type"] == "HitExactMatch":
                hitExactMatch.append(response)
            elif response["Found Match Type"] ==  "HitPartialMatch":
                hitPartialMatch.append(response)
            else:
                hitButNoMatch.append(response)
        # Not sure how best to "grade" my results
        if (len(noHit) == len(parsedResponsesList)):
            return noHit
        elif (len(hitExactMatch) > 0):
            return hitExactMatch
        elif (len(hitPartialMatch) >= len(hitButNoMatch)):
            return hitPartialMatch
        else:
            return hitButNoMatch