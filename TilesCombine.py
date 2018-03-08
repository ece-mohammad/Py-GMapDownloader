import Geo, config
from FileManager import FileManager as fm

from PIL import Image 
import re
import os, sys, time, gc

WORK_DIR = config.WORK_DIR
TILE_SIZE = config.TILE_SIZE

class MapImage(object):
	
	def __init__(self, width, height, name):
		
		self.img_width = width
		self.img_height = height
		self.base_name = name
	
	
	def open_image(self):
		
		fm.GoToWorkDir()
		#print(os.getcwd())
		
		map_img = Image.new("RGB",(self.img_width, self.img_height+20))
		
		for tile in os.listdir():
			if tile.startswith(self.base_name) and tile.endswith('.png'):
				res = re.findall('\d+', tile)
				if res:
					tile_x, tile_y = map(int, res)
					del res
					print("--> adding the image: {}".format(tile))
					tile_img = Image.open(tile)
					map_img.paste(tile_img, (tile_y*TILE_SIZE, tile_x*TILE_SIZE,))
					map_img.save(self.base_name+'.png')
				gc.collect()
		
		#map_img.save(self.base_name+'.png')


if __name__ == '__main__':
	
	TILE_SIZE = 256
	
	a = MapImage(1024, 1024, 'map')
	a.open_image()
