import json
import requests
from exceptions import ResponseException
from secrets import spotify_user_id, spotipyUserToken
from urllib import parse
import re
import datetime
from NPRPageParser import NPRPageParser
from NPRPlaylistCoverCreator import NPRPlaylistCoverCreator
from ResponsesHandle import ResponseHandle
# note: Playlists can have a maximum of 10,000 tracks each.
# note: You can have as many playlists as you want, but only with 10k tracks each. (confusing info on)
# todo: function to recheck missing songs
class NPRPlaylistCreator:
    def __init__(self):
        self.playListID = ""
        self.nprPageLink = ""
        self.ResponseHandle = ResponseHandle()

    def CreatePlaylist(self, playlistName):
        request_body = json.dumps({"name": playlistName, "public": False})
        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
        response = requests.post(query, data=request_body, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.ResponseHandle.HandleRespone(response)
        response_json = response.json()
        return response_json["id"]

    def add_song_to_playlist(self, songList, playlistID):
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlistID)
        request_data = json.dumps(uriList)
        response = requests.post(query, data=request_data, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.ResponseHandle.HandleRespone(response)

    def AddCoverArtToPlaylist(self, day, playlistID):
        encoded_string = NPRPlaylistCoverCreator.getNewCover(day)
        query = "https://api.spotify.com/v1/users/{}/playlists/{}/images".format(spotify_user_id, playlistID) 
        response = requests.put(query, encoded_string, headers={"Authorization": "Bearer {}".format(spotipyUserToken), "Content-Type": "image/jpeg"})
        self.ResponseHandle.HandleRespone(response)

# Process found and missing artists function?
    def ConstructPlaylistDescription(self, jsonData):
        for dic in jsonData:
            if "Page Link" in dic:
                self.nprPageLink = str(dic.get("Page Link"))
        if (len(self.missedTracksList) > 0):
            request_body = json.dumps({"description": self.nprPageLink + " [:(MISSING TRACK(S): " + str(len(self.missedTracksList)) + "] " + " ".join(self.missedTracksList) + " [LASTCHECKED: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "]" + " [CORRECTIONS: addy@something.com]"})
        else:
            request_body = json.dumps({"description": self.nprPageLink + " [ALL TRACKS FOUND!] " + " [LASTCHECKED: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "]" + " [CORRECTIONS(it's not perfect): addy@something.com]"})

# function to Update playlist description
    def UpdatePlaylistDescription(self, playlistID, description):
        query = "https://api.spotify.com/v1/playlists/{}".format(playlistID) 
        response = requests.put(query, data=description, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.ResponseHandle.HandleRespone(response)