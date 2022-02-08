from logging import exception
from NPRPageParser import NPRPageParser
import json
import base64
import time
from datetime import timedelta
import requests
import datetime
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from ratelimit import limits, RateLimitException
from backoff import on_exception, expo
import Secrets

NUMBER_OF_CALLS = 1
IN_SECONDS = 1

# TODO Figure out what is causing:
# Exception has occurred: ConnectionError
# ('Connection aborted.', ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None))

class NPRPlaylistCreator:

    def __init__(self):
        self.requestSession = requests.Session()
        self.secrets = Secrets.Secrets()
        self.retries = Retry(total=10, backoff_factor=1, status_forcelist=[ 204, 304, 400, 401, 403, 404, 500, 502, 503, 504 ])
        self.requestSession.mount('https://api.spotify.com/', HTTPAdapter(max_retries=self.retries, pool_maxsize=25))


    @on_exception(expo, RateLimitException, max_tries=8)
    @limits(calls=NUMBER_OF_CALLS, period=IN_SECONDS)
    def CreatePlaylist(self, playlistName, user_id):
        # Playlist name limit is 100 char
        # time.sleep(1) # maybe a delay soon after the last search track but before we create playlist will help prevent 10054 error??
        request_body = json.dumps({"name": playlistName, "public": False})
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.secrets.SPOTIFY_USER_ID_ATC)
        response = self.requestSession.post(query, data=request_body, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.secrets.GiveToken(user_id))})
        if response.status_code not in [200, 201, 202]:
            raise Exception('API response code: {0}, {1}'.format(response.status_code, response.text))
        print("-- Playlist created.")
        return response.json()

    @on_exception(expo, RateLimitException, max_tries=8)
    @limits(calls=NUMBER_OF_CALLS, period=IN_SECONDS)
    def AddTracksToPlaylist(self, editionDayData, user_id):
        tracksURIs = list()
        for item in editionDayData:
            for entry in item:
                if entry == "Result Track-Match Percent":
                    if item["Result Track-Match Percent"] >= 0.5 and item["Result Artists-Match Percent"] >= 0.5:
                        tracksURIs.append(item["Result Track URI"])
        if len(tracksURIs) != 0:
            urisData = dict()
            urisData["uris"] = tracksURIs
            request_data = json.dumps(urisData)
            query = "https://api.spotify.com/v1/playlists/{}/tracks".format(editionDayData[0]['Playlist URI'])
            response = self.requestSession.post(query, request_data, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.secrets.GiveToken(user_id))})
            if response.status_code not in [200, 201, 202]:
                raise Exception('API response: {}'.format(response.status_code))
            print("-- Playlist tracks added.")

    # TODO understand I'm calling replace when I haven't actually created the playlist
    @on_exception(expo, RateLimitException, max_tries=8)
    @limits(calls=NUMBER_OF_CALLS, period=IN_SECONDS)
    def ReplaceTracksInPlaylist(self, editionDayData, user_id):
        tracksURIs = list()
        for item in editionDayData:
            for entry in item:
                if entry == "Result Track-Match Percent":
                    if item["Result Track-Match Percent"] >= 0.5 and item["Result Artists-Match Percent"] >= 0.5:
                        tracksURIs.append(item["Result Track URI"])
        urisData = dict()
        urisData["uris"] = tracksURIs
        request_data = json.dumps(urisData)
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(editionDayData[0]['Playlist URI'])
        response = self.requestSession.put(query, request_data, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.secrets.GiveToken(user_id))})
        if response.status_code not in [200, 201, 202]:
            raise Exception('API response: {}'.format(response.status_code))
        response_json = response.json()
        editionDayData[0]["Snapshot ID"] = response_json["snapshot_id"]
        print("-- Playlist tracks replaced.")
        return editionDayData

    @on_exception(expo, RateLimitException, max_tries=8)
    @limits(calls=NUMBER_OF_CALLS, period=IN_SECONDS)
    def AddCoverArtToPlaylist(self, editionDayData, user_id):
        encoded_string = NPRPlaylistCreator.GetNewCover(editionDayData)
        query = "https://api.spotify.com/v1/users/{}/playlists/{}/images".format(self.secrets.SPOTIFY_USER_ID_ATC, editionDayData[0]['Playlist URI']) 
        response = self.requestSession.put(query, encoded_string, headers={"Authorization": "Bearer {}".format(self.secrets.GiveToken(user_id)), "Content-Type": "image/jpeg"})
        if response.status_code not in [200, 201, 202]:
            raise Exception('API response: {}'.format(response.status_code))
        print("-- Playlist cover image added.")

    # playlist descriptions have a 300 char limit
    @on_exception(expo, RateLimitException, max_tries=8)
    @limits(calls=NUMBER_OF_CALLS, period=IN_SECONDS)
    def UpdatePlaylistDescription(self, editionDayData, user_id):
        missedTracksList = list()
        foundTracks = list()
        for item in editionDayData:
            for entry in item:
                if entry == "Result Track-Match Percent":
                    if item["Result Track-Match Percent"] >= 0.5:
                        foundTracks.append(item)
                    else:
                        missedTracksList.append(item)
        newDescription = dict()
        if len(missedTracksList) == 0 and len(foundTracks) == 0:
            newDescription["description"] = "🤔 Empty: No interludes noted."
        elif len(missedTracksList) != 0: 
            newDescription["description"] = "😭 Missing: " + str(len(missedTracksList)) + " of " + str(len(foundTracks) + len(missedTracksList)) + " "
        else:
            newDescription["description"] = "🤩 Found: " + str(len(foundTracks)) + " of " + str(len(foundTracks)) + " "
        newDescription["description"] += "🌐 " + editionDayData[0]["Page Link"] + " "
        newDescription["description"] += "🤖 Send corrections to @NPR2Spotify on twitter "
        newDescription["description"] += "💸 Support your local NPR station. "
        newDescription["description"] += "📻 https://www.npr.org/donations/support "
        newDescription["description"] += "💻 https://www.github.com/Sockemboffer/NPR2Spotify "
        newDescription["description"] += "Created: " + str(datetime.datetime.now().__format__("%Y-%m-%d"))
        query = "https://api.spotify.com/v1/playlists/{}".format(editionDayData[0]['Playlist URI'])
        response = self.requestSession.put(query, json.dumps(newDescription), headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.secrets.GiveToken(user_id))})
        if response.status_code not in [200, 201, 202]:
            raise Exception('API response: {}'.format(response.status_code))
        print("-- Playlist description updated.")

    def GetNewCover(edition: list):
        if edition[0]["Edition"] != "All Things":
            if (edition[0]["Day"] != "Sat") and (edition[0]["Day"] != "Sun"):
                with open("Edition Logos/npr_me.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string    
            elif (edition[0]["Day"] != "Sun"):
                with open("Edition Logos/npr_we_sat.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string
            else:
                with open("Edition Logos/npr_we_sun.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string
        else:
            with open("Edition Logos/npr_atc.jpg", "rb") as im:
                    encoded_string = base64.b64encode(im.read())
                    return encoded_string
    
    # @on_exception(expo, RateLimitException, max_tries=8)
    # @limits(calls=NUMBER_OF_CALLS, period=IN_SECONDS)
    def ChangePlaylistToPublic(self, leftOffDate: datetime, today: datetime, projectPrefix: str, projectName: str, user_id: str):
        startDate = leftOffDate
        if projectPrefix != "ATC":
            while startDate <= today:
                projectPath = projectPrefix + " Article Data/{0}/{1}/".format(startDate.year, startDate.strftime("%m"))
                morningEditionFileName = projectPrefix + " {0} {1} {2}".format(startDate.strftime("%Y-%m-%d"), startDate.strftime("%a"), projectName)
                weekendEditionFileName = projectName + " {0} {1} {2}".format(startDate.strftime("%Y-%m-%d"), startDate.strftime("%a"), projectName)
                fileType = ".json"
                # Load article data from disk
                if startDate.weekday() <= 4:
                    editionDay = NPRPageParser.LoadJSONFile(projectPath + morningEditionFileName + fileType)
                else:
                    editionDay = NPRPageParser.LoadJSONFile(projectPath + weekendEditionFileName + fileType)
                if editionDay == None:
                    startDate = startDate + timedelta(days=+1)
                    continue
                elif editionDay[0]["Playlist URI"] == None:
                    print("Uhhhh..........")
                    exception(editionDay)
                else:
                    editionPlaylistURI = editionDay[0]["Playlist URI"]
                    query = "https://api.spotify.com/v1/playlists/{}".format(editionPlaylistURI)
                    payload = {"public": True}
                    response = self.requestSession.put(query, json.dumps(payload), headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.secrets.GiveToken(user_id))})
                    if response.status_code not in [200, 201, 202]:
                        raise Exception('API response: {}'.format(response.status_code))
                    print("-- Day {0} at {1} now public.\n".format(startDate, editionDay[0]["Playlist Link"]))
                    startDate = startDate + timedelta(days=+1)
        else:
            while startDate <= today:
                projectPath = projectPrefix + " Article Data/{0}/{1}/".format(startDate.year, startDate.strftime("%m"))
                ATCFileName = projectPrefix + " {0} {1} {2}".format(startDate.strftime("%Y-%m-%d"), startDate.strftime("%a"), projectName)
                fileType = ".json"
                # Load article data from disk
                editionDay = NPRPageParser.LoadJSONFile(projectPath + ATCFileName + fileType)
                if editionDay == None:
                    startDate = startDate + timedelta(days=+1)
                    continue
                elif editionDay[0]["Playlist URI"] == None:
                    print("Uhhhh..........")
                    exception(editionDay)
                else:
                    editionPlaylistURI = editionDay[0]["Playlist URI"]
                    query = "https://api.spotify.com/v1/playlists/{}".format(editionPlaylistURI)
                    payload = {"public": True}
                    response = self.requestSession.put(query, json.dumps(payload), headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.secrets.GiveToken(user_id))})
                    if response.status_code not in [200, 201, 202]:
                        raise Exception('API response: {}'.format(response.status_code))
                    print("-- Day {0} at {1} now public.\n".format(startDate, editionDay[0]["Playlist Link"]))
                    startDate = startDate + timedelta(days=+1)