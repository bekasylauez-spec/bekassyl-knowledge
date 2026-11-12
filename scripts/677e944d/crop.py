import os,re,sys
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
# usage: crop.py sheet x0 y0 x1 y1 n   (fractions of sheet 0..1)
sh=sys.argv[1]; x0,y0,x1,y1=[float(a) for a in sys.argv[2:6]]; n=int(sys.argv[6])
for f in os.listdir('png'):
    m=re.match(r's - Лист - (\S+) - ',f)
    if m and m.group(1).replace('Т','T')==sh:
        im=Image.open('png/'+f).convert('RGB'); W,H=im.size
        X0,Y0,X1,Y1=int(x0*W),int(y0*H),int(x1*W),int(y1*H); w=(X1-X0)/n
        for i in range(n):
            a=max(0,int(X0+i*w-30)); b=min(W,int(X0+(i+1)*w+30))
            im.crop((a,Y0,b,Y1)).save(f'c/{sh}_{i}.png'); print(sh,i,b-a,Y1-Y0)
