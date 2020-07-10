from ResponsesHandle import ResponseException
from urllib import parse
import requests
from secrets import spotify_user_id, spotipyUserToken
import json
from collections import Counter
# todo: re-check parsed page for missing tracks to research
    # todo: check if playlist exsists
    # todo: notify when previously not found track is found
# todo: when searching, push all track and artist names to lowercase
# fix: double-quotes are have dangling escape slash in string from response?
# todo: add additional search for each artist found
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
                self.nprArtistsName = dic["Interlude Artist"]
                self.artists = str(dic.get("Interlude Artist")).lower()
                #print(self.artists)
            if "Interlude Song" in dic:
                self.nprTrackName = dic.get("Interlude Song")
                self.track = str(dic.get("Interlude Song")).lower()
                #print(self.track)
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
            #print(parsedResponses)
            #print(" ")
            # compare responses
            # ======================================= are my choosen response lists correct?
            choosenResponseForTracks.append(self.CompareResponses(parsedResponses))
            #print("Finished: " + self.nprTrackName + ", by: " + self.nprArtistsName[0])
        #print(json.dumps(choosenResponseForTracks, ensure_ascii=False, indent=4))
        #print(str(len(choosenResponseForTracks)) + " songs parsed.")
        return choosenResponseForTracks

    def RemoveBrackets(self, track):
        newTrack = track.translate({ord(i): None for i in '[]'})
        #print("!! Removed brackets: " + newTrack)
        return newTrack
    
    def RemoveParenthesis(self, track):
        newTrack = track.translate({ord(i): None for i in '()'})
        #print("!! Removed parenthesis: " + newTrack)
        return newTrack

    def RemoveCommonPhrases(self, track):
        stop_words = ['feat.', 'feat', 'original', 'edit', 'featuring', 'feature']
        stopwords_dict = Counter(stop_words)
        result = ' '.join([word for word in track.split() if word not in stopwords_dict])
        #print("!! Removed common Phrases: " + result)
        return result

    def SearchExplicitTrackAndArtist(self, track, artist):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=1".format(parse.quote('track:' + '"' + track + '"' + ' ' + 'artist:"' + artist + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        #print(json.dumps(response.json(), ensure_ascii=False, indent=4))
        # check for valid response status
        if response.status_code != 200:
            raise ResponseException(response.status_code)
        #print(">> Explicit Track and Artist search finished.")
        return response.json()
    
    def SearchImplicitTrackExplicitArtist(self, track, artist):
        query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=1".format(parse.quote('"' + track + '"' + ' ' + 'artist:"' + artist + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # check for valid response status
        if response.status_code != 200:
            raise ResponseException(response.status_code)
        #print(">> Implicit Track and Explicit Artist search finished.")
        return response.json()
    
    def SearchImplicitTrackNoArtist(self, track):
        query = "https://api.spotify.com/v1/search?q={}&type=track&market=US&limit=1".format(parse.quote('"' + track + '"'))
        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # check for valid response status
        if response.status_code != 200:
            raise ResponseException(response.status_code)
        #print(">> Implicit Track and No Artist search finished.")
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
        identifiedResponses = list()
        for response in parsedResponsesJSON:
            # # str0 = str(response["Found Track Name"]).lower()
            # # str1 = self.nprTrackName.lower()
            # str2 = str(response["Found Artist Name"]).lower()
            # str3 = self.nprArtistsName[0].lower()
            # # print(str0)
            # # print(str1)
            # print(str2)
            # print(str3)
            # # print("<"+ str(response["Found Track Name"]).lower() + ">")
            # # print("<"+ self.nprTrackName.lower() + ">")
            # print("<"+ str(response["Found Artist Name"]).lower() + ">")
            # print("<"+ self.nprArtistsName[0].lower() + ">")
            # print(" ")
            if response["Found Track Name"] is None:
                # no track found at all from spotify (Not sure if None is used when no track)
                response["Found Match Type"] = "NoHit"
                identifiedResponses.append(response)
            elif str(response["Found Track Name"]).lower() == self.nprTrackName.lower() and str(response["Found Artist Name"]).lower() == self.nprArtistsName[0].lower():
                # hit exact match found to what npr had
                # should I use global var or key when comparing to original?
                response["Found Match Type"] = "HitExactMatch"
                identifiedResponses.append(response)
            elif str(response["Found Track Name"]).lower() != self.nprTrackName.lower() and str(response["Found Artist Name"]).lower() == self.nprArtistsName[0].lower():
                    # hit but track name may be slightly different than what npr has so we compare artist name hoping for an exact
                    response["Found Match Type"] = "HitPartialMatch"
                    identifiedResponses.append(response)
            else:
                # hit but matches neither the track or artist exactly as npr had it
                response["Found Match Type"] = "HitButNoMatch"
                identifiedResponses.append(response)
            #print(json.dumps(response, ensure_ascii=False, indent=4))
        # print(identifiedResponses)
        # print(len(identifiedResponses))
        print("-- Responses identified.")
        return identifiedResponses
    # Isn't returning correctly created list ####################################################
    def CompareResponses(self, parsedResponsesList):
        #print(parsedResponsesList)
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
        # ============
        if len(noHit) == len(parsedResponsesList):
            #print("no hit " + str(noHit[0]))
            return noHit[0]
        elif len(hitExactMatch) > 0:
            #print("hit exact match " + str(hitExactMatch[0]))
            return hitExactMatch[0]
        elif len(hitPartialMatch) > 0:
            #print("hit partial match " + str(hitPartialMatch[0]))
            return hitPartialMatch[0]
        else:
            #print("hit but no match " + str(hitButNoMatch[0]))
            return hitButNoMatch[0]