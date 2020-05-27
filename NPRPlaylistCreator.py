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

# todo: generate playlist title from multiple npr pages
    # check if playlist exsists
# todo: create search types to help narrow down a track when none found on default search
# todo: notify when previously not found track is found
# todo: playlist description confirms if all were found

class CreatePlaylist:
    def __init__(self):
        self.all_song_info = list()
        self.all_uri_info = list()
        self.songLastChecked = ""
        self.playListID = ""
        self.nprPageLink = ""
        self.playListDescription = ""
        self.articleDay = ""
        self.missedTracksList = list()

    def get_json_data(self):
        with open('NPRPageParser.json', "r", encoding='utf-8') as json_file:
            try:
                return json.load(json_file)
            except ValueError as e:
                print('invalid json: %s' % e)
                return None # or: raise

    def get_artist_data(self):
        jsonData = self.get_json_data()
        for entry in jsonData:
            for value in entry:
                if isinstance(value, dict):
                    self.all_song_info.append(value)
        # print(self.all_song_info)
        return self.all_song_info

    def create_playlist(self):
        jsonData = self.get_json_data()
        for dic in jsonData:
            if "Day" in dic:
                self.articleDay = str(dic.get("Day"))
            if "Date Text" in dic:
                dateText = str(dic.get("Date Text"))
            if "Page Link" in dic:
                self.nprPageLink = str(dic.get("Page Link"))
            if "Edition" in dic:
                editionText = str(dic.get("Edition"))

        # Create A New Playlist that we can fill up with interlude songs
        request_body = json.dumps({
            "name": self.articleDay + ", " + dateText + " for NPR " + editionText,
            "public": False})

        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id) 
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotipyUserToken)})
        response_json = response.json()
        #print("in file open ===============")
        with open('NPRPageParser.json', 'w', encoding='utf-8') as json_file:
            #print(jsonData)
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
            #print(json.dumps(jsonData))
            json.dump(jsonData, json_file, ensure_ascii=False, indent=4)
            json_file.close()
        #print(response_json)
        self.playListID = response_json["id"]
        if (self.articleDay != "Saturday") and (self.articleDay != "Sunday"):
            with open("npr_me.jpg", "rb") as im:
                encoded_string = base64.b64encode(im.read())
                #print(im)
                query = "https://api.spotify.com/v1/users/{}/playlists/{}/images".format(spotify_user_id, self.playListID) 
                response = requests.put(
                    query,
                    encoded_string,
                    headers={
                        "Authorization": "Bearer {}".format(spotipyUserToken),
                        "Content-Type": "image/jpeg"})
                #editionImage.close()
                #response_json = response.json()
                #print(response)
        elif (self.articleDay != "Sunday"):
            with open("npr_we_sat.jpg", "rb") as im:
                encoded_string = base64.b64encode(im.read())
                #print(im)
                query = "https://api.spotify.com/v1/users/{}/playlists/{}/images".format(spotify_user_id, self.playListID) 
                response = requests.put(
                    query,
                    encoded_string,
                    headers={
                        "Authorization": "Bearer {}".format(spotipyUserToken),
                        "Content-Type": "image/jpeg"})
                #editionImage.close()
                #response_json = response.json()
                #print(response)
        else:
            with open("npr_we_sun.jpg", "rb") as im:
                encoded_string = base64.b64encode(im.read())
                #print(im)
                query = "https://api.spotify.com/v1/users/{}/playlists/{}/images".format(spotify_user_id, self.playListID) 
                response = requests.put(
                    query,
                    encoded_string,
                    headers={
                        "Authorization": "Bearer {}".format(spotipyUserToken),
                        "Content-Type": "image/jpeg"})
                #editionImage.close()
                #response_json = response.json()
                #print(response)

        #print(response_json)
        # playlist id
        #print(response_json["id"])
        return self.playListID

    def get_spotify_uri(self, artistList):
        # building uri list to use later in playlist fill-up
        jsonData = self.get_json_data()
        foundTracks = list()
        multipleArtists = ""
        query = ""
        for dic in artistList:
            if "Interlude Artist" in dic:
                artists = dic.get("Interlude Artist")
                #print(len(artists))
            if "Interlude Song" in dic:
                track = dic.get("Interlude Song")
                #print(track)

            # taking only the first result from a track + artist search which is not always a match
            # 1, 2, or 3 common word names will return multiple hits where the 1st match is likely not it
            # Unique names more likely a match but small chance composer broadway/orchistra aren't artist name
            # who performed the version found on npr page
            # try literal artist + literal track search
            # try each artist + literal track search
            # try stripping character names
            # try stripping: feat., featuring, etc. from song names
            # try cutting/split out text found in: (), []
            #if len(artists) > 1:
            query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=5".format(
                    parse.quote('track:' + '"' + track + '"' + ' ' + 'artist:"' + artists[0] + '"'))
            print(track + " by: " + artists[0])
            # else:
            #     query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=5".format(
            #             parse.quote('track:' + '"' + track + '"' + ' ' + 'artist:"' + artists[0][1] + '"'))
            #     print(query)
            
            response = requests.get(
                query,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(spotipyUserToken)})
            response_json = response.json()
            #print("=====================================" + json.dumps(response_json, indent=4) + r'\n')

            if response_json["tracks"]["total"] == 0:
                # strip [] from track names and research literal & WITH artist search
                trackNoBrackets = track.translate({ord(i): None for i in '[]'})
                #print("TrackNoBrackets: " + trackNoBrackets)
                query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=5".format(
                        parse.quote('track:' + '"' + trackNoBrackets + '"' + ' ' + 'artist:"' + artists[0] + '"'))
                print(trackNoBrackets + " by: " + artists[0])
                response = requests.get(
                query,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(spotipyUserToken)})
                response_json = response.json()
                #print(response_json)
                #print(response_json)
                #print("NO BRACKETS: " + json.dumps(response_json, indent=4) + '\n')

            if response_json["tracks"]["total"] == 0:
                # strip [] from track names and research literal & WITHOUT artist search
                query = "https://api.spotify.com/v1/search?q={}&type=track&market=US&limit=5".format(
                        parse.quote('track:' + '"' + trackNoBrackets + '"'))
                print(trackNoBrackets + " By: None")
                response = requests.get(
                query,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(spotipyUserToken)})
                response_json = response.json()
                #print(response_json)
                #print("NO BRACKETS AND NO ARTIST: " + json.dumps(response_json, indent=4) + '\n')

            if response_json["tracks"]["total"] == 0:
                # strip [] from track names, split at "(", with artists
                trackNoBracketsAndSplit = re.split('[(]', trackNoBrackets)
                query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=5".format(
                        parse.quote('track:' + '"' + trackNoBracketsAndSplit[0] + '"' + ' ' + 'artist:"' + artists[0] + '"'))
                print(trackNoBracketsAndSplit[0] + " by: " + artists[0])
                response = requests.get(
                query,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(spotipyUserToken)})
                response_json = response.json()
                #print(response_json)
                #print(response_json)
                #print("NoBracketsAndSplit: " + json.dumps(response_json, indent=4) + '\n')

            if response_json["tracks"]["total"] != 0:
                print("| Found Track: " + str(response_json["tracks"]["items"][0]["name"])  + ", By: "
                    + response_json["tracks"]["items"][0]["artists"][0]["name"] + '\n')
                self.all_uri_info.append(response_json["tracks"]["items"][0]["uri"])
                # insert track uri back into jsonData
                with open('NPRPageParser.json', 'w', encoding='utf-8') as json_file:
                    for entry in jsonData:
                        for value in entry:
                            if isinstance(value, dict):
                                #print(value)
                                for k, v in value.items():
                                    if v == track:
                                        # print(k)
                                        for k, v in value.items():
                                            if k == "Spotify URI":
                                                v = response_json["tracks"]["items"][0]["uri"]
                                                value[k] = v
                                                #print(k)
                                            if k == "Last Checked":
                                                self.songLastChecked = str(datetime.datetime.now().__format__("%Y-%m-%d %H:%M:%S"))
                                                value[k] = self.songLastChecked
                                                #print(k)
                                        
                    #print(jsonData)
                    json.dump(jsonData, json_file, ensure_ascii=False, indent=4)
                    json_file.close()
            else:
                missedTrack = "••••••>" + "MISSING: " + track + " " + "by: " + ", ".join(artists)
                print(missedTrack)
                self.missedTracksList.append(missedTrack) 
                #print(self.missedTracksList)
                # insert last checked back into json file
                with open('NPRPageParser.json', 'w', encoding='utf-8') as json_file:
                    for entry in jsonData:
                        for value in entry:
                            if isinstance(value, dict):
                                #print(value)
                                for k, v in value.items():
                                    if v == track:
                                        # print(k)
                                        for k, v in value.items():
                                            if k == "Last Checked":
                                                dt = str(datetime.datetime.now().__format__("%Y-%m-%d %H:%M:%S"))
                                                v = dt
                                                value[k] = v
                                                #print(k)
                    #print(response)
                    json.dump(jsonData, json_file, ensure_ascii=False, indent=4)
                    json_file.close()
            # Update playlist description        
            request_body = json.dumps({"description": self.nprPageLink + " " + " ".join(self.missedTracksList)
                    + " [LASTCHECKED: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "]",})
            query = "https://api.spotify.com/v1/playlists/{}".format(self.playListID) 
            response = requests.put(
                query,
                data=request_body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(spotipyUserToken)})
        return self.all_uri_info

    def add_song_to_playlist(self, playListID, uriList):
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playListID)
        request_data = json.dumps(uriList)
        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotipyUserToken)})

        # check for valid response status
        if response.status_code != 200 or response.status_code != 201:
            print(response)
            return response
        else:
            raise ResponseException(response.status_code)
            print(response_json)
            return response_json

newPlaylistCreator = CreatePlaylist()
dayInterludeList = newPlaylistCreator.get_artist_data()
newPlaylist = newPlaylistCreator.create_playlist()
spotifyURIs = newPlaylistCreator.get_spotify_uri(dayInterludeList)
spotifyResponse = newPlaylistCreator.add_song_to_playlist(newPlaylist, spotifyURIs)