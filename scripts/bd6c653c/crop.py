import glob,os
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
d=r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_тексеру"
for f in sorted(glob.glob(d+r"\u*_лист*.png")):
    n=os.path.basename(f).split("_")[0]
    im=Image.open(f).convert("RGB"); W,H=im.size
    print(n,W,H)
    im.resize((1800,int(1800*H/W))).save(f"{n}_all.png")
    for i in range(2):
        for j in range(2):
            c=im.crop((j*W//2-(60 if j else 0),i*H//2-(60 if i else 0),(j+1)*W//2,(i+1)*H//2))
            c.thumbnail((2000,2000)); c.save(f"{n}_q{i}{j}.png")
