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

    def __init__(self):
        self.requestSession = requests.Session()
        self.retries = Retry(total=3, backoff_factor=1, status_forcelist=[ 204, 304, 400, 401, 403, 404, 500, 502, 503, 504 ])
        self.requestSession.mount('https://api.spotify.com/', HTTPAdapter(max_retries=self.retries))

    def CreatePlaylist(self, playlistName):
        # Playlist max character name limit is 100
        request_body = json.dumps({"name": playlistName, "public": False})
        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
        response = self.requestSession.post(query, data=request_body, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # if response.status_code != 200:
        #     raise ResponseException(response.status_code)
        response_json = response.json()
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
        self.requestSession.post(query, request_data, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # if response.status_code != 200:
        #     raise ResponseException(response.status_code)
        print("-- Playlist tracks added.")

    def AddCoverArtToPlaylist(self, searchedTracks, day, playlistID):
        encoded_string = NPRPlaylistCreator.GetNewCover(searchedTracks, day)
        query = "https://api.spotify.com/v1/users/{}/playlists/{}/images".format(spotify_user_id, playlistID) 
        self.requestSession.put(query, encoded_string, headers={"Authorization": "Bearer {}".format(spotipyUserToken), "Content-Type": "image/jpeg"})
        # if response.status_code != 200:
        #     raise ResponseException(response.status_code)
        print("-- Playlist cover image added.")

    def UpdatePlaylistDescription(self, searchedTracks, playlistID, nprURL):
        missedTracksList = list()
        # Removing exessive link-guts so description has more to work with
        nprURL = nprURL.partition("?")
        for missedTrack in searchedTracks:
            if missedTrack["Found Match Type"] == "NoHit" or missedTrack["Found Match Type"] == "HitButNoMatch":
                missedTracksList.append(missedTrack)
        if len(missedTracksList) != 0:
            newDescription = dict()
            newDescription["description"] = "😭💔 Missing " + str(len(missedTracksList)) + " of " + str(len(searchedTracks)) + " "
            for track in missedTracksList:
                if track["Found Match Type"] == "HitButNoMatch" and track["NPR Artist Name"][0] == "":
                    newDescription["description"] += "❌ \"" + track["NPR Track Name"] + "\" by: ❓, "
                else:
                    newDescription["description"] += "❌ \"" + track["NPR Track Name"] + "\" by: " + ", ".join(track["NPR Artist Name"]) + " "
            newDescription["description"] += " 🏁 Created: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + " 📧🧰 Corrections: NPRMoWeEd2Spotify[a-t]pm.me"
            # 300 character limit playlist desciption
            # Check if description exceeds character limit so we can truncate
            # returns response ok if over limit, but no description will be made.
            if len(newDescription["description"]) > 300:
                newDescription["description"] = newDescription["description"][:300]
                newEndingDescription =  "🚧 ...desc. limit " + "🏁 Created: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + " 📧🧰 Corrections: NPRMoWeEd2Spotify[a-t]pm.me"
                newDescription["description"] = newDescription["description"][:len(newEndingDescription)*-1]
                newDescription["description"] += newEndingDescription
                print("!! Truncated description.")
        else:
            newDescription = dict()
            newDescription["description"] = "🤩🌈 Found " + str(len(searchedTracks)) + " of " + str(len(searchedTracks)) + " 🏁 Created: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + " 📧🧰 Corrections: NPRMoWeEd2Spotify[a-t]pm.me ⇔ " + "Support your local 🌎👩🏽‍🤝‍👩🏿👨🏻‍🤝‍👨🏼👫🏻🧑🏻‍🤝‍🧑🏾👭🏼👫🏽👭👬🏿👬🏼🧑🏻‍🤝‍🧑🏿🧑‍🤝‍🧑👩🏾‍🤝‍👩🏼🧑🏿‍🤝‍🧑🏿👫👩🏻‍🤝‍👩🏿👬🧑🏽‍🤝‍🧑🏾👫🏿📻 station because they're rad AND use dope music. 💯🔥 www.npr.org/donations/support 🔥"
        missedTracksList.clear()
        query = "https://api.spotify.com/v1/playlists/{}".format(playlistID)
        self.requestSession.put(query, json.dumps(newDescription), headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # if response.status_code != 200:
        #     raise ResponseException(response.status_code)
        print("-- Playlist description updated.")

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