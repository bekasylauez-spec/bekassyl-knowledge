import sys, glob
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import numpy as np
Image.MAX_IMAGE_PIXELS = None
key = sys.argv[1]; x0,x1,y0,y1 = map(int, sys.argv[2:6]); frac=float(sys.argv[6]) if len(sys.argv)>6 else 0.8
f = glob.glob(r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_тексеру\Парақ_КЖ-%s_*.png" % key)[0]
a = np.asarray(Image.open(f).convert("L"))[y0:y1, x0:x1] < 160
colfrac = a.mean(0); rowfrac = a.mean(1)
vc = [i+x0 for i,v in enumerate(colfrac) if v>frac]
hr = [i+y0 for i,v in enumerate(rowfrac) if v>frac]
print("vertical lines (cols with >%.0f%% ink):" % (frac*100), vc)
print("horizontal lines (rows with >%.0f%% ink):" % (frac*100), hr)
# rightmost ink column that is not part of a full-height line
anyc = np.where(a.any(0))[0]
print("ink col range", anyc.min()+x0, anyc.max()+x0)
