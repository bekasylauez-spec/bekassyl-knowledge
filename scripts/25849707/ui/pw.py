import win32gui,win32ui,ctypes,sys
from PIL import Image
h=int(sys.argv[1]); out=sys.argv[2]
l,t,r,b=win32gui.GetWindowRect(h); w,hh=r-l,b-t
hdc=win32gui.GetWindowDC(h); dc=win32ui.CreateDCFromHandle(hdc); m=dc.CreateCompatibleDC()
bmp=win32ui.CreateBitmap(); bmp.CreateCompatibleBitmap(dc,w,hh); m.SelectObject(bmp)
ctypes.windll.user32.PrintWindow(h,m.GetSafeHdc(),2)
i=bmp.GetInfo(); im=Image.frombuffer('RGB',(i['bmWidth'],i['bmHeight']),bmp.GetBitmapBits(True),'raw','BGRX',0,1); im.save(out)
