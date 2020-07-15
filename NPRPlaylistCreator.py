import json
import requests
from secrets import spotify_user_id, spotipyUserToken
from urllib import parse
import re
import datetime
from NPRPageParser import NPRPageParser
from ResponsesHandle import ResponseException
from PIL import Image
import base64
# note: You can have as many playlists as you want, but only with 10k tracks each. (confusing info on)
# todo: function to recheck missing songs
# todo: functions to check and pass correct cover art to new playlist
# todo: bake special "All tracks found!" or checkmark?, "Missing tracks!" into art?
class NPRPlaylistCreator:

    def CreatePlaylist(self, playlistName):
        # Playlist max character name limit is 100
        request_body = json.dumps({"name": playlistName, "public": False})
        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
        response = requests.post(query, data=request_body, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # check for valid response status
        if response.status_code != 201:
            raise ResponseException(response.status_code)
        response_json = response.json()
        print(json.dumps(response_json, indent=4))
        print("-- Playlist created.")
        return response_json

    def AddTracksToPlaylist(self, searchedTracks, playlistID):
        tracksURIs = list()
        urisData = dict()
        for track in searchedTracks:
            if (track["Found Match Type"] == "HitExactMatch") or (track["Found Match Type"] ==  "HitPartialMatch"):
                tracksURIs.append(track["Found Track URI"])
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlistID)
        urisData["uris"] = tracksURIs
        request_data = json.dumps(urisData)
        #print(request_data)
        response = requests.post(query, request_data, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # check for valid response status
        #print(response)
        if response.status_code != 201:
            raise ResponseException(response.status_code)
        print("-- Playlist tracks added.")

    def AddCoverArtToPlaylist(self, searchedTracks, day, playlistID):
        encoded_string = self.GetNewCover(searchedTracks, day)
        query = "https://api.spotify.com/v1/users/{}/playlists/{}/images".format(spotify_user_id, playlistID) 
        response = requests.put(query, encoded_string, headers={"Authorization": "Bearer {}".format(spotipyUserToken), "Content-Type": "image/jpeg"})
        # check for valid response status
        if response.status_code != 202:
            raise ResponseException(response.status_code)
        print("-- Playlist cover image added.")

    # Process found and missing artists function?
    def UpdatePlaylistDescription(self, searchedTracks, playlistID, nprURL):
        # 300 character limit returns response ok if over limit, but no description will be made.
        missedTracksList = list()
        for missedTrack in searchedTracks:
            if missedTrack["Found Match Type"] == "NoHit" or missedTrack["Found Match Type"] == "HitButNoMatch":
                #print(missedTrack)
                missedTracksList.append(missedTrack)
        if missedTracksList != None:
            newDescription = dict()
            newDescription["description"] = str(nprURL) + " [MISSING: " + str(len(missedTracksList)) + "]"
            for track in missedTracksList:
                newDescription["description"] += " [TRACK: " + track["NPR Track Name"] + ", by: " + ", ".join(track["NPR Artist Name"]) + "]"
            newDescription["description"] += " [LASTCHECKED: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "] <CORRECTIONS: addy@something.com>"
        else:
            newDescription = dict()
            newDescription["description"] = nprURL + " [ALL TRACKS FOUND!] [LASTCHECKED: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "] <CORRECTIONS: addy@something.com>"
        query = "https://api.spotify.com/v1/playlists/{}".format(playlistID) 
        #print(json.dumps(newDescription, ensure_ascii=False, indent=4))
        response = requests.put(query, json.dumps(newDescription, ensure_ascii=False), headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # check for valid response status
        if response.status_code != 200:
            raise ResponseException(response.status_code)
        print("-- Playlist description updated.")

    def GetNewCover(self, searchedTracks, day):
        missingTrack = False
        # print(searchedTracks)
        for track in searchedTracks:
            if (track["Found Match Type"] == "NoHit") or (track["Found Match Type"] == "HitButNoMatch"):
                # should include hitbutnomatch?
                missingTrack = True
                break
        if missingTrack == True:
            # Missing tracks cover art used instead
            # Create missing cover art
            print("-- Missing Tracks jpg selected.")
            if (day != "Saturday") and (day != "Sunday"):
                with open("npr_me.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string    
            elif (day != "Sunday"):
                with open("npr_we_sat.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string
            else:
                with open("npr_we_sun.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string
        else:
            # Every track has an entry (though should verified)
            # Create found all tracks cover art
            print("-- All Tracks found jpg selected.")
            if (day != "Saturday") and (day != "Sunday"):
                with open("npr_me.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string    
            elif (day != "Sunday"):
                with open("npr_we_sat.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string
            else:
                with open("npr_we_sun.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string


