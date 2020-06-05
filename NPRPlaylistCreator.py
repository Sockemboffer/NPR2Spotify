import json
import requests
from exceptions import ResponseException
from secrets import spotify_user_id, spotipyUserToken
from urllib import parse
import re
from string import Template
import datetime
from PIL import Image
import base64
# note: Playlists can have a maximum of 10,000 tracks each.
# note: You can have as many playlists as you want, but only with 10k tracks each. (confusing info on)
# todo: function to recheck missing songs
class CreatePlaylist:
    def __init__(self):
        self.all_song_info = list()
        self.all_uri_info = list()
        self.songLastChecked = ""
        self.playListID = ""
        self.nprPageLink = ""
        self.articleDay = ""
        self.missedTracksList = list()
        self.foundTracksList = list()
        self.result = ""

    def create_playlist(self):
        # Create A New Playlist
        jsonData = self.get_json_data()
        for dic in jsonData:
            if "Playlist Name" in dic:
                playlistName = str(dic.get("Playlist Name"))
            if "Page Link" in dic:
                self.nprPageLink = str(dic.get("Page Link"))
            if "Day" in dic:
                self.articleDay = str(dic.get("Day"))
        request_body = json.dumps({
            "name": playlistName,
            "public": False})
        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotipyUserToken)})
        response_json = response.json()
        handleResponse(response)
        #print(response_json)
        self.playListID = response_json["id"]
        return self.playListID

    def get_artist_data(self):
        # request/fetch artist data from json file
        jsonData = self.get_json_data()
        for entry in jsonData:
            for value in entry:
                if isinstance(value, dict):
                    self.all_song_info.append(value)
        # print(self.all_song_info)
        return self.all_song_info

    def add_song_to_playlist(self, playListID, uriList):
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playListID)
        request_data = json.dumps(uriList)
        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotipyUserToken)})
        handleResponse(response)


    def handleRespone(self, response):
        # check for valid response status
        if response.status_code != 200 or response.status_code != 201:
            print(response)
        else:
            raise ResponseException(response.status_code)
            print(response)

# function to update key,value pair?
    for dicInJson in jsonData:
        if isinstance(dicInJson, dict):
            for kDicData, vDicData in dicInJson.items():
                if kDicData == "Playlist Link":
                    #print(json.dumps(response_json))
                    for kRes, vRes in response_json.items():
                        #print(k)
                        if isinstance(vRes, dict) and ("spotify" in vRes):
                            dicInJson[kDicData] = vRes["spotify"]
                            #print(kDicData)
                elif kDicData == "Playlist URI":
                    #print(json.dumps(response_json))
                    for kRes, vRes in response_json.items():
                        #print(k)
                        if kRes == "uri":
                            dicInJson[kDicData] = vRes
                            #print(kDicData)

# Process found and missing artists function?
    self.result = "" # gross
    if (len(self.missedTracksList) > 0):
        request_body = json.dumps({"description": self.nprPageLink + " [:(MISSING TRACK(S): "
        + str(len(self.missedTracksList)) + "] " + " ".join(self.missedTracksList) + " [LASTCHECKED: " 
        + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "]" + " [CORRECTIONS: addy@something.com]"})
    else:
        request_body = json.dumps({"description": self.nprPageLink + " [ALL TRACKS FOUND!] "
        + " [LASTCHECKED: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "]" 
        + " [CORRECTIONS(it's not perfect): addy@something.com]"})

# function to Update playlist description
    def updatePlaylistDescription(self, playlistID, description)
        query = "https://api.spotify.com/v1/playlists/{}".format(playlistID) 
        response = requests.put(
            query,
            data=description,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotipyUserToken)})
        handleResponse(response)

newPlaylistCreator = CreatePlaylist()
dayInterludeList = newPlaylistCreator.get_artist_data()
newPlaylist = newPlaylistCreator.create_playlist()
spotifyURIs = newPlaylistCreator.get_spotify_uri(dayInterludeList)
spotifyResponse = newPlaylistCreator.add_song_to_playlist(newPlaylist, spotifyURIs)