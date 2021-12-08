
from pynput import mouse
from pynput import keyboard
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QObject, Signal, Slot,Qt, QFile, QIODevice
import sys
import os
import time
_MOUSE_CTRL = mouse.Controller()
UI_LOADER = QUiLoader()

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

def Load_Py_Auto_Click_UI():
    """"""
    global UI_LOADER

    current_dir = os.path.dirname(__file__)
    py_auto_click_ui = os.path.join(current_dir,"PyAutoPickGUI.ui")
    widget = Build_Widget_From_Ui_File(py_auto_click_ui, UI_LOADER)
    isinstance(widget,QMainWindow)
    return widget

class Mouse_Monitor(QObject):
    """"""
    Mouse_Moved    = Signal(str)
    Mouse_Clicked  = Signal(str)
    Mouse_Scrolled = Signal(str)
    Left_Mouse_Clicked  = Signal(bool)
    Toggle_Auto_Click_Enabled = Signal(bool)
    def __init__(self,parent=None):
        """Constructor"""
        super(Mouse_Monitor,self).__init__(parent)
        self._is_in_autoclick_mode = False
        
        self.listener = mouse.Listener(on_move=self.On_Mouse_Moved,on_click=self.On_Mouse_Clicked,on_scroll=self.On_Mouse_Scrolled)
        self.listener.start()
        self.keyboardlistener = keyboard.Listener(on_press=self.On_Keyboard_Press,on_release=self.On_Keyboard_Release)
        self.keyboardlistener.start()
    
    def On_Mouse_Moved(self,x,y):
        """"""
        self.Mouse_Moved.emit('Pointer moved to {0}'.format((x, y)))

    def On_Mouse_Clicked(self, x, y, button, pressed):
        """"""
        if button == mouse.Button.left:
            button_name = "right"
            if pressed and not self._is_in_autoclick_mode:
                self.Left_Mouse_Clicked.emit(True)
            elif not pressed:
                self.Left_Mouse_Clicked.emit(False)
                
        elif button == mouse.Button.right:
            button_name = "Right"
        else:
            button_name = "Middle"
        if pressed:
            action_name = "Pressed"
        else:
            action_name = "Released"
        #print('{0} Button Was {1} at {2},{3}'.format(button_name,action_name,x, y))
        self.Mouse_Clicked.emit('{0} Button Was {1} at {2},{3}'.format(button_name,action_name,x, y))

    def On_Mouse_Scrolled(self, x, y, dx, dy):
        """"""
        self.Mouse_Scrolled.emit('Scrolled {0} at {1}'.format('down' if dy < 0 else 'up',(x, y)))

    def On_Keyboard_Press(self,key):
        try:
            if key.char == "?":
                #print('{0} pressed'.format(key.char))
                if self._is_in_autoclick_mode:
                    self.Toggle_Auto_Click_Enabled.emit(False)
                else:
                    self.Toggle_Auto_Click_Enabled.emit(True)
        except AttributeError:
            pass
            #print('special key {0} pressed'.format(
                #key))
    
    def On_Keyboard_Release(self,key):
        try:
            if key.char == "?":
                print('{0} released'.format(key))
        except:
            pass
        #if key == keyboard.Key.esc:
            ## Stop listener
            #return False
        
class MyWidget(QWidget):
    def __init__(self,parent=None):
        super(MyWidget,self).__init__(parent)
        
        self._click_timer = None
        self._auto_clicking_enabled = False
        
        self.layout = QVBoxLayout()
        self.ui_widget = Load_Py_Auto_Click_UI()
        self.layout.addWidget(self.ui_widget)
        self.setLayout(self.layout)
        self.listener = Mouse_Monitor(parent=self)
        self.listener.Mouse_Moved.connect(self.ui_widget.mousePositionLineEdit.setText)
        self.listener.Mouse_Clicked.connect(self.ui_widget.mouseButtonClickedLineEdit.setText)
        self.ui_widget.StartButton.clicked.connect(self.Enabled_Auto_Clicking)
        self.ui_widget.StopButton.clicked.connect(self.Disable_Auto_Clicking)
        self.listener.Left_Mouse_Clicked.connect(self.Start_Auto_Clicking)
        self.listener.Toggle_Auto_Click_Enabled.connect(self.Toggle_Auto_Clicking)
    @Slot(bool)
    def Toggle_Auto_Clicking(self,value):
        """"""
        if self.ui_widget.StartButton.isEnabled():
            self.ui_widget.StartButton.click()
        else:
            self.ui_widget.StopButton.click()
        
    @Slot()
    def Enabled_Auto_Clicking(self):
        """"""
        self._auto_clicking_enabled = True
    @Slot()
    def Disable_Auto_Clicking(self):
        """"""
        self._auto_clicking_enabled = False
            
    @Slot(bool)
    def Start_Auto_Clicking(self,value):
        if value and self._auto_clicking_enabled:
            click_timer = 1000 / self.ui_widget.clicks_per_second.value()
            self.listener._is_in_autoclick_mode = True
            self._click_timer = self.startTimer(click_timer)
        else:
            if not self._click_timer == None:
                #print("Killing click timer {0}".format(self._click_timer))
                self.killTimer(self._click_timer)
                self._click_timer = None
                self.listener._is_in_autoclick_mode = False
            
    def timerEvent(self, event):
        _MOUSE_CTRL.press(mouse.Button.left)
        _MOUSE_CTRL.release(mouse.Button.left)
    
        #print("Timer ID:{0}".format(event.timerId()))
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MyWidget()
    mainWin.resize(500, 220)
    mainWin.show()
    sys.exit(app.exec_())