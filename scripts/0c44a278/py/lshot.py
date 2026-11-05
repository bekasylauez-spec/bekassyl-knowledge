import win32gui, win32con, sys, pyautogui
from PIL import ImageGrab
def find():
    r=[]
    win32gui.EnumWindows(lambda h,_: r.append(h) if win32gui.IsWindowVisible(h) and 'ЛИРА' in win32gui.GetWindowText(h) else None, None)
    return r
hs=find(); print([(h,win32gui.GetWindowText(h),win32gui.GetWindowRect(h)) for h in hs])
import ctypes
user32=ctypes.windll.user32
print('screens', [ (m[2]) for m in __import__('win32api').EnumDisplayMonitors()])
if hs:
    rc=win32gui.GetWindowRect(hs[0]); img=ImageGrab.grab(bbox=rc, all_screens=True); img.save(sys.argv[1]); print(img.size)
