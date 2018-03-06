"""
Configuration file
------------------
- Variables in `UserConfig` section can be changed as needed.
- DO NOT change variables in the `ProgConfig` section.
"""

##---------------------- UserConfig Section -------------------------------------
#Geo configs
#The size of the small images that make the final image
TILE_SIZE = 512		#equations were made by google to suit their 256*256 tile size

#TileRequest configs
#Google maps static API key
API_KEYS = ["AIzaSyAJvgfyNDc-jFJnKkOzq-_A--4ihinEHCs",
"AIzaSyDhgu8wmvJgePWedvjjNQx2Pn33YP5v33w",
"AIzaSyAdS5nawnHjcQl7Cxt_NxbIJoPqA1iPH8M"]

#the name of the temporary work directory
WORK_DIR = "TMP"

#---------------------- ProgConfig Section --------------------------------------
#--- DO NOT CHANGE the values, if you don't know what you're doing, the program 
#--- will not work correctly, if at all!

STATIC_GMAPS_REQ = "https://maps.googleapis.com/maps/api/staticmap?center={LAT},{LONG}&format=png&zoom={ZOOM_LEVEL}&size={TILE_SIZE}&sclae={SCALE}&maptype=roadmap&{MARKERS}&key={API_KEY}"
MARKER_FORMAT = "&markers=color:{COLOR}%7Clabel:{LABEL}%7C{LAT},{LONG}"
KEY_INDEX = 0
QUOTA = 24000	#2500 actually
REQUESTS = 0


if __name__ == '__main__':
	
	pass
