import sys, glob, os
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import numpy as np
Image.MAX_IMAGE_PIXELS = None
OUT = r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\3e50b09e-f733-4310-9158-fc456184a213\scratchpad\chk"
key = sys.argv[1]; x0,y0,x1,y1 = map(int, sys.argv[2:6]); name = sys.argv[6]
f = glob.glob(r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_тексеру\Парақ_КЖ-%s_*.png" % key)[0]
im = Image.open(f).convert("RGB")
a = np.asarray(im.convert("L"))[y0:y1, x0:x1] < 160
ys = np.where(a.any(1))[0]; xs = np.where(a.any(0))[0]
if len(ys)==0: print("empty"); sys.exit()
bx0 = max(x0, x0+xs.min()-20); bx1 = min(x1, x0+xs.max()+20); by0 = max(y0, y0+ys.min()-20); by1 = min(y1, y0+ys.max()+20)
c = im.crop((bx0,by0,bx1,by1)); p = os.path.join(OUT, name+".png"); c.save(p)
print(p, (bx0,by0,bx1,by1), c.size)
