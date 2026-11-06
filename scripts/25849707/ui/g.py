import sys
from PIL import ImageGrab
# args: name x0 y0 x1 y1 in virtual screen coords
n,x0,y0,x1,y1=sys.argv[1],*map(int,sys.argv[2:6])
im=ImageGrab.grab(bbox=(x0,y0,x1,y1),all_screens=True); im.save(n+'.png'); print(im.size)
