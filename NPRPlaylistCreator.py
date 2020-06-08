import json
import requests
from exceptions import ResponseException
from secrets import spotify_user_id, spotipyUserToken
from urllib import parse
import re
import datetime
from NPRPageParser import NPRPageParser
# note: Playlists can have a maximum of 10,000 tracks each.
# note: You can have as many playlists as you want, but only with 10k tracks each. (confusing info on)
# todo: function to recheck missing songs
class NPRPlaylistCreator:
    def __init__(self):
        self.all_song_info = list()
        self.playListID = ""
        self.nprPageLink = ""
        self.articleDay = ""
        self.fileName = ""
        self.jsonData = NPRPageParser.GetJsonData(self.fileName)

    def create_playlist(self, playlistName):
        request_body = json.dumps({"name": playlistName, "public": False})
        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
        response = requests.post(query, data=request_body, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        handleResponse(response)
        response_json = response.json()
        self.playListID = response_json["id"]

    def get_artist_data(self):
        # request/fetch artist data from json file
        for entry in self.jsonData:
            for value in entry:
                if isinstance(value, dict):
                    self.all_song_info.append(value)
        return self.all_song_info

    def add_song_to_playlist(self, playListID, songList):
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playListID)
        request_data = json.dumps(uriList)
        response = requests.post(query, data=request_data, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        return handleResponse(response)


    def handleRespone(self, response):
        # check for valid response status
        if response.status_code != 200 or response.status_code != 201:
            print(response)
            return response
        else:
            raise ResponseException(response.status_code)
            print(response)

# Process found and missing artists function?
    def constructPlaylistDescription(self):
        for dic in self.jsonData:
            if "Page Link" in dic:
                self.nprPageLink = str(dic.get("Page Link"))
        if (len(self.missedTracksList) > 0):
            request_body = json.dumps({"description": self.nprPageLink + " [:(MISSING TRACK(S): " + str(len(self.missedTracksList)) + "] " + " ".join(self.missedTracksList) + " [LASTCHECKED: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "]" + " [CORRECTIONS: addy@something.com]"})
        else:
            request_body = json.dumps({"description": self.nprPageLink + " [ALL TRACKS FOUND!] " + " [LASTCHECKED: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "]" + " [CORRECTIONS(it's not perfect): addy@something.com]"})

# function to Update playlist description
    def updatePlaylistDescription(self, playlistID, description):
        query = "https://api.spotify.com/v1/playlists/{}".format(playlistID) 
        response = requests.put(query, data=description, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        handleResponse(response)