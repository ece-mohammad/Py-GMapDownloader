# Py-GMapDownloader
Python script with a GUI to download a map using Google static maps API.

Requirements:
------------
  - Python 3.x.

How to use:
-----------
  - Run the file `main.py`, either from the terminal by using the command: `python main.py`
     or by double clicking the file.
  - Enter the upper-left and lower-right corners co-ordinates of the map you want to download.
  - Enter the zoom level*:
      - 1: World
      - 5: Landmass/continent
      - 10: City
      - 15: Streets
      - 20: Buildings
  - Enter the map name (optional).
  - Click `Download Map`

How it works:
-------------
  - The scripts takes the co-ordinates and the zoom level, then calculates how many tiles needed to cover the requested map. After that, calculates the center co-ordinates of each tile and requests the tiles from google's static maps api. It also puts 4 markers on the corners of the map, and generates a text file witht he corndinates of each marker.
  - Downloaded maps are saved in a sub folder `TMP` (name can be changed, look at `config.py`).
  - After downloading all the tiles, the script then starts to 'stitch' the tiles into one big image.

Config.py:
----------
  - You'll notice a `config.py` file, as the name suggests, the file has some configuration variables, like the work subfolder name.
  - It's divided into 2 sections:
    - `UserConfig section`: variables that the user can change according to his needs.
    - `ProgConfig section`: variables required by the program to run correctly, shouldn't be changed unless you know what you're doing. Keep a backup copy of the file before changing it, in case things don't go very well.

Known Issues:
-------------
- The GUI hangs when you start downloading a map, you can't clikc on buttons or change text fields untill the script is finishes your map, or interrupted by `Ctrl+C`. You can still minimize or close the window.
  - This script is a memory hog! If the number of tiles is large (700+), it'll take a lot of memory (RAM) during the tile stitching process. The maximum number of tiles depends on how much RAM do you have, it's better not to push it too far though.
  When requesting a map, the program prints on the terminal the number of tiles that will be requested, if the number is too large, you can always `Ctrl+c`.
  - I put a delay between tile requests to not overload the API server with requests (5 sec delay), this makes the process of requesting tiles take quite some time.
  - Currently, the only supported map type is `roadmap`, you can actually change this in the `config.py` file by changing the map type in `STATIC_GMAPS_REQ`. Again, If you don't know what you're doing, don't change it!

Future:
------
  - Add logging.
  - Add a way to know how many requests are left to reach api's request limit.
  - Use multithreading to start stitching the tiles as soon as they are downloaded, and request multiple tiles at the same time.
  - Add `Cancel` button.
  - Add support for more map types (staellite, terrain, etc).
  - Add an option to not include markers.
  - ~~Overlap the images to cover Google's logo everywhere in the map except for the bottom row~~.
  
  *: Increasing the zoom level greatly increases the number of tiles needed to be downloaded - I think the difference is ( 2 ** (2* (zoom_2 - zoom_1) ) ), but I could be wrong! - So, If you need a highly detailed map (streets/buildings zoom level) of a large area, consider breaking it down to multiple smaller areas.
  
  ** I usually use TABs instead of spaces, so If you have indentation errors, try opening the files in an editor that replaces tabs with spaces (replace TAB with 4 or 2 spaces).
  
  *** This script is inspired by Hayden Eskriett's GoogleMapDownloader, website: [http://eskriett.com].
