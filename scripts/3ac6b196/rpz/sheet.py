import sys, glob, os
from PIL import Image, ImageDraw
files=sys.argv[3:]; out=sys.argv[1]; W=int(sys.argv[2])
ims=[]
for f in files:
    try: im=Image.open(f).convert('RGB')
    except Exception as e: continue
    im.thumbnail((W,W)); ims.append((os.path.basename(f),im))
cols=3; rows=(len(ims)+cols-1)//cols
S=Image.new('RGB',(cols*W,rows*(W+20)),'white'); d=ImageDraw.Draw(S)
for k,(n,im) in enumerate(ims):
    x=(k%cols)*W; y=(k//cols)*(W+20); S.paste(im,(x,y+20)); d.text((x+3,y+3),n,fill='red')
S.save(out)
