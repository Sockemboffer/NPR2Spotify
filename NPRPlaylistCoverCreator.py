# todo: function to update cover art on already made playlist
    # todo: bake special "All tracks found!", "Missing tracks!" into art?

# Create functions to check and pass correct cover art to new playlist
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