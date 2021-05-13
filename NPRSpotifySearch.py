import re
import copy
import json
import time
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

# TODO create a way to make correction updates from helpers easy
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
        auxiliaryList = list()
        if artists == None:
            artists = list("") # we could still search and accept a track result hit without an artist entry?
        else:
            for artist in artists:
                artist = self.RemoveCommonPhrasesArtists(self.RemoveParenthesis(self.RemoveBrackets(artist)))
                artist = artist.split()
                artist.extend(artists)
                for word in artist:
                    if word not in auxiliaryList:
                        auxiliaryList.append(word)
            auxiliaryList.append("") # Need an empty string for when track match is really high but artist is 0
        for artist in auxiliaryList:
            artistResponses = list()
            artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(trackCopy), unidecode(artist)))
            trackCopy = self.RemoveBrackets(unidecode(trackCopy))
            artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(trackCopy), unidecode(artist)))
            trackCopy = self.RemoveParenthesis(unidecode(track))
            artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(trackCopy), unidecode(artist)))
            trackCopy = self.RemoveCommonPhrasesTracks(unidecode(trackCopy))
            artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(trackCopy), unidecode(artist)))
            trackCopy = self.RemoveNumbers(unidecode(trackCopy))
            artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(trackCopy), unidecode(artist)))
            artistResponses.append(self.SearchImplicitTrackExplicitArtist(unidecode(trackCopy), unidecode(artist)))
            artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(trackCopy.split("(")[0]), unidecode(artist)))
            artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(trackCopy.split("[")[0]), unidecode(artist)))
            artistResponses.append(self.SearchExplicitTrackAndArtist(unidecode(trackCopy.partition(":")[2]), unidecode(artist)))
            # hail Marry's
            artistResponses.append(self.SearchImplicitTrackImplicitArtist(unidecode(track), unidecode(self.ReplaceAmpersand(artist))))
            artistResponses.append(self.SearchImplicitTrackAndArtistCombined(unidecode(track), unidecode(self.ReplaceAmpersand(artist))))
            # time.sleep(1) # Don't hammer spotify server?
            trackResponses.append(artistResponses)
        print("-- NPR Track \"{0}\" by \"{1}\" searched.".format(track, str(artists)))
        bestChoice = self.ChooseBestMatch(trackResponses, track, artists)
        return bestChoice

    # Using libdiff to create a hit threshhold of sorts.
    def ChooseBestMatch(self, responses, nprTrack, nprArtists):
        bestMatch = dict()
        bestMatch["NPR Track Name"] = nprTrack
        bestMatch["NPR Artist Names"] = nprArtists
        bestMatch["Result Track Name"] = None
        bestMatch["Result Artist Names"] = list()
        bestMatch["Result Track-Match Percent"] = 0.0
        bestMatch["Result Artists-Match Percent"] = 0.0
        bestMatch["Result Track URI"] = None
        if responses == None or len(responses) == 0.0:
            print("hmmm...")
        # this is all really gross looking
        else:
            for response in responses:
                for result in response:
                    if len(result["tracks"]["items"]) != 0.0:
                        resultTrackName = result["tracks"]["items"][0]["name"]
                        resultTrackNameSplit = list() # split track name words into a new list for comparison later
                        for word in resultTrackName.split(): # go through each word in track name
                            word = re.sub(r'[^\w]', ' ', word).lower().strip() # remove non-alphanumerics
                            resultTrackNameSplit.extend(word.split()) # split strings that end up like 'no 1'
                        resultTrackNameSplit = list(filter(None, resultTrackNameSplit)) # get rid of empty strings
                        nprTrackNameSplit = list()
                        for word in nprTrack.split():
                            word = re.sub(r'[^\w]', ' ', word).lower().strip()
                            nprTrackNameSplit.extend(word.split())
                        nprTrackNameSplit = list(filter(None, nprTrackNameSplit))
                        resultMatchesToNPR = [sub for sub in resultTrackNameSplit if sub in nprTrackNameSplit] # see what of the result matches the npr name
                        #
                        nprRemovedPhrasesArtists = list()
                        for artist in nprArtists:
                            artist = re.sub(r'[^\w]', ' ', artist).lower().strip()
                            nprRemovedPhrasesArtists.extend(artist.split())
                        nprRemovedPhrasesArtists = list(filter(None, nprRemovedPhrasesArtists))
                        resultTrackArtistNames = result["tracks"]["items"][0]["artists"]
                        resultArtistNames = list() # need to split first, last, misc names into individual strings
                        resultArtistNamesCopy = list() # copy to store later in best match
                        for artist in resultTrackArtistNames:
                            resultArtistNamesCopy.append(artist["name"]) # copy to store later in best match
                            artist["name"] = re.sub(r'[^\w]', ' ', artist["name"]).lower().strip()
                            resultArtistNames.extend(artist["name"].split())
                        resultArtistNames = list(filter(None, resultArtistNames))
                        resultArtistNPRMatches = [sub for sub in resultArtistNames if sub in nprRemovedPhrasesArtists]
                        #
                        resultsArtistsSet = set(resultArtistNPRMatches)
                        nprArtistNamesSet = set(nprRemovedPhrasesArtists)
                        resultsTrackNameSet = set(resultMatchesToNPR)
                        nprTrackNameSet = set(nprTrackNameSplit)
                        # First, a quick exact-match check (preferred)
                        if nprArtistNamesSet == resultsArtistsSet and nprTrackNameSet == resultsTrackNameSet or bestMatch["Result Track-Match Percent"] == 1.0 and bestMatch["Result Artists-Match Percent"] == 1.0: # check artist names first, less likely to match
                            bestMatch["Result Track Name"] = result["tracks"]["items"][0]["name"]
                            bestMatch["Result Artist Names"] = resultArtistNamesCopy
                            bestMatch["Result Track-Match Percent"] = 1.0
                            bestMatch["Result Artists-Match Percent"] = 1.0
                            bestMatch["Result Track URI"] = result["tracks"]["items"][0]["uri"]
                            print("--------- Best Match Found ----------")
                            print(json.dumps(bestMatch, indent=4, sort_keys=True, ensure_ascii=False))
                            print("    ---------   End   ----------")
                            return bestMatch
                            # If we have a perfect match, no need to check the rest
                        # Fun weighting(?) results-land
                        else:
                            seqTrack = SequenceMatcher(a=nprTrackNameSplit, b=resultTrackNameSplit)
                            seqArtist = SequenceMatcher(a=nprRemovedPhrasesArtists, b=resultArtistNames)
                            trackMatchScore = seqTrack.ratio()
                            artistsMatchScore = seqArtist.ratio()
                            if artistsMatchScore >= 0.5 and artistsMatchScore >= bestMatch["Result Artists-Match Percent"]: # high artist name accuracy
                                if trackMatchScore >= 0.75 and trackMatchScore >= bestMatch["Result Track-Match Percent"]: # good chance at match
                                    bestMatch["Result Track Name"] = result["tracks"]["items"][0]["name"]
                                    bestMatch["Result Artist Names"] = resultArtistNamesCopy
                                    bestMatch["Result Track-Match Percent"] = trackMatchScore
                                    bestMatch["Result Artists-Match Percent"] = artistsMatchScore
                                    bestMatch["Result Track URI"] = result["tracks"]["items"][0]["uri"]
                            if trackMatchScore >= 0.5 and trackMatchScore >= bestMatch["Result Track-Match Percent"]: # high artist name accuracy
                                if  artistsMatchScore>= 0.75 and artistsMatchScore >= bestMatch["Result Artists-Match Percent"]: # good chance at match
                                    bestMatch["Result Track Name"] = result["tracks"]["items"][0]["name"]
                                    bestMatch["Result Artist Names"] = resultArtistNamesCopy
                                    bestMatch["Result Track-Match Percent"] = trackMatchScore
                                    bestMatch["Result Artists-Match Percent"] = artistsMatchScore
                                    bestMatch["Result Track URI"] = result["tracks"]["items"][0]["uri"]
            print("--------- Current Best ----------")
            print(json.dumps(bestMatch, indent=4, sort_keys=True, ensure_ascii=False))
            print("--------- Current Best End ------")
            return bestMatch

    def RemoveBrackets(self, track):
        newTrack = track.translate({ord(i): None for i in '[]'})
        return newTrack
    
    def RemoveParenthesis(self, track):
        newTrack = track.translate({ord(i): None for i in '()'})
        return newTrack

    def RemoveNumbers(self, track):
        newTrack = track.translate({ord(i): None for i in '0'})
        return newTrack

    def RemoveCommonPhrasesTracks(self, track):
        stop_words = ['feat.', 'feat', 'original', 'edit', 'featuring', 'feature']
        stopwords_dict = Counter(stop_words)
        result = ' '.join([word for word in track.lower().split() if word not in stopwords_dict])
        return result

    def RemoveCommonPhrasesArtists(self, track):
        stop_words = ['and', 'the', 'various', 'artists', 'orchestra', 'symphony', "conducted", 'by', 'sax']
        stopwords_dict = Counter(stop_words)
        result = ' '.join([word for word in track.lower().split() if word not in stopwords_dict])
        return result

    def ReplaceAmpersand(self, track):
        result = track.replace('&', 'and')
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
