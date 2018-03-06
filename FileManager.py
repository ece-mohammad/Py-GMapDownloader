import config
import os, sys

WORK_DIR = config.WORK_DIR

class FileManager(object):
	@staticmethod
	def GoToWorkDir():
		global WORK_DIR
			
		cd = os.getcwd()
		contents = os.listdir()
			
		if (os.path.basename(cd) != WORK_DIR) and (sys.argv[0] in contents):
			if (not WORK_DIR in contents):
				os.mkdir(WORK_DIR)
			os.chdir(WORK_DIR)
		return True
	
	@staticmethod
	def GoToMainDir():
		global WORK_DIR
		
		cd = os.getcwd()
		
		if (os.path.basename(cd) == WORK_DIR):
			os.chdir('..')
		return True
	
	
if __name__ == '__main__':
    pass
