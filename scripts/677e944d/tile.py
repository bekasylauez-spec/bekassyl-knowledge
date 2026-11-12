import os,re,sys,math
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
src='png'; out='t'; os.makedirs(out,exist_ok=True)
for f in sorted(os.listdir(src)):
    m=re.match(r's - Лист - (\S+) - ',f)
    if not m: continue
    n=m.group(1).replace('Т','T')
    im=Image.open(os.path.join(src,f)).convert('RGB'); W,H=im.size
    nx=max(1,math.ceil(W/1350)); ny=max(1,math.ceil(H/1000))
    ov=im.copy(); ov.thumbnail((1560,1560)); ov.save(f'{out}/{n}_ov.png')
    tw=W/nx; th=H/ny
    for j in range(ny):
        for i in range(nx):
            x0=max(0,int(i*tw-40)); y0=max(0,int(j*th-40)); x1=min(W,int((i+1)*tw+40)); y1=min(H,int((j+1)*th+40))
            im.crop((x0,y0,x1,y1)).save(f'{out}/{n}_{j}{i}.png')
    print(n,W,H,nx,ny)
