import copy
import json
import requests
from urllib import parse
from collections import Counter
from unidecode import unidecode
from ResponsesHandle import ResponseException
from secrets import spotify_user_id, spotipyUserToken
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class NPRSpotifySearch:

    def __init__(self):
        self.requestSession = requests.Session()
        self.retries = Retry(total=10, backoff_factor=1, status_forcelist=[ 204, 304, 400, 401, 403, 404, 500, 502, 503, 504 ])
        self.requestSession.mount('https://api.spotify.com/', HTTPAdapter(max_retries=self.retries))
        self.nprTrackName = None
        self.nprArtistsName = list()
        self.track = None
        self.artists = list()

    # GetTrackURIs transforms the data I send it, is that confusing to a user they get back different data?
    def GetTrackURIs(self, artistList):
        choosenResponseForTracks = list()
        for dic in artistList:
            if "Interlude Artist" in dic:
                if dic["Interlude Artist"] == None or dic["Interlude Artist"][0] == "":
                    self.nprArtistsName.clear()
                    self.nprArtistsName.append("")
                    self.artists.clear()
                    self.artists.append("")
                else:
                    self.nprArtistsName = dic.get("Interlude Artist")
                    self.artists = dic.get("Interlude Artist")
            if "Interlude Song" in dic:
                if dic["Interlude Song"] == None or dic["Interlude Song"] == "":
                    self.nprTrackName = ""
                    self.track = ""
                else:
                    self.nprTrackName = dic.get("Interlude Song")
                    self.track = dic.get("Interlude Song")
            # get spotify responses and convert to json
            if self.nprTrackName != "":
                responsesJSON = list()
                responsesJSON.append(self.SearchExplicitTrackAndArtist(unidecode(self.track), unidecode(self.artists[0])))
                self.track = self.RemoveBrackets(unidecode(self.track))
                responsesJSON.append(self.SearchExplicitTrackAndArtist(unidecode(self.track), unidecode(self.artists[0])))
                self.track = self.RemoveParenthesis(unidecode(self.track))
                responsesJSON.append(self.SearchExplicitTrackAndArtist(unidecode(self.track), unidecode(self.artists[0])))
                self.track = self.RemoveCommonPhrases(unidecode(self.track))
                responsesJSON.append(self.SearchExplicitTrackAndArtist(unidecode(self.track), unidecode(self.artists[0])))
                responsesJSON.append(self.SearchImplicitTrackExplicitArtist(unidecode(self.track), unidecode(self.artists[0])))
                responsesJSON.append(self.SearchImplicitTrackNoArtist(unidecode(self.track)))
                responsesJSON.append(self.SearchExplicitTrackAndArtist(unidecode(self.nprTrackName.split("(")[0]), unidecode(self.artists[0])))
                responsesJSON.append(self.SearchExplicitTrackAndArtist(unidecode(self.nprTrackName.split("[")[0]), unidecode(self.artists[0])))
                # hail marry
                responsesJSON.append(self.SearchImplicitTrackNoArtist(unidecode(self.nprTrackName)))
                # parse responses
                # should I pass a list to the function or keep the list out here?
                parsedResponses = list()
                for response in responsesJSON:
                    parsedResponses.append(self.ParseResponseJSON(response))
                # Categorize responses
                self.IdentifyResponses(parsedResponses)
                # Very basic weighting on if I accept a track found or not
                choosenResponseForTracks.append(copy.deepcopy(self.CompareResponses(parsedResponses)))
                print("Finished: " + self.nprTrackName + ", by: " + self.nprArtistsName[0])
            else:
                print("> Empty track found.")
        return choosenResponseForTracks

    def RemoveBrackets(self, track):
        newTrack = track.translate({ord(i): None for i in '[]'})
        return newTrack
    
    def RemoveParenthesis(self, track):
        newTrack = track.translate({ord(i): None for i in '()'})
        return newTrack

    def RemoveCommonPhrases(self, track):
        stop_words = ['feat.', 'feat', 'original', 'edit', 'featuring', 'feature']
        stopwords_dict = Counter(stop_words)
        result = ' '.join([word for word in track.split() if word not in stopwords_dict])
        return result

    # Explicit Track or Artist means I define a type encoded in what I send: eg. track:"Smells like teen spirit" artist:"Nirvana"
    # without those it can mean different results, etc.
    def SearchExplicitTrackAndArtist(self, track, artist):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=1".format(parse.quote('track:' + '"' + track + '"' + ' ' + 'artist:"' + artist + '"'))
        response = self.requestSession.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # if response.status_code != 200:
        #     raise ResponseException(response.status_code)
        return response.json()
    
    def SearchImplicitTrackExplicitArtist(self, track, artist):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=1".format(parse.quote('"' + track + '"' + ' ' + 'artist:"' + artist + '"'))
        response = self.requestSession.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # if response.status_code != 200:
        #     raise ResponseException(response.status_code)
        return response.json()
    
    def SearchImplicitTrackNoArtist(self, track):
        query = "https://api.spotify.com/v1/search?q={}&type=track&market=US&limit=1".format(parse.quote('"' + track + '"'))
        response = self.requestSession.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # if response.status_code != 200:
        #     raise ResponseException(response.status_code)
        return response.json()

    # Take the responses and strip out what I want/need for later into my own dictionary
    def ParseResponseJSON(self, responseJSON):
        parsed = dict()
        if responseJSON["tracks"]["total"] == 0:
            # confusing/risky to rely that the correct nprtrackname/artist assigning here?
            parsed["NPR Track Name"] = self.nprTrackName
            parsed["Found Track Name"] = None
            parsed["NPR Artist Name"] = self.nprArtistsName
            parsed["Found Artist Name"] = self.artists
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

    # Doing some simple identifying of my NPR page data against the my parsed response json data
    # to determin how the response "hit" or not
    def IdentifyResponses(self, parsedResponsesJSON):
        identifiedResponses = list()
        for response in parsedResponsesJSON:
            if response["Found Track Name"] is None:
                response["Found Match Type"] = "NoHit"
                identifiedResponses.append(response)
            elif unidecode(str(response["Found Track Name"]).lower()) == unidecode(self.nprTrackName.lower()) and unidecode(str(response["Found Artist Name"])).lower() == unidecode(self.nprArtistsName[0]).lower():
                # hit exact match found to what npr had
                # should I use global var or key when comparing to original?
                response["Found Match Type"] = "HitExactMatch"
                identifiedResponses.append(response)
            elif unidecode(str(response["Found Track Name"]).lower()) != unidecode(self.nprTrackName.lower()) and unidecode(str(response["Found Artist Name"])).lower() == unidecode(self.nprArtistsName[0]).lower():
                # hit but track name may be slightly different than what npr has so we compare artist name hoping for an exact
                # leave up to community to help vet incorrect picks here
                response["Found Match Type"] = "HitPartialMatch"
                identifiedResponses.append(response)
            else:
                # hit but matches neither the track or artist exactly as npr had it
                # stored but we'll count as a missed track later
                response["Found Match Type"] = "HitButNoMatch"
                identifiedResponses.append(response)
        print("-- Responses identified.")
        return identifiedResponses

    # Take the identified "hit" responses and do a shity "weighting"
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
        if len(hitExactMatch) > 0:
            return hitExactMatch[0]
        elif len(hitPartialMatch) > 0:
            return hitPartialMatch[0]
        elif len(hitButNoMatch) > 0:
            return hitButNoMatch[0]
        else:
            return noHit[0]