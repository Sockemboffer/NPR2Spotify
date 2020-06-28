import json
import requests
from exceptions import ResponseException
from secrets import spotify_user_id, spotipyUserToken
from urllib import parse
import re
import datetime
from NPRPageParser import NPRPageParser
from ResponsesHandle import ResponseHandle
from PIL import Image
import base64
# note: Playlists can have a maximum of 10,000 tracks each.
# note: You can have as many playlists as you want, but only with 10k tracks each. (confusing info on)
# todo: function to recheck missing songs
# Create functions to check and pass correct cover art to new playlist
# todo: bake special "All tracks found!" or checkmark?, "Missing tracks!" into art?
class NPRPlaylistCreator:
    def __init__(self):
        self.ResponseHandle = ResponseHandle()

    def CreatePlaylist(self, playlistName):
        request_body = json.dumps({"name": playlistName, "public": False})
        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
        response = requests.post(query, data=request_body, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.ResponseHandle.HandleRespone(response)
        response_json = response.json()
        return response_json["id"]

    def AddTracksToPlaylist(self, searchedTracks, playlistID):
        tracksURIs = list()
        for trackList in searchedTracks:
            if (trackList[0]["Found Match Type"] == "HitExactMatch") or (trackList[0]["Found Match Type"] ==  "HitPartialMatch"):
                tracksURIs.append(trackList[0]["Found Track URI"])
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlistID)
        request_data = json.dumps(tracksURIs)
        response = requests.post(query, data=request_data, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.ResponseHandle.HandleRespone(response)

    def AddCoverArtToPlaylist(self, searchedTracks, day, playlistID):
        encoded_string = self.GetNewCover(searchedTracks, day)
        query = "https://api.spotify.com/v1/users/{}/playlists/{}/images".format(spotify_user_id, playlistID) 
        response = requests.put(query, encoded_string, headers={"Authorization": "Bearer {}".format(spotipyUserToken), "Content-Type": "image/jpeg"})
        self.ResponseHandle.HandleRespone(response)

    # Process found and missing artists function?
    def UpdatePlaylistDescription(self, searchedTracks, playlistID, nprURL):
        missedTracksList = list()
        for track in searchedTracks:
            for matchType in track:
                if (matchType["Found Match Type"] == "NoHit") or (matchType["Found Match Type"] == "HitButNoMatch"):
                    # no track found at all from spotify or hit but with neithermatching track or artist
                    # count each of these as a miss to be added to playlist descriptions for others to know
                    missedTracksList.append(matchType)
        if missedTracksList != None:
            newDescription = dict()
            newDescription["description"] = str(nprURL) + " [:(MISSING TRACK(S): " + str(len(missedTracksList))
            for missedTrack in missedTracksList:
                newDescription["description"] += "] " + missedTrack["NPR Track Name"] + " by: " + " ".join(missedTrack["NPR Artist Name"])
                newDescription["description"] += " [LASTCHECKED: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "] <CORRECTIONS: addy@something.com>"
            request_body = json.dumps(newDescription)
        else:
            newDescription = dict()
            newDescription["description"] = nprURL + " [ALL TRACKS FOUND!] [LASTCHECKED: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "] <CORRECTIONS: addy@something.com>"
            request_body = json.dumps(newDescription)
        query = "https://api.spotify.com/v1/playlists/{}".format(playlistID) 
        response = requests.put(query, data=request_body, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        self.ResponseHandle.HandleRespone(response)

    def GetNewCover(self, searchedTracks, day):
        missingTrack = False
        for tracks in searchedTracks:
            for track in tracks:
                if (track["Found Match Type"] == "NoHit") or (track["Found Match Type"] == "HitButNoMatch"):
                    # should include hitbutnomatch?
                    missingTrack = True
                    break
        if missingTrack == True:
            # Missing tracks cover art used instead
            # Create missing cover art
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


