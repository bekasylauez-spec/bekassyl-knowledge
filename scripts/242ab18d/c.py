import sys,glob
from PIL import Image
n,x0,y0,x1,y1,s=sys.argv[1],*map(int,sys.argv[2:6]),float(sys.argv[6])
d=glob.glob('D:/_claude_work/*/check')[0]
im=Image.open(f'{d}/{n}.png').crop((x0,y0,x1,y1))
im=im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS)
im.save('crop.png');print(im.size)
