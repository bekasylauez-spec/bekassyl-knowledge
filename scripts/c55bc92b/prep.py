import os,glob,time
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
S=os.path.dirname(os.path.abspath(__file__))+os.sep+'s'
D='D:/Бекасыл КЖ КМ/РМЦ_КМ/_тексеру'
t=time.mktime((2026,11,14,0,28,0,0,0,-1))
for f in glob.glob(D+'/Парақ_*.png'):
    if os.path.getmtime(f)<t: continue
    n=os.path.basename(f)[6:].split('_')[0]
    im=Image.open(f).convert('RGB')
    w,h=im.size
    im.resize((2400,int(h*2400/w))).save(os.path.join(S,n+'_full.png'))
    print(n,im.size)
