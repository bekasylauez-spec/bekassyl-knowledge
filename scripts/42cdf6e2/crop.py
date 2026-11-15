import sys,glob
from PIL import Image
n,x0,y0,x1,y1,out=sys.argv[1:7]
f=glob.glob(f'D:/_claude_work/km3602/v3/img/sheet_{n} *.png')[0]
im=Image.open(f).convert('RGB').crop((int(x0),int(y0),int(x1),int(y1)))
s=min(2000/im.size[0],1400/im.size[1]); 
im.resize((int(im.size[0]*s),int(im.size[1]*s)),Image.LANCZOS).save(out)
