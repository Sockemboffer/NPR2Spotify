# My profile: https://open.spotify.com/user/sockemboffer?si=3AvciftURRGu-oFlgt3hpA
# https://open.spotify.com/user/sockemboffer?si=P6WKUn7RQyGHcQdC8gIG0w
import os
import spotipy
import spotipy.util as util

SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID') 
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET') 
SPOTIPY_REDIRECT_URI = os.environ.get('SPOTIPY_REDIRECT_URI') 

spotify_user_id = 'sockemboffer'
scope = 'ugc-image-upload playlist-modify-private'

spotipyUserToken = util.prompt_for_user_token(spotify_user_id, scope, SPOTIPY_CLIENT_ID,
    SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI)

print("Token: " + spotipyUserToken)
# Make sure to fill in your spotify client_secret information
#spotify_token = "BQBNr1RyNq_UgtJkHCNtVKhsbCbNDtMpO0EoUzeOVeNTfmuwl98w6U_ExxHor3_iJrS8mn9Sbrr1lxSHEA-4y2tiq6atWnnYyPVQ3tRj8Gh0NaW4MOQcTGCs01nXKHWXBbXdrj9yKdktJx3JNf2X5G6ig6VidEY8inrN7IBnPVL6IsCRdnqkyGhEoRft5Kvr88N8-U67AGvCBkayPBkWEn7sE4ybsyRSnqaj_LDBgVwIPV0"