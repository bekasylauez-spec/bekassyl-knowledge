import sys,glob,os,time
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
# usage: crop.py N x0 y0 x1 y1 (fractions) [outw]
n=sys.argv[1]; x0,y0,x1,y1=map(float,sys.argv[2:6]); ow=int(sys.argv[6]) if len(sys.argv)>6 else 2000
D='D:/Бекасыл КЖ КМ/РМЦ_КМ/_тексеру'
t=time.mktime((2026,11,14,0,28,0,0,0,-1))
for f in glob.glob(D+'/Парақ_*.png'):
    b=os.path.basename(f)[6:].split('_')[0]
    if b==n and os.path.getmtime(f)>t:
        im=Image.open(f).convert('RGB'); w,h=im.size
        c=im.crop((int(x0*w),int(y0*h),int(x1*w),int(y1*h)))
        s=ow/c.size[0]
        if s<1: c=c.resize((ow,int(c.size[1]*s)))
        out=os.path.join(os.path.dirname(os.path.abspath(__file__)),'s','c_%s_%d_%d.png'%(n,int(x0*100),int(y0*100)))
        c.save(out); print(out)
