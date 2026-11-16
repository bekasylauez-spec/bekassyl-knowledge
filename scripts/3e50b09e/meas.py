import sys, glob
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import numpy as np
Image.MAX_IMAGE_PIXELS = None
def load(key):
    f = glob.glob(r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_тексеру\Парақ_КЖ-%s_*.png" % key)[0]
    return np.asarray(Image.open(f).convert("L"))
def rows_with_ink(a, x0, x1, y0, y1, thr=160):
    sub = a[y0:y1, x0:x1] < thr
    r = np.where(sub.any(1))[0]
    return [int(v)+y0 for v in r]
def runs(lst):
    out=[]; s=None; p=None
    for v in lst:
        if s is None: s=p=v; continue
        if v==p+1: p=v; continue
        out.append((s,p)); s=p=v
    if s is not None: out.append((s,p))
    return out
key = sys.argv[1]; x0,x1,y0,y1 = map(int, sys.argv[2:6])
a = load(key)
print(key, "ink row runs in x%d-%d y%d-%d:" % (x0,x1,y0,y1), runs(rows_with_ink(a,x0,x1,y0,y1)))
