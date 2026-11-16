import sys, glob, os, re
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import numpy as np
Image.MAX_IMAGE_PIXELS = None
try:
    from scipy import ndimage
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False
print("scipy", HAVE_SCIPY)
def runs(mask1d):
    # return list of (start, end) of True runs
    r=[]; s=None
    for i,v in enumerate(mask1d):
        if v and s is None: s=i
        if not v and s is not None: r.append((s,i-1)); s=None
    if s is not None: r.append((s,len(mask1d)-1))
    return r
for f in sorted(glob.glob(r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_тексеру\Парақ_КЖ-*.png")):
    b = os.path.basename(f)
    m = re.match(r"Парақ_КЖ-(\d+)-(\d+)_", b); key = "%s-%s" % (m.group(1), m.group(2))
    a = np.asarray(Image.open(f).convert("L"))
    H, W = a.shape
    dark = a < 160
    rowc = dark.sum(1); colc = dark.sum(0)
    hr = runs(rowc > 0.6*W); vr = runs(colc > 0.6*H)
    print(key, W, H, "hlines", hr, "vlines", vr)
