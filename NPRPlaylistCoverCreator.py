from PIL import Image
import base64
# todo: bake special "All tracks found!" or checkmark?, "Missing tracks!" into art?

# Create functions to check and pass correct cover art to new playlist
class NPRPlaylistCoverCreator:
    
    def getNewCover(self, day):
        if (day != "Saturday") and (day != "Sunday"):
            with open("npr_me.jpg", "rb") as im:
                encoded_string = base64.b64encode(im.read())
                return encoded_string    
        elif (day != "Sunday"):
            with open("npr_we_sat.jpg", "rb") as im:
                encoded_string = base64.b64encode(im.read())
                return encoded_string
        else:
            with open("npr_we_sun.jpg", "rb") as im:
                encoded_string = base64.b64encode(im.read())
                return encoded_string