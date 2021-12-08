import cv2
import numpy
import os
import sys
import mss
import mss.tools
import time
import pyautogui
import glob

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile,QIODevice
UI_LOADER = QUiLoader()

# All the 6 methods for comparison in a list
methods = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR',
		   'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']
#----------------------------------------------------------------------
def capture_part_of_the_screen(top,left,width,height,save_to_file=False,as_numpy_array=False):
	""" capture only a part of the screen"""
	with mss.mss() as sct:
		# The screen part to capture
		monitor = {"top": top, "left": left, "width": width, "height": height}
	
		# Grab the data
		sct_img = sct.grab(monitor)
		#isinstance(sct_img,mss.screenshot.ScreenShot)
		
		if save_to_file:
			mss.tools.to_png(sct_img.rgb, sct_img.size, output=r"images\screen_grab_section.png")
			sct_img = create_cv2_Image(r"images\screen_grab_section.png")
			sct_img = cv2.cvtColor(sct_img, cv2.COLOR_RGB2RGBA)
		sct_img = numpy.array(sct_img)
		return sct_img

#----------------------------------------------------------------------
def create_cv2_Image(fp,flags=cv2.IMREAD_UNCHANGED):
	""""""
	res = cv2.imread(fp, flags=flags)
	res = cv2.cvtColor(res, cv2.COLOR_RGB2RGBA)
	return res

#----------------------------------------------------------------------
def show_To_Window(image):
	""""""
	if isinstance(image,str):
		image = create_cv2_Image(image)
	cv2.imshow("Result", image)
	cv2.waitKey()
	cv2.destroyAllWindows()


#----------------------------------------------------------------------
def Build_Widget_From_Ui_File(ui_file_name,loader):
	""""""
	ui_file = QFile(ui_file_name)

	if not ui_file.open(QIODevice.ReadOnly):
		print("Cannot open {}: {}".format(ui_file_name, ui_file.errorString()))
	else:
		widget = loader.load(ui_file, None)
		ui_file.close()
		if not widget:
			print(loader.errorString())
			return None
		else:
			return widget
	return None


#----------------------------------------------------------------------
def Load_Bloxburg_Auto_Fisher_UI():
	""""""
	global UI_LOADER

	current_dir = os.path.dirname(__file__)
	file_ui = os.path.join(current_dir,"blockburg_Fisher.ui")
	widget = Build_Widget_From_Ui_File(file_ui, UI_LOADER)
	isinstance(widget,QWidget)
	return widget


class MyWidget(QWidget):
	def __init__(self,parent=None):
		super(MyWidget,self).__init__(parent)
		self._sleeping = False
		self.layout = QVBoxLayout()
		self.ui_widget = Load_Bloxburg_Auto_Fisher_UI()
		self.ui_widget.start_fishing_button.clicked.connect(self.start_Timer)
		self.ui_widget.stop_fishing_button.clicked.connect(self.stop_Timer)
		self.ui_widget.RunScanButton.clicked.connect(self.run_Scan_Data)
		self.layout.addWidget(self.ui_widget)
		self.setLayout(self.layout)
		self._check_for_fish_timer = None
		self._swatchs_to_scan = []
		for fp in glob.glob("swatch_Lookup/*.jpg", recursive=False):
			self._swatchs_to_scan.append(create_cv2_Image(fp))
	#----------------------------------------------------------------------
	def run_Scan_Data(self):
		""""""
		screen_grab   = capture_part_of_the_screen(500, 550, 800, 600,save_to_file=True,as_numpy_array=True)
		cv2.imwrite("images/screen_grab_with_rec.jpg",screen_grab)
		pixmap = QPixmap("images/screen_grab_with_rec.jpg")
		self.ui_widget.Screen_Shot_Image.setPixmap(pixmap)
		
	#----------------------------------------------------------------------
	def run_matchTemplate(self,image_to_scan):
		""""""
		match_data = TemplateMatch_Data(self.image_to_scan_for)
		match_data.draw_rectangle()
		return match_data
	
	#----------------------------------------------------------------------
	def start_Timer(self):
		""""""
		if self._check_for_fish_timer == None:
			self._check_for_fish_timer = self.startTimer(900)
	#----------------------------------------------------------------------
	def stop_Timer(self):
		""""""
		if not self._check_for_fish_timer == None:
			self.killTimer(self._check_for_fish_timer)
			self._check_for_fish_timer = None
		
	def timerEvent(self, event):
		screen_grab   = capture_part_of_the_screen(500, 550, 800, 600,save_to_file=True,as_numpy_array=True)
		if not self._sleeping:
			for test_item in self._swatchs_to_scan:
				res = cv2.matchTemplate(screen_grab, test_item, cv2.TM_CCOEFF_NORMED)
				min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
				if max_val > 0.965:
					print(max_val)
					pyautogui.moveTo(960, 1130) # Move the mouse to XY coordinates.
					pyautogui.doubleClick()
					time.sleep(6)
					pyautogui.doubleClick()
					break
			
#image_to_scan = capture_part_of_the_screen(500, 550, 800, 600,save_to_file=True,as_numpy_array=False)
#image_to_look_for = create_cv2_Image(r"D:\GitHub\PyAutoClick\White_And_Orange_Ball.jpg")


#w = image_to_look_for.shape[1]
#h = image_to_look_for.shape[0]

#res = cv2.matchTemplate(image_to_scan, image_to_look_for, cv2.TM_CCOEFF_NORMED)

#min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
#print(max_val)
#cv2.rectangle(image_to_scan, max_loc, (max_loc[0] + w, max_loc[1] + h) ,(0,255,255), thickness=2)
#if max_val > 0.8:
	#print(max_val)
	#show_To_Window(image_to_scan)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	mainWin = MyWidget()
	mainWin.resize(500, 220)
	mainWin.show()
	sys.exit(app.exec_())