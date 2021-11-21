import os
import spotipy
from spotipy import oauth2
# from spotipy import cache_handler
# from spotipy.cache_handler import CacheFileHandler, CacheHandler
import spotipy.util as util

class Secrets:
    def __init__(self):
        # After adding and or modifying any environment variables, RESTART VSCode
        self.SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID') # This apps id
        self.SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET') # This apps secret
        self.SPOTIPY_REDIRECT_URI = os.environ.get('SPOTIPY_REDIRECT_URI') # Points to localhost
        self.spotify_user_id = os.environ.get('SPOTIFY_USER_ID') # The user ID we create the playlists for (NOT username)
        self.scope = 'ugc-image-upload playlist-modify-private' # Type of permissions we need to modify this users playlists
        self.spo = oauth2.SpotifyOAuth(self.SPOTIPY_CLIENT_ID, self.SPOTIPY_CLIENT_SECRET, self.SPOTIPY_REDIRECT_URI, state=None, scope=self.scope, username=self.spotify_user_id)
        self.cacheToken = self.spo.get_access_token()
        # self.spotipySCC = spotipy.SpotifyClientCredentials(self.SPOTIPY_CLIENT_ID, self.SPOTIPY_CLIENT_SECRET)
        # self.sp = spotipy.Spotify(client_credentials_manager=self.spotipySCC)

    # Make sure browser allows popups
    def RefreshMyToken(self):
        if self.cacheToken == None or self.spo.is_token_expired(self.cacheToken):
            print("Cached token is {0}".format(self.cacheToken))
            refreshed_token = self.cacheToken['refresh_token']
            new_token = self.spo.refresh_access_token(refreshed_token)
            print(new_token['access_token'])
            self.sp = spotipy.Spotify(auth=new_token['access_token'])
            return new_token['access_token']
        else:
            return self.cacheToken['access_token']
