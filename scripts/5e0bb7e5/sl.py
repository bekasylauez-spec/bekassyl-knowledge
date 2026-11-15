import sys,glob
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import os
d=r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_тексеру"
out=sys.argv[1]
for f in glob.glob(d+"\\*.png"):
    n=os.path.basename(f)
    if "КЖ-3-2" in n: tag="a"; 
    elif "КЖ-3-3" in n: tag="b"
    else: continue
    im=Image.open(f).convert("RGB"); print(tag,im.size)
    W,H=im.size
    cols,rows=(3,3) if tag=="a" else (2,2)
    w=W//cols;h=H//rows
    for r in range(rows):
        for c in range(cols):
            box=(max(0,c*w-80),max(0,r*h-80),min(W,(c+1)*w+80),min(H,(r+1)*h+80))
            im.crop(box).save(f"{out}\\{tag}_{r}{c}.png")
