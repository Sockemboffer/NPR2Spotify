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
# note: Playlists can have a maximum of 10,000 tracks each.
# note: You can have as many playlists as you want, but only with 10k tracks each. (confusing info on)
# todo: function to recheck missing songs
# Create functions to check and pass correct cover art to new playlist
# todo: bake special "All tracks found!" or checkmark?, "Missing tracks!" into art?
class NPRPlaylistCreator:

    def CreatePlaylist(self, playlistName):
        request_body = json.dumps({"name": playlistName, "public": False})
        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
        response = requests.post(query, data=request_body, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # check for valid response status
        if response.status_code != 201:
            raise ResponseException(response.status_code)
        response_json = response.json()
        print("-- Playlist created.")
        return response_json["id"]

    def AddTracksToPlaylist(self, searchedTracks, playlistID):
        tracksURIs = list()
        for trackList in searchedTracks:
            if (trackList[0]["Found Match Type"] == "HitExactMatch") or (trackList[0]["Found Match Type"] ==  "HitPartialMatch"):
                tracksURIs.append(trackList[0]["Found Track URI"])
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlistID)
        print(tracksURIs)
        request_data = json.dumps(tracksURIs)
        print(request_data)
        response = requests.post(query, data=request_data, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # check for valid response status
        print(response)
        if response.status_code != 400:
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
        # Some sort of character limit returns response ok but no description will be made
        missedTracksList = list()
        missedDuplicatesRemoved = list()
        missedTrackCount = 0
        for track in searchedTracks:
            duplicateNameCheck = track[0]["NPR Track Name"]
            for matchType in track:
                # no track found at all from spotify or hit but with neithermatching track or artist
                # count each of these as a miss to be added to playlist descriptions for others to know
                if matchType["NPR Track Name"] == duplicateNameCheck:
                    # don't add duplicate to missed list
                elif matchType["NPR Track Name"] != duplicateNameCheck:
                    if matchType["Found Match Type"] == "NoHit":
                        missedTracksList.append(matchType)
                    elif matchType["Found Match Type"] == "HitButNoMatch":
                        missedTracksList.append(matchType)
        print(missedTracksList)

        if missedTracksList != None:
            newDescription = dict()
            newDescription["description"] = str(nprURL) + " [MISSING: " + str(missedTrackCount) + "]"
            for missedTrack in missedTracksList:
                 newDescription["description"] += " [TRACK: " + missedTrack["NPR Track Name"] + " by: " + " ".join(missedTrack["NPR Artist Name"]) + "]"
            newDescription["description"] += " [LASTCHECKED: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + " <CORRECTIONS: addy@something.com>]"
        else:
            newDescription = dict()
            newDescription["description"] = nprURL + " [ALL TRACKS FOUND!] [LASTCHECKED: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "] <CORRECTIONS: addy@something.com>"
        query = "https://api.spotify.com/v1/playlists/{}".format(playlistID) 
        print(json.dumps(newDescription, ensure_ascii=False))
        response = requests.put(query, json.dumps(newDescription, ensure_ascii=False), headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        # check for valid response status
        if response.status_code != 200:
            raise ResponseException(response.status_code)
        print(response.status_code)
        print("-- Playlist description updated.")

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


