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

# todo: re-check parsed page for missing tracks to research
    # check if playlist exsists
    # todo: notify when previously not found track is found
# todo: organize queries 
# todo: stripping: feat., featuring, etc. from song names

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
            if "Playlist Name" in dic:
                playlistName = str(dic.get("Playlist Name"))
            if "Page Link" in dic:
                self.nprPageLink = str(dic.get("Page Link"))
            if "Day" in dic:
                self.articleDay = str(dic.get("Day"))
        # Create A New Playlist that we can fill up with interlude songs
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
                query = "https://api.spotify.com/v1/users/{}/playlists/{}/images".format(spotify_user_id, self.playListID) 
                response = requests.put(
                    query,
                    encoded_string,
                    headers={
                        "Authorization": "Bearer {}".format(spotipyUserToken),
                        "Content-Type": "image/jpeg"})
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
                #print(response)
        #print(response_json["id"])
        return self.playListID

    def get_spotify_uri(self, artistList):
        # building uri list to use later in playlist fill-up
        jsonData = self.get_json_data()
        query = ""
        for dic in artistList:
            if "Interlude Artist" in dic:
                artists = dic.get("Interlude Artist")
                #print(len(artists))
            if "Interlude Song" in dic:
                track = dic.get("Interlude Song")
                #print(track)

            # Initial search raw track and 1st artist name
            query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=5".format(
                    parse.quote('track:' + '"' + track + '"' + ' ' + 'artist:"' + artists[0] + '"'))
            print(track + " by: " + artists[0])
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
                #print("NO BRACKETS: " + json.dumps(response_json, indent=4) + '\n')

            if response_json["tracks"]["total"] == 0:
                # strip () from track name, search literal track name + artist type
                trackNoBracketsAndBraces = trackNoBrackets.translate({ord(i): None for i in '()'})
                query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=5".format(
                        parse.quote('"' + trackNoBracketsAndBraces + '"' + ' ' + 'artist:"' + artists[0] + '"'))
                print(trackNoBracketsAndBraces + ' ' + 'by: ' + artists[0])
                response = requests.get(
                query,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(spotipyUserToken)})
                response_json = response.json()
                #print("NO BRACKETS AND NO ARTIST: " + json.dumps(response_json, indent=4) + '\n')

            if response_json["tracks"]["total"] == 0:
                # strip () from track name, search literal track name + NO artist
                # When no artist used, double check found track's artist matches npr page artist
                query = "https://api.spotify.com/v1/search?q={}&type=track&market=US&limit=5".format(
                        parse.quote('"' + trackNoBracketsAndBraces + '"'))
                print(trackNoBracketsAndBraces + ' ' + 'by: None')
                response = requests.get(
                query,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(spotipyUserToken)})
                response_json = response.json()
                if (response_json["tracks"]["total"] == 0):
                    print(trackNoBracketsAndBraces + ' ' + 'by: None')
                else:
                    print("<!check!> " + response_json["tracks"]["items"][0]["name"] + " by: " + response_json["tracks"]["items"][0]["artists"][0]["name"] + " <=?=> " + trackNoBracketsAndBraces + " by: " + artists[0])

            if response_json["tracks"]["total"] == 0:
                # strip words from songs like featuring, edit, original, etc.
                stopwords = ['feat.','original','edit','featuring','feature']
                querywords = trackNoBracketsAndBraces.split()
                resultwords  = [word for word in querywords if word.lower() not in stopwords]
                self.result = ' '.join(resultwords)
                query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=5".format(
                        parse.quote('"' + self.result + '"' + ' ' + 'artist:"' + artists[0] + '"'))
                print(self.result + ' ' + 'by: ' + artists[0])
                response = requests.get(
                query,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(spotipyUserToken)})
                response_json = response.json()
                #print("NO BRACKETS AND NO ARTIST: " + json.dumps(response_json, indent=4) + '\n')

            if response_json["tracks"]["total"] == 0:
                # strip words from songs like featuring, edit, original, etc. + search WITHOUT type artist
                # When no artist used, double check found track's artist matches npr page artist
                query = "https://api.spotify.com/v1/search?q={}&type=track&market=US&limit=5".format(
                        parse.quote('"' + self.result + '"'))
                response = requests.get(
                query,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(spotipyUserToken)})
                response_json = response.json()
                if (response_json["tracks"]["total"] == 0):
                    print(self.result + ' ' + 'by: None')
                else:
                    print("<!check!> " + response_json["tracks"]["items"][0]["name"] + " by: " + response_json["tracks"]["items"][0]["artists"][0]["name"] + " <=?=> " + self.result + " by: " + artists[0])

            # Added missed track scan date check back into json
            # No more search configurations left
            if (response_json["tracks"]["total"] == 0) or (response_json["tracks"]["items"][0]["artists"][0]["name"] != artists[0]):
                missedTrack = " ••••••> " + "MISSING: " + track + " by: " + ", ".join(artists) + '\n'
                self.missedTracksList.append(missedTrack)
                print(missedTrack)
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
                #print("NoBracketsAndSplit: " + json.dumps(response_json, indent=4) + '\n')
            else:
                # found artist and need to put it's uri back into json file
                print("| Found Track: " + str(response_json["tracks"]["items"][0]["name"])  + ", by: "
                    + response_json["tracks"]["items"][0]["artists"][0]["name"] + '\n')
                self.all_uri_info.append(response_json["tracks"]["items"][0]["uri"])
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
            # Update playlist description
            self.result = "" # gross
            if (len(self.missedTracksList) > 0):
                request_body = json.dumps({"description": self.nprPageLink + " [:(MISSING TRACK(S): "
                + str(len(self.missedTracksList)) + "] " + " ".join(self.missedTracksList) + " [LASTCHECKED: " 
                + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "]" + " [CORRECTIONS: addy@something.com]"})
            else:
                request_body = json.dumps({"description": self.nprPageLink + " [ALL TRACKS FOUND!] "
                + " [LASTCHECKED: " + str(datetime.datetime.now().__format__("%Y-%m-%d")) + "]" 
                + " [CORRECTIONS(it's not perfect): addy@something.com]"})
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