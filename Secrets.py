import os
import spotipy

# Make sure browser allows popups
# After adding and or modifying any environment variables, RESTART VSCode
class Secrets:
    def __init__(self):
        self.SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID') # This apps id from dashboard login
        self.SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET') # This apps secret from dashboard login
        self.SPOTIPY_REDIRECT_URI = os.environ.get('SPOTIPY_REDIRECT_URI') # Points to redirect URI (http://localhost:8888/callback)
        self.SPOTIFY_USER_ID = os.environ.get('SPOTIFY_USER_ID') # The user ID/username listed on the profile page
        self.scope = 'ugc-image-upload playlist-modify-private' # Type of permissions we need to modify this users playlists
        self.oauthManager = spotipy.SpotifyOAuth(self.SPOTIPY_CLIENT_ID, self.SPOTIPY_CLIENT_SECRET, self.SPOTIPY_REDIRECT_URI, None, self.scope, None, self.SPOTIFY_USER_ID, None, True)
    
    def GiveToken(self):
        token = spotipy.util.prompt_for_user_token(self.SPOTIFY_USER_ID, self.scope, self.SPOTIPY_CLIENT_ID, self.SPOTIPY_CLIENT_SECRET, self.SPOTIPY_REDIRECT_URI, None, self.oauthManager, True)
        return token