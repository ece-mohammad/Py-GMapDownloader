import config, Geo
import TilesCombine as TC
import TilesRequest as TR
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import os, gc, re

def MainWin():
	
	gc.enable()
	
	def close_win():
		files = os.listdir()
		for img in files:
			if img.endswith(".png") and re.findall('_\d+', img):
				os.remove(img)
		root.destroy()
	
	def get_map():
		
		gc.collect()
		
		UL_val = [ *map(float, ( UL_corner.get().split(',') ) )]
		LR_val = [ *map(float, ( LR_corner.get().split(',') ) ) ]
		zoom_level = zoom.get()
		name = img_name.get()
		
		if not 0 < zoom_level < 21:
			messagebox.showerror("Value Error!", "Zoom Level must be in range [0, 20]")
			return False
		
		if name == "":
			name = "map"
		
		#print(name)
		
		UL_val = Geo.UMTPoint(UL_val[0], UL_val[1], zoom_level)
		LR_val = Geo.UMTPoint(LR_val[0], LR_val[1], zoom_level)
		map_ = TR.MapReq(UL_val, LR_val, zoom_level, name=name)
		print(map_.MAP)
		map_.RequestTiles()
		TC.MapImage(map_.MAP.map_width, map_.MAP.map_height, name).open_image()
		
		
	
	root = tk.Tk()
	root.title("Google Map Downloader")
	root.resizable(width=False, height=False)
	
	main_frame = tk.Frame(root, padx=12, pady=4, relief="flat", borderwidth=4)
	main_frame.grid(column=0, row=0, columnspan=2, sticky=(tk.N, tk.E, tk.S, tk.W))
	main_frame.columnconfigure(0, weight=1)
	
	UL_corner = tk.StringVar()
	LR_corner = tk.StringVar()
	zoom = tk.IntVar()
	img_name = tk.StringVar()
	
	
	UL_corner_label = tk.Label(main_frame, text="Upper Left corner:")
	UL_corner_label.grid(column=0, row=0, sticky=(tk.W,))
	
	UL_corner_box = tk.Entry(main_frame, textvariable=UL_corner)
	UL_corner_box.grid(column=1, row=0, sticky=(tk.W,))
	
	LR_corner_label = tk.Label(main_frame, text="Lower Right corner:")
	LR_corner_label.grid(column=0, row=1, sticky=(tk.W,))
	
	LR_corner_box = tk.Entry(main_frame, textvariable=LR_corner)
	LR_corner_box.grid(column=1, row=1, sticky=(tk.W,))
	
	zoom_label = tk.Label(main_frame, text="Zoom Level:")
	zoom_label.grid(column=0, row=2, sticky=(tk.W,))
	
	zoom_box = tk.Entry(main_frame, textvariable=zoom)
	zoom_box.grid(column=1, row=2, sticky=(tk.W,))
	
	name_label = tk.Label(main_frame, text="Image Name:")
	name_label.grid(column=0, row=3, sticky=(tk.W))
	
	name_box = tk.Entry(main_frame, textvariable=img_name)
	name_box.grid(column=1, row=3, sticky=(tk.W))
	
	
	ok_button = tk.Button(root, text="Download Map", width=15, padx=2, pady=2)
	ok_button.grid(column=0, row=1, ipadx=1, ipady=1)
	ok_button.configure(command=get_map)
	
	exit_button = tk.Button(root, text="Exit", width=15, padx=2, pady=2)
	exit_button.grid(column=1, row=1, ipadx=1, ipady=1)
	exit_button.configure(command=close_win)
	
	
	
	
	root.mainloop()


if __name__ == '__main__':
	MainWin()
