# My profile: https://open.spotify.com/user/sockemboffer?si=3AvciftURRGu-oFlgt3hpA
# https://open.spotify.com/user/sockemboffer?si=P6WKUn7RQyGHcQdC8gIG0w
import os
import spotipy
import spotipy.util as util

SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID') 
SPOTIPY_CLIENT_SECRET = "test"
SPOTIPY_REDIRECT_URI = os.environ.get('SPOTIPY_REDIRECT_URI') 

spotify_user_id = 'sockemboffer'
scope = 'ugc-image-upload playlist-modify-private'

spotipyUserToken = util.prompt_for_user_token(spotify_user_id, scope, SPOTIPY_CLIENT_ID,
    SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI)