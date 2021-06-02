import os
import spotipy
from spotipy import oauth2
import spotipy.util as util

class Secrets:
    def __init__(self):
        self.SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID') 
        self.SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
        self.SPOTIPY_REDIRECT_URI = os.environ.get('SPOTIPY_REDIRECT_URI')
        self.spotify_user_id = '1tnm7cyegqffdjtsz6mt1ozcl'
        self.scope = 'ugc-image-upload playlist-modify-private'
        # self.spotipyUserToken = util.prompt_for_user_token(spotify_user_id, scope, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI)
        self.spo = oauth2.SpotifyOAuth(self.SPOTIPY_CLIENT_ID, self.SPOTIPY_CLIENT_SECRET, self.SPOTIPY_REDIRECT_URI, state=None, scope=self.scope, username=self.spotify_user_id)
        self.spotipySCC = spotipy.SpotifyClientCredentials(self.SPOTIPY_CLIENT_ID, self.SPOTIPY_CLIENT_SECRET)
        self.sp = spotipy.Spotify(client_credentials_manager=self.spotipySCC)

    def RefreshMyToken(self):
        cached_token = self.spo.get_cached_token()
        if self.spo.is_token_expired(cached_token):
            print("Cached token is {0}".format(cached_token))
            refreshed_token = cached_token['refresh_token']
            new_token = self.spo.refresh_access_token(refreshed_token)
            print(new_token['access_token'])
            # also we need to specifically pass `auth=new_token['access_token']`
            self.sp = spotipy.Spotify(auth=new_token['access_token'])
            return new_token['access_token']
        else:
            return cached_token['access_token']

