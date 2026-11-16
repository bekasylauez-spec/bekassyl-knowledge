import sys, glob
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import numpy as np
Image.MAX_IMAGE_PIXELS = None
key = sys.argv[1]; x0,x1,y0,y1 = map(int, sys.argv[2:6])
f = glob.glob(r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_тексеру\Парақ_КЖ-%s_*.png" % key)[0]
a = np.asarray(Image.open(f).convert("L"))[y0:y1, x0:x1] < 160
cols = np.where(a.any(0))[0]
# group columns into glyph clusters (gap>=3)
groups=[]; s=None; p=None
for c in cols:
    if s is None: s=p=c; continue
    if c<=p+3: p=c; continue
    groups.append((s,p)); s=p=c
if s is not None: groups.append((s,p))
for g in groups[:12]:
    sub = a[:, g[0]:g[1]+1]
    r = np.where(sub.any(1))[0]
    print("glyph x%d-%d  rows %d-%d  h=%d" % (g[0]+x0, g[1]+x0, r[0]+y0, r[-1]+y0, r[-1]-r[0]+1))
