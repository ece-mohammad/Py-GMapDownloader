"""

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



public final class GoogleMapsProjection2 
{
    private final int TILE_SIZE = 256;
    private PointF _pixelOrigin;
    private double _pixelsPerLonDegree;
    private double _pixelsPerLonRadian;

    public GoogleMapsProjection2()
    {
        this._pixelOrigin = new PointF(TILE_SIZE / 2.0,TILE_SIZE / 2.0);
        this._pixelsPerLonDegree = TILE_SIZE / 360.0;
        this._pixelsPerLonRadian = TILE_SIZE / (2 * Math.PI);
    }

    double bound(double val, double valMin, double valMax)
    {
        double res;
        res = Math.max(val, valMin);
        res = Math.min(res, valMax);
        return res;
    }

    double degreesToRadians(double deg) 
    {
        return deg * (Math.PI / 180);
    }

    double radiansToDegrees(double rad) 
    {
        return rad / (Math.PI / 180);
    }

    PointF fromLatLngToPoint(double lat, double lng, int zoom)
    {
        PointF point = new PointF(0, 0);

        point.x = _pixelOrigin.x + lng * _pixelsPerLonDegree;       

        // Truncating to 0.9999 effectively limits latitude to 89.189. This is
        // about a third of a tile past the edge of the world tile.
        double siny = bound(Math.sin(degreesToRadians(lat)), -0.9999,0.9999);
        point.y = _pixelOrigin.y + 0.5 * Math.log((1 + siny) / (1 - siny)) *- _pixelsPerLonRadian;

        int numTiles = 1 << zoom;
        point.x = point.x * numTiles;
        point.y = point.y * numTiles;
        return point;
     }

    PointF fromPointToLatLng(PointF point, int zoom)
    {
        int numTiles = 1 << zoom;
        point.x = point.x / numTiles;
        point.y = point.y / numTiles;       

        double lng = (point.x - _pixelOrigin.x) / _pixelsPerLonDegree;
        double latRadians = (point.y - _pixelOrigin.y) / - _pixelsPerLonRadian;
        double lat = radiansToDegrees(2 * Math.atan(Math.exp(latRadians)) - Math.PI / 2);
        return new PointF(lat, lng);
    }

    public static void main(String []args) 
    {
        GoogleMapsProjection2 gmap2 = new GoogleMapsProjection2();

        PointF point1 = gmap2.fromLatLngToPoint(41.850033, -87.6500523, 15);
        System.out.println(point1.x+"   "+point1.y);
        PointF point2 = gmap2.fromPointToLatLng(point1,15);
        System.out.println(point2.x+"   "+point2.y);
    }
}

public final class PointF 
{
    public double x;
    public double y;

    public PointF(double x, double y)
    {
        this.x = x;
        this.y = y;
    }
}

"""

import math
import config

#------- constants
PI = math.pi
E = math.e
DEF_TILE_SIZE = 256

TILE_SIZE = config.TILE_SIZE

class Point(object):

	def __init__(self, x, y):
		self.x = x
		self.y = y
	
	def __sub__(self, other):
		assert isinstance(other, self.__class__), "ValueError! Can't sub %s from %s!"%(type(self), type(other))
		return Point(self.x - other.x, self.y - other.y)
	
	def __add__(self, other):
		assert isinstance(other, self.__class__), "ValueError! Can't add %s to %s!"%(type(self), type(other))
		return Point(self.x + other.x, self.y + other.y)
	
	def __mul__(self, scale):
		assert isinstance(scale, int) or isinstance(scale, float), "ValueError! Can't multiply %s to numerical value!"%(type(self))
		return Point(self.x*scale, self.y*scale)
	
	def __truediv__(self, scale):
		assert isinstance(scale, int) or isinstance(scale, float), "ValueError! Can't multiply %s to numerical value!"%(type(self))
		return Point(self.x/scale, self.y/scale)
	
	def __eq__(self, other):
		assert isinstance(other, self.__class__), "ValueError! Can't compare %s to %s"%(type(self), type(other))
		return (self.x == other.x) and (self.y == other.y)
	
	def __str__(self):
		return "Point: ({:.6f}, {:.6f})".format(self.x, self.y)
	
	def __repr__(self):
		return "%r(%s)"%(self.__class__, self.__dict__)


class PixelPoint(Point):
	
	def __init__(self, x, y, z):
		self.x, self.y = x, y
		self.zoom_level = z
	
	def __str__(self):
		return "PixelPoint (x: {:.6f}, y:{:.6f}), zoom level: {}".format(self.x, self.y, self.zoom_level)
	
	def Pixel2LatLong(self):
		"""Transforms from X/Y pixel co-ordinates to latitude/longitude co-ordinates"""
		"""not very accurate when truncating decimal numbers from pixel points"""
		return self.PixelToWorld().WorldPoint2LatLong()
	
	def PixelToWorld(self):
		"""Transforms from X/Y pixel co-ordinates to world co-ordinates (mercator projection)"""
		world_x = self.x/(1<<self.zoom_level)
		world_y = self.y/(1<<self.zoom_level)
		return WorldPoint(world_x, world_y, self.zoom_level)
	
	def PixelToTile(self):
		"""Transforms from X/Y pixel co-ordinates to tile co-ordinates"""
		return Tile(self.x//DEF_TILE_SIZE, self.y//DEF_TILE_SIZE, self.zoom_level)

	
class WorldPoint(Point):
	
	def __init__(self, x, y, z):
		self.x, self.y = x, y
		self.zoom_level = z
	
	def __str__(self):
		return "WorldPoint (x: {:.6f}, y: {:.6f}), zoom level: {}".format(self.x, self.y, self.zoom_level)
	
	def WorldToPixel(self):
		"""Transforms from world X/Y co-ordinates (mercator projection) to Pixel X/Y co-ordinates"""
		pixel_x = self.x*(1<<self.zoom_level)
		pixel_y = self.y*(1<<self.zoom_level)
		return PixelPoint(pixel_x, pixel_y, self.zoom_level)
	
	def WorldPoint2LatLong(self):
		"""Transforms from world co-ordinates(mercator) to latitude/longitude co-ordinates"""
		long = ((self.x*2/DEF_TILE_SIZE) - 1) * 180
		inv_mercator = math.exp(PI * (1 - self.y*2/DEF_TILE_SIZE))
		lat = (math.atan(inv_mercator) - PI/4) * 360/PI
		return UMTPoint(lat, long, self.zoom_level)
	
	def World2Tile(self):
		"""Transforms from world co-ordinates(mercator) to tile co-ordinates"""
		x = self.x*(1<<self.zoom_level)//DEF_TILE_SIZE
		y = self.y*(1<<self.zoom_level)//DEF_TILE_SIZE
		return Tile(x, y, self.zoom_level)
	

class UMTPoint(Point):
	
	def __init__(self, lat, long, zoom):
		self.long = long
		self.lat = lat
		self.zoom_level = zoom
	
	def __str__(self):
		return "UMT point (lat: {:.6f}, long: {:.6f}), zoom: {}".format(self.lat, self.long, self.zoom_level)
	
	def LatLong2WorldPoint(self):
		"""Transforms from latitude/longitude co-ordinates to world X/Y co-ordinates (mercator projection)"""
		lat = self.lat*PI/180
		mercator = -1 * math.log( math.tan( PI/4 + lat/2 ) )
		world_x = (DEF_TILE_SIZE/2) * (self.long/180 + 1)
		world_y = (DEF_TILE_SIZE/2) * (mercator/PI + 1)
		return WorldPoint(world_x, world_y, self.zoom_level)
	
	def LatLong2Pixel(self):
		"""Transforms from latitude/longitude co-ordinates to Pixel co-ordinates"""
		return self.LatLong2WorldPoint().WorldToPixel()
		
	def LatLongToTile(self):
		"""Transforms from latitude/longitude co-ordinates to tile co-ordinates"""
		co_ords = self.LatLong2WorldPoint()
		x = (co_ords.x*(1<<self.zoom_level)//DEF_TILE_SIZE)
		y = (co_ords.y*(1<<self.zoom_level)//DEF_TILE_SIZE)
		return Tile(x, y, self.zoom_level)
	
	
class Tile(object):
	
	def __init__(self, x, y, z, r=(0,0)):
		self.x = x				#tile x for tile[x][y] where x is rows, y is columns 
		self.y = y				#tile y for tile[x][y] where x is rows, y is columns 
		self.zoom_level = z
		self.name = (r[0], r[1])
	
	def __str__(self):
		return "Tile: (x: {}, y: {}), zoom_level: {}, name: {}".format(self.x, self.y, self.zoom_level, self.name)
	
	def __repr_(self):
		return "%s(%r)"%(self.__class__, self.__dict__)
	
	def tile_center(self):
		"""Returns the upper_left_corner of the tile as Lat/Long co-ordinates"""
		center_x = (self.x + 1/2)*DEF_TILE_SIZE
		center_y = (self.y + 1/2)*DEF_TILE_SIZE
		return PixelPoint(center_x, center_y, self.zoom_level).Pixel2LatLong()


class Map(object):
	def __init__(self, upper_left, lower_right, zoom):
		assert isinstance(upper_left, UMTPoint) and isinstance(lower_right, UMTPoint),\
		"ValueError! Both upper left point and lower right corner points must be UMTPoint instances!"
		
		self.upper_left_corner = upper_left
		self.lower_right_corner = lower_right
		self.zoom_level = zoom
		
		#convert from lat/long to tiles
		self.upper_left_tile = self.upper_left_corner.LatLongToTile()
		self.lower_right_tile = self.lower_right_corner.LatLongToTile()
		
		#number of tiles
		self.num_tiles_x = abs(self.lower_right_tile.x - self.upper_left_tile.x) + 1
		self.num_tiles_x = int(self.num_tiles_x*(DEF_TILE_SIZE/TILE_SIZE)) + 1
		
		self.num_tiles_y = abs(self.lower_right_tile.y - self.upper_left_tile.y) + 1
		self.num_tiles_y = int(self.num_tiles_y*(DEF_TILE_SIZE/TILE_SIZE)) + 1
		
		self.num_tiles = self.num_tiles_x * self.num_tiles_y
		
		#image dimensions
		self.map_width = self.num_tiles_x * TILE_SIZE
		self.map_height = self.num_tiles_y * TILE_SIZE
	
	def __str__(self):
		return "Map object UL(%f,%f), LR(%f, %f), Zoom= %d\nWidth: %d, Height: %d, Tiles: %d"\
		%(self.upper_left_corner.lat, self.upper_left_corner.long,
		self.lower_right_corner.lat, self.lower_right_corner.long, self.zoom_level,
		self.map_width, self.map_height, self.num_tiles)
	
	def __repr_(self):
		return "%s(%r)"%(self.__class__, self.__dict__)
	
	def TilesCenters(self):
		"""fills dictionary with tiles centers"""
		upper_tile_x = self.upper_left_tile.x
		upper_tile_y = self.upper_left_tile.y
		scale = TILE_SIZE//DEF_TILE_SIZE
		
		for y in range(self.num_tiles_y):
			for x in range(self.num_tiles_x):
				yield Tile((upper_tile_x +(x*scale) ), (upper_tile_y + (y*scale) ), self.zoom_level, (y, x))
				print("GENERATOR____INFO")
				print(y,x)
				print((upper_tile_x +(x*scale) ), (upper_tile_y + (y*scale) ))



if __name__ == '__main__':
	
	def test():
		long = -87.64999999999998 
		lat = 41.85
		#-----------
		pixel_x = 525
		pixel_y = 761
		#------------
		world_x = 65.67111111111113
		world_y = 95.17492654697409
		#------------
		zoom = 17
		
		#test point
		#p = Point(0,0)
		#q = Point(3,4)
		#print(p, q, sep='\n')
		#print("add:",p+q)
		#print("sub:",p-q)
		#print("mul:",q*2)
		#print("div:",q/2)
		#print("eq:",p==q)
		#print('------------------------\n')
		
		#Test UMTPoint class
		foo = UMTPoint(lat, long, zoom)
		print(foo)
		print(foo.LatLong2WorldPoint())
		print(foo.LatLong2Pixel())
		print(foo.LatLongToTile())
		print('------------------------\n')
		
		#Test WorldPoint class
		print(foo.LatLong2WorldPoint().WorldPoint2LatLong())
		print(foo.LatLong2WorldPoint().WorldToPixel())
		print(foo.LatLong2WorldPoint().World2Tile())
		print('------------------------\n')
		
		#Test PixelPoint class
		print(foo.LatLong2Pixel().Pixel2LatLong())
		print(foo.LatLong2Pixel().PixelToWorld())
		print(foo.LatLong2Pixel().PixelToTile())
		print('------------------------\n')
		
		#Test Tile
		#t = Tile(268988, 389836, zoom)
		#print(t.tile_center())
		#print(t.tile_center().LatLong2WorldPoint())
		#print(t.tile_center().LatLong2Pixel())
		#print(t.tile_center().LatLongToTile())
		
		#Test Map class
		zoom = 9
		ul = UMTPoint(35.874970, 23.417749, zoom)
		lr = UMTPoint(34.727331, 26.515893, zoom)
		m = Map(ul, lr, zoom)
		print(m)
		for t in m.TilesCenters():
			print(t)
			print('tile center:',t.tile_center())
			print('------------')
		
		#test point for markers
		center = UMTPoint(30.061366, 31.190270,17)
		cp = center.LatLong2Pixel()
		UL = PixelPoint(cp.x - 256 + 20, cp.y - 256 + 40, 17)
		UL = UL.Pixel2LatLong()
		print("UL: (%.6f, %.6f)"%(UL.lat, UL.long))
		LR = PixelPoint(cp.x + 256 - 20, cp.y + 256 - 20, 17)
		LR = LR.Pixel2LatLong()
		print("LR: (%.6f, %.6f)"%(LR.lat, LR.long))
		
		
		
	test()
#https://maps.googleapis.com/maps/api/staticmap?center=30.541152,%2031.011732&zoom=16&size=400x400&markers=color:blue%7Clabel:S%7C11211%7C11206%7C11222&key=AIzaSyAJvgfyNDc-jFJnKkOzq-_A--4ihinEHCs
