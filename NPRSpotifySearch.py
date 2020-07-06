from ResponsesHandle import ResponseException
from urllib import parse
import requests
from secrets import spotify_user_id, spotipyUserToken
import json
from collections import Counter
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
                self.nprArtistsName = dic["Interlude Artist"][0]
                self.artists = dic.get("Interlude Artist")
            if "Interlude Song" in dic:
                self.nprTrackName = dic.get("Interlude Song")
                self.track = dic.get("Interlude Song")
            # get spotify responses and convert to json
            responsesJSON = list()
            responsesJSON.append(self.SearchExplicitTrackAndArtist(self.track, self.artists[0]))
            self.track = self.RemoveBrackets(self.track)
            responsesJSON.append(self.SearchExplicitTrackAndArtist(self.track, self.artists[0]))
            self.track = self.RemoveParenthesis(self.track)
            responsesJSON.append(self.SearchExplicitTrackAndArtist(self.track, self.artists[0]))
            self.track = self.RemoveCommonPhrases(self.track)
            responsesJSON.append(self.SearchExplicitTrackAndArtist(self.track, self.artists[0]))
            responsesJSON.append(self.SearchImplicitTrackExplicitArtist(self.track, self.artists[0]))
            responsesJSON.append(self.SearchImplicitTrackNoArtist(self.track))
            responsesJSON.append(self.SearchExplicitTrackAndArtist(self.nprTrackName.split("(")[0], self.artists[0]))
            responsesJSON.append(self.SearchExplicitTrackAndArtist(self.nprTrackName.split("[")[0], self.artists[0]))
            # hail marry
            responsesJSON.append(self.SearchImplicitTrackNoArtist(self.nprTrackName))
            # parse responses
            # should I pass a list to the function or keep the list out here?
            parsedResponses = list()
            for response in responsesJSON:
                parsedResponses.append(self.ParseResponseJSON(response))
            # Categorize responses
            self.IdentifyResponses(parsedResponses)
            # compare responses
            choosenResponseForTracks.append(self.CompareResponses(parsedResponses))
            #print(choosenResponseForTracks)
        return choosenResponseForTracks

    def RemoveBrackets(self, track):
        newTrack = track.translate({ord(i): None for i in '[]'})
        print("!! Removed brackets: " + newTrack)
        return newTrack
    
    def RemoveParenthesis(self, track):
        newTrack = track.translate({ord(i): None for i in '()'})
        print("!! Removed parenthesis: " + newTrack)
        return newTrack

    def RemoveCommonPhrases(self, track):
        stop_words = ['feat.', 'feat', 'original', 'edit', 'featuring', 'feature']
        stopwords_dict = Counter(stop_words)
        result = ' '.join([word for word in track.split() if word not in stopwords_dict])
        print("!! Removed common Phrases: " + result)
        return result

    def SearchExplicitTrackAndArtist(self, track, artist):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=1".format(parse.quote('track:' + '"' + track + '"' + ' ' + 'artist:"' + artist + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        #print(json.dumps(response.json(), ensure_ascii=False, indent=4))
        # check for valid response status
        if response.status_code != 200:
            raise ResponseException(response.status_code)
        print(">> Explicit Track and Artist search finished.")
        return response.json()
    
    def SearchImplicitTrackExplicitArtist(self, track, artist):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=1".format(parse.quote('"' + track + '"' + ' ' + 'artist:"' + artist + '"'))
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
            parsed["Found Track Name"] = None
            parsed["NPR Artist Name"] = self.nprArtistsName
            parsed["Found Artist Name"] = None
            parsed["Found Track URI"] = None
            parsed["Found Match Type"] = ""
            return parsed
        else:
            parsed["NPR Track Name"] = self.nprTrackName
            parsed["Found Track Name"] = responseJSON["tracks"]["items"][0]["name"]
            parsed["NPR Artist Name"] = self.nprArtistsName
            parsed["Found Artist Name"] = responseJSON["tracks"]["items"][0]["artists"][0]["name"]
            parsed["Found Track URI"] = responseJSON["tracks"]["items"][0]["uri"]
            parsed["Found Match Type"] = ""
            return parsed
    # ==============================================double check compared responses
    def IdentifyResponses(self, parsedResponsesJSON):
        for response in parsedResponsesJSON:
            if response["Found Track Name"] == None:
                # no track found at all from spotify (Not sure if None is used when no track)
                response["Found Match Type"] = "NoHit"
            elif response["Found Track Name"] == self.nprTrackName and response["Found Artist Name"] == self.nprArtistsName:
                # hit exact match found to what npr had
                # should I use global var or key when comparing to original?
                response["Found Match Type"] = "HitExactMatch"
            elif response["Found Track Name"] != self.nprTrackName and response["Found Artist Name"] == self.nprArtistsName:
                # hit but track name may be slightly different than what npr has so we compare artist name hoping for an exact
                response["Found Match Type"] = "HitPartialMatch"
            else:
                # hit but matches neither the track or artist exactly as npr had it
                response["Found Match Type"] = "HitButNoMatch"
            #print(json.dumps(response, ensure_ascii=False, indent=4))
        return parsedResponsesJSON
    # Isn't returning correctly created list ####################################################
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
        # print("++++++++ No Hit")
        # print(noHit)
        # print("++++++++ Hit Exact Match")
        # print(hitExactMatch)
        # print("++++++++ Hit Partial Match")
        # print(hitPartialMatch)
        # print("++++++++ Hit But No Match")
        # print(hitButNoMatch)
        # Not sure how best to "grade" my results
        print(len(noHit))
        print(len(parsedResponsesList))
        if len(noHit) == len(parsedResponsesList):
            return noHit
        elif len(hitExactMatch) > 0:
            return hitExactMatch
        elif len(hitPartialMatch) >= len(hitButNoMatch):
            return hitPartialMatch
        else:
            return hitButNoMatch