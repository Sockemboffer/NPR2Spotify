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
import difflib
from difflib import SequenceMatcher

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
        choosenTracks = list()
        for dic in artistList:
            if "Interlude Artist" in dic:
                if dic["Interlude Artist"] == None or str(dic["Interlude Artist"][0]).strip() == "":
                    self.nprArtistsName.clear()
                    self.nprArtistsName.append("")
                    self.artists.clear()
                    self.artists.append("")
                else:
                    self.nprArtistsName = dic.get("Interlude Artist")
                    self.artists = dic.get("Interlude Artist")
            if "Interlude Song" in dic:
                if dic["Interlude Song"] == None or dic["Interlude Song"] == "":
                    # Empty song from webpage, nothing to search
                    print("> Empty track found.")
                    continue
                else:
                    self.nprTrackName = dic.get("Interlude Song")
                    self.track = dic.get("Interlude Song")
            # get spotify responses and convert to json
            trackResponses = list()
            for artist in self.artists:
                artistResponses = list()
                artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(self.track), unidecode(artist)))
                self.track = self.RemoveBrackets(unidecode(self.track))
                artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(self.track), unidecode(artist)))
                self.track = self.RemoveParenthesis(unidecode(self.track))
                artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(self.track), unidecode(artist)))
                self.track = self.RemoveCommonPhrases(unidecode(self.track))
                artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(self.track), unidecode(artist)))
                artistResponses.append(self.SearchImplicitTrackExplicitArtist(unidecode(self.track), unidecode(artist)))
                artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(self.nprTrackName.split("(")[0]), unidecode(artist)))
                artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(self.nprTrackName.split("[")[0]), unidecode(artist)))
                # hail Marry's
                artistResponses.append(self.SearchImplicitTrackImplicitArtist(unidecode(self.nprTrackName), unidecode(artist)))
                artistResponses.append(self.SearchImplicitTrackAndArtistCombined(unidecode(self.nprTrackName), unidecode(artist)))
                trackResponses.append(artistResponses)
            # Very basic weighting on which response I use to add to the playlist
            choosenTracks.append(self.CatagorizeResponses(self.ParseResponsesJSON(trackResponses)))
        return choosenTracks

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
        return response.json()
    
    def SearchImplicitTrackExplicitArtist(self, track, artist):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=1".format(parse.quote('"' + track + '"' + ' ' + 'artist:"' + artist + '"'))
        response = self.requestSession.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # print(json.dumps(response.json(), sort_keys=True, indent=4))
        return response.json()

    def SearchImplicitTrackImplicitArtist(self, track, artist):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=1".format(parse.quote('"' + track + '"' + ' ' + '"' + artist + '"'))
        response = self.requestSession.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        return response.json()

    def SearchImplicitTrackAndArtistCombined(self, track, artist):
        query = "https://api.spotify.com/v1/search?q={}&type=track&market=US&limit=1".format(parse.quote(str(track + " AND " + artist)))
        response = self.requestSession.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        return response.json()

    # Take the responses and strip out what I want/need for later into my own dictionary
    def ParseResponsesJSON(self, responsesJSON):
        parsedTracks = list()
        if responsesJSON == None or len(responsesJSON) == 0:
            # Empty or no tracks returned
            parsed = dict()
            parsed["NPR Track Name"] = self.nprTrackName
            parsed["Found Track Name"] = ""
            parsed["NPR Artist Name"] = ""
            emptyList = list()
            emptyList.append("")
            parsed["Found Artist Name"] = emptyList
            parsed["Found Track URI"] = ""
            parsed["Match"] = 0
            parsedTracks.append(parsed)
            return parsedTracks
        # Loop over every artist search results
        for artistResponse in responsesJSON:
            # do we have any results for this artist
            if len(artistResponse) != 0:
                for result in artistResponse:
                    # is there track data to get
                    if result["tracks"]["total"] != 0:
                        parsed = dict()
                        parsed["NPR Track Name"] = self.nprTrackName
                        parsed["Found Track Name"] = result["tracks"]["items"][0]["name"]
                        parsed["NPR Artist Name"] = self.nprArtistsName
                        # later we want to itterate over lists because there could be tracks with many artists credited
                        # Spotfy's results can return a list of attributed artists or if only one a string
                        artistList = list()
                        if isinstance(result["tracks"]["items"][0]["artists"], list):
                            for artist in result["tracks"]["items"][0]["artists"]:
                                artistList.append(artist["name"])
                            parsed["Found Artist Name"] = artistList
                        else:
                            emptyList = list()
                            emptyList.append("")
                            parsed["Found Artist Name"] = emptyList
                        parsed["Found Track URI"] = result["tracks"]["items"][0]["uri"]
                        parsed["Match"] = None
                        parsedTracks.append(parsed)
                    else:
                        # Empty result used later
                        parsed = dict()
                        parsed["NPR Track Name"] = self.nprTrackName
                        parsed["Found Track Name"] = ""
                        parsed["NPR Artist Name"] = self.nprArtistsName
                        emptyList = list()
                        emptyList.append("")
                        parsed["Found Artist Name"] = emptyList
                        parsed["Found Track URI"] = ""
                        parsed["Match"] = 0
                        parsedTracks.append(parsed)
        return parsedTracks

    # Using libdiff to create a hit threshhold of sorts.
    def CatagorizeResponses(self, parsedResponses):
        bestMatches = list()
        for idx, nprArtist in enumerate(self.nprArtistsName):
            for trackResults in parsedResponses:
                for track in trackResults:
                    seqTrack = SequenceMatcher(a=str(track["NPR Track Name"]).lower(), b=str(track["Found Track Name"]).lower())
                    seqArtist = SequenceMatcher(a=nprArtist.lower(), b=track["Found Artist Name"].lower())
                    artistRatio = seqArtist.ratio()
                    trackRatio = seqTrack.ratio()
                    # perfect 
                    if trackRatio >= 1.0 and artistRatio >= 1.0:
                        track["Match"] = trackRatio
                        bestMatches.append(track)
                    # artist name might be a bit wrong
                    elif trackRatio >= 0.9 and artistRatio >= 0.2:
                        track["Match"] = trackRatio
                        bestMatches.append(track)
                    # good chance match
                    elif trackRatio >= 0.6 and artistRatio >= 0.6:
                        track["Match"] = trackRatio
                        bestMatches.append(track)
                    # close match
                    elif trackRatio >= 0.4 and artistRatio >= 0.8:
                        track["Match"] = trackRatio
                        bestMatches.append(track)
                    # poor chance 
                    elif trackRatio < 0.4 and artistRatio < 0.2:
                        track["Match"] = 0
                        bestMatches.append(track)
                    # catch rest as no match
                    else:
                        track["Match"] = 0
                        bestMatches.append(track)
        # Compare results
        bestMatch = bestMatches[0]
        for match in bestMatches:
            if match["Match"] <= bestMatch["Match"]:
                continue
            else:
                bestMatch = match
        print(str(bestMatch["Match"]))
        # print("NPR Track " + str(bestMatch["NPR Track Name"]) + " by, " + str(bestMatch["NPR Artist Name"]))
        print(bestMatch)
        return bestMatch