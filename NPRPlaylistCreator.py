import json
import base64
import requests
import datetime
from ResponsesHandle import ResponseException
from secrets import spotify_user_id, spotipyUserToken
# note: You can have as many playlists as you want, but only with 10k tracks each. (confusing info on)
# todo: function to recheck missing songs?
# todo: make a check if we some how go over playlist name and desciption limits to warn
# todo: Skip days that had no interlude music
class NPRPlaylistCreator:

    def CreatePlaylist(playlistName):
        # Playlist max character name limit is 100
        request_body = json.dumps({"name": playlistName, "public": False})
        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
        response = requests.post(query, data=request_body, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        if response.status_code != 201:
            raise ResponseException(response.status_code)
        response_json = response.json()
        print("-- Playlist created.")
        return response_json

    def AddTracksToPlaylist(searchedTracks, playlistID):
        tracksURIs = list()
        urisData = dict()
        for track in searchedTracks:
            if (track["Found Match Type"] == "HitExactMatch") or (track["Found Match Type"] ==  "HitPartialMatch"):
                tracksURIs.append(track["Found Track URI"])
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlistID)
        urisData["uris"] = tracksURIs
        request_data = json.dumps(urisData)
        response = requests.post(query, request_data, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        if response.status_code != 201:
            raise ResponseException(response.status_code)
        print("-- Playlist tracks added.")

    def AddCoverArtToPlaylist(searchedTracks, day, playlistID):
        encoded_string = NPRPlaylistCreator.GetNewCover(searchedTracks, day)
        query = "https://api.spotify.com/v1/users/{}/playlists/{}/images".format(spotify_user_id, playlistID) 
        response = requests.put(query, encoded_string, headers={"Authorization": "Bearer {}".format(spotipyUserToken), "Content-Type": "image/jpeg"})
        if response.status_code != 202:
            raise ResponseException(response.status_code)
        print("-- Playlist cover image added.")

    def UpdatePlaylistDescription(searchedTracks, playlistID, nprURL):
        # 300 character limit playlist desciption
        # returns response ok if over limit, but no description will be made.
        missedTracksList = list()
        # Removing some areas of the link that aren't required for more description space
        splitArchiveURL = nprURL.rsplit("?", maxsplit=1)
        print(splitArchiveURL)
        splitMorningEditionURL = splitArchiveURL[0].rsplit("morning", maxsplit=1)
        print(splitMorningEditionURL)
        splitWeekendEditionURL = splitMorningEditionURL[0].rsplit("weekend", maxsplit=1)
        print(splitWeekendEditionURL)
        nprURL = splitWeekendEditionURL[0]
        print(nprURL)
        for missedTrack in searchedTracks:
            if missedTrack["Found Match Type"] == "NoHit" or missedTrack["Found Match Type"] == "HitButNoMatch":
                missedTracksList.append(missedTrack)
        print(missedTracksList)
        if missedTracksList != None:
            newDescription = dict()
            newDescription["description"] = str(nprURL) + " [MISSING: " + str(len(missedTracksList)) + "]"
            for track in missedTracksList:
                print(track)
                if track["Found Match Type"] == "HitButNoMatch":
                    newDescription["description"] += " Song: " + track["NPR Track Name"] + " by: " + ", ".join(track["NPR Artist Name"]) + ","
                else:
                    newDescription["description"] += " Song: " + track["NPR Track Name"] + " by: " + ", ".join(track["NPR Artist Name"]) + ","
            newDescription["description"] += " [Last checked: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + ", Corrections: addy@something.com"
        else:
            newDescription = dict()
            newDescription["description"] = str(nprURL) + " [ALL TRACKS FOUND!] [Last checked: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + ", Corrections: addy@something.com"
        print(newDescription)
        query = "https://api.spotify.com/v1/playlists/{}".format(playlistID)
        response = requests.put(query, json.dumps(newDescription), headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        print(response)
        if response.status_code != 200:
            raise ResponseException(response.status_code)
        print("-- Playlist description updated.")

    def GetNewCover(searchedTracks, day):
        missingTrack = False
        for track in searchedTracks:
            if (track["Found Match Type"] == "NoHit") or (track["Found Match Type"] == "HitButNoMatch"):
                missingTrack = True
                break
        if missingTrack == True:
            print("-- Missing Tracks jpg selected.")
            if (day != "Saturday") and (day != "Sunday"):
                with open("npr_me-missingtracks.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string    
            elif (day != "Sunday"):
                with open("npr_we_sat-missingtracks.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string
            else:
                with open("npr_we_sun-missingtracks.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string
        else:
            print("-- All Tracks found jpg selected.")
            if (day != "Saturday") and (day != "Sunday"):
                with open("npr_me-alltracks.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string    
            elif (day != "Sunday"):
                with open("npr_we_sat-alltracks.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string
            else:
                with open("npr_we_sun-alltracks.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string