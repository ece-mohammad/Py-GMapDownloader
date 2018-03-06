"""

session request format
https://www.googleapis.com/tile/v1/createSession?key={YOUR_API_KEY}

zoom levels: 0 to 20

pixel_coordinate = world_cordiante * 2^zoom_level
num_of_tiles = (2^zoom_level)^2 or 2^(2*zoom_level)

request body (JSON) example:
-----------------------------
{
  "mapType": "roadmap",
  "language": "en-EN",
  "region": "eg",
  "layerTypes": [ "layerRoadmap", "layerStreetview" ],
  "overlay":  true,
  "scale": "scaleFactor1x"
}
mapType: roadmap >> standard for google maps
language: language on the tiles/map
region: my location (location of end-user)
scale: the size of map elements, such as road labels
highDpi:  Specifies whether to return high DPI tiles.
	If true,the number of pixels in each of the x and y dimensions are multiplied by the scale factor value
	not effective with scale factor x1
layerTypes: An array of values representing the layer type(s) to be added to the map

Response for session request:
-------------------------
{
  "session": "IgAAAHGU9jnAU4KOAfwY3Bcd6eH_WxQsyocSBAdUnAr9pnvTTNXtF9c_27RBo94ytEXTDg",
  "expiry": 1361828036,
  "tileWidth": 256,
  "tileHeight": 256,
  "imageFormat": "png"
}

Tile request:
------------
https://www.googleapis.com/tile/v1/tiles/
	z/
	x/			
	y
  ?session=session token
  &key=YOUR_API_KEY
 
 z: zoom level 
 x:	x tile co-ordinate of the tile
 y:	y tile co-ordinate of the tile
 
 
 Coordinate functions:
 ---------------------
 var TILE_SIZE = 256;
function fromLatLngToPoint(latLng) {
  var mercator = -Math.log(Math.tan((0.25 + latLng.lat() / 360) * Math.PI));
  return {
    x: TILE_SIZE * (latLng.lng() / 360 + 0.5),
    y: TILE_SIZE / 2 * (1 +  mercator / Math.PI)
  };
}

function fromLatLngToTileCoord(latLng, zoom) {
  var point = fromLatLngToPoint(latLng);
  var scale = Math.pow(2, zoom);

  return {
    x: Math.floor(point.x * scale / TILE_SIZE),
    y: Math.floor(point.y * scale / TILE_SIZE),
    z: zoom
  };
}

View port request:
------------------
https://www.googleapis.com/tile/v1/viewport
  ?session=session token
  &zoom=zoom
  &north=N
  &south=S
  &east=E
  &west=W
  &key=YOUR_API_KEY

  N,S,E,W are max lat/long values in degrees (-/+90, -/+180)

 View Port Response:
 -------------------
 {
  "copyright": "Map data ©2013 Google",
  "maxZoomRect": [
    {
      "maxZoom": 8,
      "south": -90,
      "west": -180
      "north": 90,
      "east": 180
    }, ...
  ]
}
 
Errors:
--------
{
  "error": {
    "errors": [
      {
        "domain": "global",
        "reason": "required",
        "message": ""\"mapType\" is a required field"",
        "location": "mapType"
      }
    ],
    "code": 400,
    "message": ""
  }
}
domain: most errors fall in global domain
reason: reason of error:
		[required(missing value),
		notFound(error in x,y,z),
		invalidCredentials,
		authTokenExpired,
		badRequest,
		quotaExceeded,
		rateLimitExceeded ]
location: exact parameter name of the offending value.
code: HTTP code
 
###retry requests with exponential backoff.
"""

import config, Geo
from FileManager import FileManager as fm

from urllib import request, error, parse
from http.client import HTTPResponse
from http import HTTPStatus
import time, os, sys, gc

API_KEYS = config.API_KEYS
STATIC_GMAPS_REQ = config.STATIC_GMAPS_REQ
MARKER_FORMAT = config.MARKER_FORMAT
KEY_INDEX = config.KEY_INDEX
QUOTA = config.QUOTA
REQUESTS = 0

WORK_DIR = config.WORK_DIR

class MapReq(object):
	
	def __init__(self, upper_left, lower_right, zoom=17, scale=2, size=config.TILE_SIZE, key=0, name='map'):
		assert isinstance(upper_left, Geo.UMTPoint) and isinstance(lower_right, Geo.UMTPoint),\
		"ValueError! Upper_left and Lower_right must be Geo.UMTPoint instances!"
		
		self.MAP = Geo.Map(upper_left, lower_right, zoom)
		self.zoom_level = zoom
		self.scale = 2
		self.tile_size = size
		self.key = 0
		self.map_name = name
		fm.GoToWorkDir()
		self.markers = self._add_markers()
		
		
	def _add_markers(self):
		
		marker_a = self.MAP.upper_left_corner
		marker_b = self.MAP.lower_right_corner
		
		markers = [ {"COLOR":"black", "LABEL":"A", "LAT":marker_a.lat, "LONG":marker_a.long},
					{"COLOR":"red", "LABEL":"B", "LAT":marker_a.lat, "LONG":marker_b.long},
					{"COLOR":"green", "LABEL":"C", "LAT":marker_b.lat, "LONG":marker_b.long},
					{"COLOR":"blue", "LABEL":"D", "LAT":marker_b.lat, "LONG":marker_a.long},
				]
		
		line = 'marker: {LABEL}, color: {COLOR}, lat:{LAT}, long:{LONG}\n'
		with open(self.map_name+'_markers.txt','w', encoding='utf-8') as marker_file:
			for marker in markers:
				marker_file.write(line.format(**marker))
		
		markers = ''.join([MARKER_FORMAT.format(**mark) for mark in markers])
		
		#gc.collect()
		
		return markers
	
	
		
	def RequestTiles(self):
		
		for tile in self.MAP.TilesCenters():
			print("Requesting tile:",tile.name)
			print(tile.x, tile.y, tile.tile_center())
			tile_rsp = TileReq(tile.tile_center(), self.zoom_level, self.scale, self.tile_size, self.markers, self.key).response()
			
			if tile_rsp:
				tile_name = self.map_name+"_%s_%s.png"%(tile.name[0], tile.name[1]) #images
				with open(tile_name,'wb') as img:
					img.write(tile_rsp)
				# tile_name = self.map_name+"_%s_%s.txt"%(tile[0], tile[1])
				# with open(tile_name,'w') as img:
					# img.write(tile_rsp)
			else:
				return False
			time.sleep(5)
			
			#gc.collect()


class TileReq(object):
	
	def __init__(self, center, zoom, scale, size, markers, key):
		self.LAT = center.lat
		self.LONG = center.long
		self.ZOOM_LEVEL = zoom
		self.SCALE = scale
		self.TILE_SIZE = "%dx%d"%(size, size)
		self.API_KEY = API_KEYS[KEY_INDEX]
		self.http_err = 0
		self.url_err = 0
		self.status_err = 0
		self.MARKERS = markers
	
	def response(self):
		
		global REQUESTS
		global QUOTA
		
		if REQUESTS > QUOTA:
			REQUESTS = 0
			KEY_INDEX += 1
			self.API_KEY = API_KEYS[KEY_INDEX]
		
		params = self.__dict__
		api_req = STATIC_GMAPS_REQ.format(**params)
		print(api_req)
		
		REQUESTS+=1
		# return api_req	#>>>>> test
		
		
		try:
			rsp = request.urlopen(api_req)
			self.http_err = self.url_err = 0
			
			if rsp.code == HTTPStatus.OK:
				self.status_err = 0
				return rsp.read()
			else:
				self.status_err += 1
				self.response()
			
		except error.HTTPError as e:
			self.http_err += 1
			if self.http_err < 3:
				print(e, "Retrying after 10 seconds...", sep='\n')
				time.sleep(10)
				self.response()
			else:
				print(e, "Requests failed 3 times!", sep='\n')
				http_err = 0
				return False
			
		except error.URLError as e:
			self.url_err += 1
			if self.url_err < 3:
				print(e, "Retrying after 10 seconds...", sep='\n')
				time.sleep(10)
				self.response()
			else:
				self.url_err = 0
				print(e, "Requests failed 3 times!", sep='\n')
				return False


				
if __name__ == "__main__":
	
	from pprint import pprint as pp
	
	#UL = 30.542686, 31.009286
	#LR = 30.539683, 31.014264
	UL = 30.061366, 31.190270
	LR = 30.056398, 31.199443
	
	zoom = 18
	scale = 2
	size = 512
	print(size)
	UL = Geo.UMTPoint(UL[0], UL[1], zoom)
	LR = Geo.UMTPoint(LR[0], LR[1], zoom)
	print(UL, LR, sep='\n')
	
	map = MapReq(UL, LR, zoom, scale, size, KEY_INDEX)
	print(map)
	print(map.MAP)
	print(map.MAP.upper_left_tile)
	print(map.MAP.lower_right_tile)
	map.RequestTiles()
