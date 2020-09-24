import json
import base64
import requests
import datetime
from ResponsesHandle import ResponseException
from secrets import spotify_user_id, spotipyUserToken
# todo: retry on request submissions

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
        # Removing exessive characters so description has more
        nprURL = nprURL.partition("?")
        for missedTrack in searchedTracks:
            if missedTrack["Found Match Type"] == "NoHit" or missedTrack["Found Match Type"] == "HitButNoMatch":
                missedTracksList.append(missedTrack)
        #print(missedTracksList)
        if missedTracksList != None:
            newDescription = dict()
            newDescription["description"] = str(nprURL[0]) + " [MISSING:" + str(len(missedTracksList)) + "]"
            for track in missedTracksList:
                if track["Found Match Type"] == "HitButNoMatch" and track["NPR Artist Name"][0] == "":
                    newDescription["description"] += " Song: " + track["NPR Track Name"] + " by: ¿Missing?,"
                else:
                    newDescription["description"] += " Song: " + track["NPR Track Name"] + " by: " + ", ".join(track["NPR Artist Name"]) + ","
            newDescription["description"] += " {Checked: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "}--Send fixes to: addy@something.com"
            # Check if description exceeds character limit so we can truncate
            if len(newDescription["description"]) > 300:
                newDescription["description"] = newDescription["description"][:300]
                newEndingDescription =  "<...too many missing.>" + "{Checked: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "}--Send fixes to: addy@something.com"
                newDescription["description"] = newDescription["description"][:len(newEndingDescription)*-1]
                newDescription["description"] += newEndingDescription
        else:
            newDescription = dict()
            newDescription["description"] = str(nprURL) + " [ALL TRACKS FOUND!] {Checked: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "}--Send fixes to: addy@something.com"
        query = "https://api.spotify.com/v1/playlists/{}".format(playlistID)
        response = requests.put(query, json.dumps(newDescription), headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotipyUserToken)})
        if response.status_code != 200:
            raise ResponseException(response.status_code)
        print("!! Truncated description.")

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