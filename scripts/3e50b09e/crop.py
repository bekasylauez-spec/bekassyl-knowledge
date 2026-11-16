import sys,glob,os
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
D='D:/Бекасыл КЖ КМ/РМЦ_КМ/_тексеру/'
O='C:/Users/Admin/AppData/Local/Temp/claude/210ab68cad67e8c1/3e50b09e-f733-4310-9158-fc456184a213/scratchpad/chk2/'
def sheet(n): return glob.glob(D+'Парақ_КЖ-%s_*.png'%n)[0]
n=sys.argv[1]
im=Image.open(sheet(n))
W,H=im.size
if len(sys.argv)==2:
    for i,(x,y) in enumerate([(0,0),(1,0),(0,1),(1,1)]):
        im.crop((x*W//2,y*H//2,(x+1)*W//2,(y+1)*H//2)).save(O+f'{n}_q{i+1}.png')
else:
    x0,y0,x1,y1=map(int,sys.argv[2:6]); sc=float(sys.argv[6]) if len(sys.argv)>6 else 1
    c=im.crop((x0,y0,x1,y1))
    if sc!=1: c=c.resize((int(c.width*sc),int(c.height*sc)),Image.LANCZOS)
    c.save(O+f'{n}_{x0}_{y0}.png')
