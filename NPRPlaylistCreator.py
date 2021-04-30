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
        # Playlist name limit is 100 char
        request_body = json.dumps({"name": playlistName, "public": False})
        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
        response = self.requestSession.post(query, data=request_body, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        response_json = response.json()
        print("-- Playlist created.")
        return response_json

    def AddTracksToPlaylist(self, editionDayData):
        tracksURIs = list()
        for item in editionDayData:
            for entry in item:
                if entry == "Result Track-Match Percent":
                    if item["Result Track-Match Percent"] >= 0.5:
                        tracksURIs.append(item["Result Track URI"])
        urisData = dict()
        urisData["uris"] = tracksURIs
        request_data = json.dumps(urisData)
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(editionDayData[0]['Playlist URI'])
        self.requestSession.post(query, request_data, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        print("-- Playlist tracks added.")

    def AddCoverArtToPlaylist(self, editionDayData):
        encoded_string = NPRPlaylistCreator.GetNewCover(editionDayData[0]["Day"])
        query = "https://api.spotify.com/v1/users/{}/playlists/{}/images".format(spotify_user_id, editionDayData[0]['Playlist URI']) 
        self.requestSession.put(query, encoded_string, headers={"Authorization": "Bearer {}".format(spotipyUserToken), "Content-Type": "image/jpeg"})
        # if response.status_code != 200:
        #     raise ResponseException(response.status_code)
        print("-- Playlist cover image added.")

    def UpdatePlaylistDescription(self, searchedTracks, playlistID, nprURL):
        # Removing exessive link-guts so description has more to work with
        nprURL = nprURL.partition("?")
        missedTracksList = list()
        for track in searchedTracks:
            if track["Match"] < 0.4:
                missedTracksList.append(track)
        # print("Missed Tracks: ")
        # print(missedTracksList)
        if len(missedTracksList) != 0:
            newDescription = dict()
            newDescription["description"] = "😭💔 Missing " + str(len(missedTracksList)) + " of " + str(len(searchedTracks)) + " "
            for track in missedTracksList:
                newDescription["description"] += "❌ \"" + track["NPR Track Name"] + "\" by: " + ", ".join(track["NPR Artist Name"]) + " "
            newDescription["description"] += " 🏁 Created: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + " 🧰 Corrections: MoWeEd2Spotify[a-t]pm.me"
            # 300 character limit playlist desciption
            # Check if description exceeds character limit so we can truncate
            # returns response ok if over limit, but no description will be made.
            if len(newDescription["description"]) > 300:
                newDescription["description"] = newDescription["description"][:300]
                newEndingDescription =  "🚧 ...desc. limit " + "🏁 Created: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + " 🧰 Corrections: MoWeEd2Spotify[a-t]pm.me"
                newDescription["description"] = newDescription["description"][:len(newEndingDescription)*-1]
                newDescription["description"] += newEndingDescription
                print("!! Truncated description.")
        else:
            newDescription = dict()
            newDescription["description"] = "🤩🌈 Found " + str(len(searchedTracks)) + " of " + str(len(searchedTracks)) + " 🏁 Created: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + " 🧰 Corrections: MoWeEd2Spotify[a-t]pm.me ⇔ " + "Support your local 🌎👩🏽‍🤝‍👩🏿👨🏻‍🤝‍👨🏼👫🏻🧑🏻‍🤝‍🧑🏾👭🏼👫🏽👭👬🏿👬🏼🧑🏻‍🤝‍🧑🏿🧑‍🤝‍🧑👩🏾‍🤝‍👩🏼🧑🏿‍🤝‍🧑🏿👫👩🏻‍🤝‍👩🏿👬🧑🏽‍🤝‍🧑🏾👫🏿📻 station because they're rad AND use dope music. 💯🔥 www.npr.org/donations/support 🔥"
        missedTracksList.clear()
        query = "https://api.spotify.com/v1/playlists/{}".format(playlistID)
        self.requestSession.put(query, json.dumps(newDescription), headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # if response.status_code != 200:
        #     raise ResponseException(response.status_code)
        print("-- Playlist description updated.")

    def GetNewCover(day):
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