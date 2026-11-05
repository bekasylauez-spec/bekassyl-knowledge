# usage: lc.py click X Y | dclick X Y | rclick X Y | key keys | type text | shot out [x0 y0 x1 y1]   (X,Y in screenshot px of window, origin = window rect)
import sys, time, win32gui, pyautogui
from PIL import ImageGrab
pyautogui.FAILSAFE=False
def lira():
    r=[]
    win32gui.EnumWindows(lambda h,_: r.append(h) if win32gui.IsWindowVisible(h) and 'ЛИРА-САПР' in win32gui.GetWindowText(h) else None, None)
    return r[0]
h=lira(); L,T,R,B=win32gui.GetWindowRect(h)
a=sys.argv[1:]
i=0
while i<len(a):
    c=a[i]
    if c in('click','dclick','rclick'):
        x,y=int(a[i+1])+L,int(a[i+2])+T; i+=3
        {'click':pyautogui.click,'dclick':pyautogui.doubleClick,'rclick':pyautogui.rightClick}[c](x,y)
    elif c in('sclick','sdclick'):
        x,y=int(a[i+1]),int(a[i+2]); i+=3
        (pyautogui.click if c=='sclick' else pyautogui.doubleClick)(x,y)
    elif c=='key': pyautogui.hotkey(*a[i+1].split('+')); i+=2
    elif c=='type': pyautogui.write(a[i+1],interval=0.02); i+=2
    elif c=='wait': time.sleep(float(a[i+1])); i+=2
    elif c=='fg':
        try: win32gui.SetForegroundWindow(h)
        except Exception as e: print('fg',e)
        i+=1
    elif c=='shot':
        img=ImageGrab.grab(all_screens=True)  # full virtual screen
        img.save(a[i+1]); i+=2
    elif c=='crop':
        im=ImageGrab.grab(all_screens=True); x0,y0,x1,y1=map(int,a[i+2:i+6]); im.crop((x0,y0,x1,y1)).save(a[i+1]); i+=6
    elif c=='wshot':
        ImageGrab.grab(bbox=(L,T,R,B),all_screens=True).save(a[i+1]); i+=2
    time.sleep(0.4)
