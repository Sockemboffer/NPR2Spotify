import json
import base64
import logging
import requests
import datetime
from ResponsesHandle import ResponseException
from secrets import spotify_user_id, spotipyUserToken
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class NPRPlaylistCreator:

    def CreatePlaylist(playlistName):
        requestSession = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
        requestSession.mount('https://api.spotify.com/', HTTPAdapter(max_retries=retries))
        # Playlist max character name limit is 100
        request_body = json.dumps({"name": playlistName, "public": False})
        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
        response = requestSession.post(query, data=request_body, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        response_json = response.json()
        print("-- Playlist created.")
        return response_json

    def AddTracksToPlaylist(searchedTracks, playlistID):
        requestSession = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
        requestSession.mount('https://api.spotify.com/', HTTPAdapter(max_retries=retries))
        tracksURIs = list()
        urisData = dict()
        for track in searchedTracks:
            if (track["Found Match Type"] == "HitExactMatch") or (track["Found Match Type"] ==  "HitPartialMatch"):
                tracksURIs.append(track["Found Track URI"])
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlistID)
        urisData["uris"] = tracksURIs
        request_data = json.dumps(urisData)
        response = requestSession.post(query, request_data, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        print("-- Playlist tracks added.")

    def AddCoverArtToPlaylist(searchedTracks, day, playlistID):
        requestSession = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
        requestSession.mount('https://api.spotify.com/', HTTPAdapter(max_retries=retries))
        encoded_string = NPRPlaylistCreator.GetNewCover(searchedTracks, day)
        query = "https://api.spotify.com/v1/users/{}/playlists/{}/images".format(spotify_user_id, playlistID) 
        response = requestSession.put(query, encoded_string, headers={"Authorization": "Bearer {}".format(spotipyUserToken), "Content-Type": "image/jpeg"})
        print("-- Playlist cover image added.")

    def UpdatePlaylistDescription(searchedTracks, playlistID, nprURL):
        requestSession = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
        requestSession.mount('https://api.spotify.com/', HTTPAdapter(max_retries=retries))
        missedTracksList = list()
        # Removing exessive link-guts so description has more to work with
        nprURL = nprURL.partition("?")
        for missedTrack in searchedTracks:
            if missedTrack["Found Match Type"] == "NoHit" or missedTrack["Found Match Type"] == "HitButNoMatch":
                missedTracksList.append(missedTrack)
        if missedTracksList != None:
            newDescription = dict()
            newDescription["description"] = str(nprURL[0]) + " [MISSING:" + str(len(missedTracksList)) + "]"
            for track in missedTracksList:
                if track["Found Match Type"] == "HitButNoMatch" and track["NPR Artist Name"][0] == "":
                    newDescription["description"] += ", Song: " + track["NPR Track Name"] + " by: ¿?"
                else:
                    newDescription["description"] += ", Song: " + track["NPR Track Name"] + " by: " + ", ".join(track["NPR Artist Name"])
            newDescription["description"] += "-{Checked: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "}  Send corrections: NPRMoWeEd2Spotify@pm.me"
            # 300 character limit playlist desciption
            # Check if description exceeds character limit so we can truncate
            # returns response ok if over limit, but no description will be made.
            if len(newDescription["description"]) > 300:
                newDescription["description"] = newDescription["description"][:300]
                newEndingDescription =  "-desc. limit" + "-{Checked: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "}  Send corrections: NPRMoWeEd2Spotify@pm.me"
                newDescription["description"] = newDescription["description"][:len(newEndingDescription)*-1]
                newDescription["description"] += newEndingDescription
        else:
            newDescription = dict()
            newDescription["description"] = str(nprURL) + " [ALL " + len(searchedTracks) + " FOUND] {Checked: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "}  Send corrections: NPRMoWeEd2Spotify@pm.me"
        query = "https://api.spotify.com/v1/playlists/{}".format(playlistID)
        response = requestSession.put(query, json.dumps(newDescription), headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        print("!! Truncated description.")

    def GetNewCover(searchedTracks, day):
        print("-- All Tracks found jpg selected.")
        if (day != "Saturday") and (day != "Sunday"):
            with open("NPRLogos/npr_me.jpg", "rb") as im:
                encoded_string = base64.b64encode(im.read())
                return encoded_string    
        elif (day != "Sunday"):
            with open("NPRLogos/npr_we_sat.jpg", "rb") as im:
                encoded_string = base64.b64encode(im.read())
                return encoded_string
        else:
            with open("NPRLogos/npr_we_sun.jpg", "rb") as im:
                encoded_string = base64.b64encode(im.read())
                return encoded_string