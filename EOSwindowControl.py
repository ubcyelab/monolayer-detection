import win32gui
import re
import time
import keyboard
from pywinauto import application
from pywinauto.findwindows import WindowAmbiguousError, WindowNotFoundError

def focusWindow(name):
    # Init App object
    app = application.Application()
    try:
        app.connect(title_re=".*%s.*" % name)

        # Access app's window object
        app_dialog = app.top_window()
        app_dialog.set_focus()
    except(WindowNotFoundError):
        print('"%s" not found' % name)
        pass
    except(WindowAmbiguousError):
        print('There are too many "%s" windows found' % name)
        pass

def captureImage(windowName):
    focusWindow(windowName)
    time.sleep(.05)
    keyboard.press_and_release('space')
    # print("!!!PIC TAKING")
    time.sleep(1.6)

def setUpEOS(windowName):
    camWindow = WindowMgr()
    camWindow.find_window_wildcard(windowName)
    return camWindow

class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""
    def __init__ (self):
        """Constructor"""
        self._handle = None

    def find_window(self, class_name, window_name=None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)
    
    def set_foreground(self):
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self._handle)