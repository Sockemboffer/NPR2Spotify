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
    def SearchSpotify(self, track, artists):
        trackCopy = track
        artistsCopy = artists
        trackResponses = list()
        if artistsCopy == None or len(artistsCopy) == 0:
            artistsCopy = list()
            artistsCopy.append("")
        for artist in artistsCopy:
            if track == None:
                matchResult = dict()
                matchResult["Interlude Track"] = track
                matchResult["Interlude Artists"] = artists
                matchResult["Interlude Track URI"] = None
                matchResult["Interlude Match Track"] = None
                matchResult["Interlude Match Artists"] = None
                matchResult["Interlude Match Percent"] = None
                return matchResult
            artistResponses = list()
            artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(track), unidecode(artist)))
            track = self.RemoveBrackets(unidecode(track))
            artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(track), unidecode(artist)))
            track = self.RemoveParenthesis(unidecode(track))
            artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(track), unidecode(artist)))
            track = self.RemoveCommonPhrases(unidecode(track))
            artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(track), unidecode(artist)))
            artistResponses.append(self.SearchImplicitTrackExplicitArtist(unidecode(track), unidecode(artist)))
            artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(trackCopy.split("(")[0]), unidecode(artist)))
            artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(trackCopy.split("[")[0]), unidecode(artist)))
            # hail Marry's
            artistResponses.append(self.SearchImplicitTrackImplicitArtist(unidecode(track), unidecode(artist)))
            artistResponses.append(self.SearchImplicitTrackAndArtistCombined(unidecode(track), unidecode(artist)))
            trackResponses.append(artistResponses)
        print("-- NPR Track {0} by {1} searched.".format(track, str(artists)))
        return self.ChooseBestMatch(trackResponses, track, artists)

    # Using libdiff to create a hit threshhold of sorts.
    def ChooseBestMatch(self, responses, track, artists):
        bestMatch = dict()
        bestMatch["Interlude Track"] = track
        bestMatch["Interlude Artists"] = artists
        bestMatch["Interlude Match Track"] = ""
        bestMatch["Interlude Match Artists"] = ""
        bestMatch["Interlude Match Percent"] = 0
        if responses == None or len(responses) == 0:
            print("hmmm...")
        else:
            currentResult = dict()
            currentResult["Interlude Track URI"] = ""
            currentResult["Interlude Match Track"] = ""
            currentResult["Interlude Match Artists"] = ""
            currentResult["Interlude Match Percent"] = 0.0
            for response in responses:
                for result in response:
                    if len(result["tracks"]["items"]) == 0:
                        continue
                    else:
                        resultTrackName = result["tracks"]["items"][0]["name"]
                        resultArtists = list()
                        for resultartist in result["tracks"]["items"][0]["artists"]:
                            resultArtists.append(resultartist["name"])
                        currentResult["Interlude Track URI"] = result["tracks"]["items"][0]["uri"]
                        currentResult["Interlude Match Track"] = resultTrackName
                        currentResult["Interlude Match Artists"] = resultArtists
                        seqTrack = SequenceMatcher(a=str(track).lower(), b=str(resultTrackName).lower())
                        seqArtist = SequenceMatcher(a=str(artists).lower(), b=str(resultArtists).lower())
                        artistRatio = seqArtist.ratio()
                        trackRatio = seqTrack.ratio()
                        # perfect 
                        if trackRatio >= 1.0 and artistRatio >= 1.0:
                            currentResult["Interlude Match Percent"] = trackRatio
                        # artist name might be a bit wrong
                        elif trackRatio >= 0.9 and artistRatio >= 0.2:
                            currentResult["Interlude Match Percent"] = trackRatio
                        # good chance match
                        elif trackRatio >= 0.6 and artistRatio >= 0.6:
                            currentResult["Interlude Match Percent"] = trackRatio
                        # close match
                        elif trackRatio >= 0.4 and artistRatio >= 0.8:
                            currentResult["Interlude Match Percent"] = trackRatio
                        # poor chance 
                        elif trackRatio < 0.4 and artistRatio < 0.2:
                            currentResult["Interlude Match Percent"] = 0.0
                        # catch rest as no match
                        else:
                            currentResult["Interlude Match Percent"] = 0.0
                        if currentResult["Interlude Match Percent"] >= bestMatch["Interlude Match Percent"]:
                            bestMatch = currentResult
                        else:
                            continue
        print("Match Track {0} by {1} found.".format(bestMatch["Interlude Match Track"], bestMatch["Interlude Match Artists"]))
        print("Match percent: {0}".format(bestMatch["Interlude Match Percent"]))
        return bestMatch

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

    # # Take the responses and strip out what I want/need for later into my own dictionary
    # def GenerateMatchRatios(self, responsesJSON, track, artists):
    #     if responsesJSON == None or len(responsesJSON) == 0:
    #         # Empty or no tracks returned
    #         parsed = dict()
    #         parsed["Match Ratio"] = None
    #         print("-- No matches found for {} by {}", track, str(artists))
    #     # Loop over every search results
    #     parsedTracks = list()
    #     for artistResponse in responsesJSON:
    #         # do we have any results for this artist
    #         if len(artistResponse) != 0:
    #             for result in artistResponse:
    #                 # is there track data to get
    #                 if result["tracks"]["total"] != 0:
    #                     # parsed = dict()
    #                     # parsed["Found Track Name"] = result["tracks"]["items"][0]["name"]
    #                     # # later we want to itterate over lists because there could be tracks with many artists credited
    #                     # # Spotfy's results can return a list of attributed artists or if only one a string
    #                     # artistList = list()
    #                     # if isinstance(result["tracks"]["items"][0]["artists"], list):
    #                     #     for artist in result["tracks"]["items"][0]["artists"]:
    #                     #         artistList.append(artist["name"])
    #                     #     parsed["Found Artist Names"] = artistList
    #                     # else:
    #                     #     emptyList = list()
    #                     #     emptyList.append("")
    #                     #     parsed["Found Artist Names"] = emptyList
    #                     # parsed["Found Track URI"] = result["tracks"]["items"][0]["uri"]
    #                     # parsed["Match"] = None
    #                     # parsedTracks.append(parsed)
    #                 else:
    #                     # # Empty result used later
    #                     # parsed = dict()
    #                     # parsed["NPR Track Name"] = track
    #                     # parsed["Found Track Name"] = ""
    #                     # parsed["NPR Artist Name"] = artists
    #                     # emptyList = list()
    #                     # emptyList.append("")
    #                     # parsed["Found Artist Name"] = emptyList
    #                     # parsed["Found Track URI"] = ""
    #                     # parsed["Match"] = 0
    #                     # parsedTracks.append(parsed)
    #     self.CatagorizeResponses(parsedTracks)
    #     return parsedTracks
