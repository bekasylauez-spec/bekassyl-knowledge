import sys,glob,os
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
d=r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_тексеру"
n,x1,y1,x2,y2,out=sys.argv[1],*map(int,sys.argv[2:6]),sys.argv[6]
f=glob.glob(d+f"\{n}_лист*.png")[0]
im=Image.open(f).convert("RGB"); k=7000/1800
c=im.crop((int(x1*k),int(y1*k),int(x2*k),int(y2*k)))
s=min(2000/c.width,1500/c.height); c=c.resize((int(c.width*s),int(c.height*s)))
c.save(out)
