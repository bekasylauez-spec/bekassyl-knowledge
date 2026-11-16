import sys, glob, os, re
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import numpy as np
Image.MAX_IMAGE_PIXELS = None
def runs(m):
    r=[];s=None
    for i,v in enumerate(m):
        if v and s is None: s=i
        if not v and s is not None: r.append((s,i-1)); s=None
    if s is not None: r.append((s,len(m)-1))
    return r
for f in sorted(glob.glob(r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_тексеру\Парақ_КЖ-*.png")):
    key = re.match(r"Парақ_КЖ-(\d+-\d+)_", os.path.basename(f)).group(1)
    a = np.asarray(Image.open(f).convert("L")) < 160
    H, W = a.shape
    pxmm = W/ (420.0 if key=="7-1" else (841.0 if W>6000 else 594.0))
    colc = a.sum(0); rowc = a.sum(1)
    vr = [r for r in runs(colc > 0.6*H) if 5 < r[0] < W-5]
    hr = [r for r in runs(rowc > 0.6*W) if 5 < r[0] < H-5]
    fl, fr = vr[0][1], vr[-1][0]; ft, fb = hr[0][1], hr[-1][0]
    # vertical segments >= 150 px long (table borders etc.) in band right of frame-left
    best_r = None; best_t = None
    # rightmost long vertical segment left of frame right
    for x in range(fr-3, fr-400, -1):
        col = a[ft+5:fb-5, x]
        rr = runs(col)
        if any(e-s > 200 for s,e in rr):
            best_r = x; break
    # topmost long horizontal segment below frame top
    for y in range(ft+3, ft+400):
        row = a[y, fl+5:fr-5]
        rr = runs(row)
        if any(e-s > 300 for s,e in rr):
            best_t = y; break
    print("%s px/mm=%.2f frameR=%d nearest long vertical at x=%s gap=%.1f mm | frameT=%d nearest long horizontal y=%s gap=%.1f mm" % (
        key, pxmm, fr, best_r, (fr-best_r)/pxmm if best_r else -1, ft, best_t, (best_t-ft)/pxmm if best_t else -1))
