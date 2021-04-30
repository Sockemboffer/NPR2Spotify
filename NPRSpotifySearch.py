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
        trackResponses = list()
        for artist in artists:
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
        print("-- NPR Track \"{0}\" by \"{1}\" searched.".format(track, str(artists)))
        return self.ChooseBestMatch(trackResponses, track, artists)

    # Using libdiff to create a hit threshhold of sorts.
    def ChooseBestMatch(self, responses, track, artists):
        bestMatch = dict()
        bestMatch["NPR Track Name"] = track
        bestMatch["NPR Artist Names"] = artists
        bestMatch["Result Track Name"] = None
        bestMatch["Result Artist Names"] = None
        bestMatch["Result Track URI"] = None
        bestMatch["Result Track-Match Percent"] = 0.0
        bestMatch["Result Artists-Match Percent"] = 0.0
        if responses == None or len(responses) == 0.0:
            print("hmmm...")
        else:
            for response in responses:
                for result in response:
                    if len(result["tracks"]["items"]) == 0.0:
                        continue
                    else:
                        currentResult = dict()
                        currentResult["NPR Track Name"] = track
                        currentResult["NPR Artist Names"] = artists
                        currentResult["Result Track Name"] = result["tracks"]["items"][0]["name"]
                        resultArtists = list()
                        for resultartist in result["tracks"]["items"][0]["artists"]:
                            resultArtists.append(resultartist["name"])
                        currentResult["Result Artist Names"] = resultArtists
                        currentResult["Result Track URI"] = result["tracks"]["items"][0]["uri"]
                        seqTrack = SequenceMatcher(a=str(track).lower(), b=str(currentResult["Result Track Name"]).lower())
                        seqArtist = SequenceMatcher(a=str(artists).lower(), b=str(currentResult["Result Artist Names"]).lower())
                        currentResult["Result Track-Match Percent"] = seqTrack.ratio()
                        currentResult["Result Artists-Match Percent"] = seqArtist.ratio()
                        if currentResult["Result Track-Match Percent"] > bestMatch["Result Track-Match Percent"]:
                            if currentResult["Result Artists-Match Percent"] > bestMatch["Result Artists-Match Percent"]:
                                bestMatch["Result Artists-Match Percent"] = currentResult["Result Artists-Match Percent"]
                            bestMatch = currentResult
                            print(json.dumps(bestMatch, indent=4, sort_keys=True, ensure_ascii=False))
                        else:
                            print("-- Not better than best.")
        print("--------- Best Selected -----------------")
        print(json.dumps(bestMatch, indent=4, sort_keys=True, ensure_ascii=False))
        print("--------- Best Selected End -----------------")
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
        return response.json()

    def SearchImplicitTrackImplicitArtist(self, track, artist):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=1".format(parse.quote('"' + track + '"' + ' ' + '"' + artist + '"'))
        response = self.requestSession.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        return response.json()

    def SearchImplicitTrackAndArtistCombined(self, track, artist):
        query = "https://api.spotify.com/v1/search?q={}&type=track&market=US&limit=1".format(parse.quote(str(track + " AND " + artist)))
        response = self.requestSession.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        return response.json()
