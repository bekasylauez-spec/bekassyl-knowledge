import sys, glob, os, re
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import numpy as np
from scipy import ndimage
Image.MAX_IMAGE_PIXELS = None
def runs(mask1d):
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
    dark = a < 200
    rowc = dark.sum(1); colc = dark.sum(0)
    hr = [r for r in runs(rowc > 0.6*W) if r[0] > 5 and r[1] < H-5]
    vr = [r for r in runs(colc > 0.6*H) if r[0] > 5 and r[1] < W-5]
    top = hr[0]; bot = hr[-1]; left = vr[0]; right = vr[-1]
    inside = np.zeros_like(dark)
    inside[top[0]-2:bot[1]+3, left[0]-2:right[1]+3] = True
    border = np.zeros_like(dark); border[:3,:]=True; border[-3:,:]=True; border[:,:3]=True; border[:,-3:]=True
    out = dark & ~inside & ~border
    lab, n = ndimage.label(out, structure=np.ones((3,3)))
    objs = ndimage.find_objects(lab)
    # merge boxes close together
    boxes = []
    for sl in objs:
        y0,y1 = sl[0].start, sl[0].stop; x0,x1 = sl[1].start, sl[1].stop
        boxes.append([x0,y0,x1,y1])
    # simple merge
    merged=True
    while merged:
        merged=False
        nb=[]
        while boxes:
            bx=boxes.pop()
            for o in boxes:
                if bx[0]-30<=o[2] and o[0]-30<=bx[2] and bx[1]-30<=o[3] and o[1]-30<=bx[3]:
                    boxes.remove(o); bx=[min(bx[0],o[0]),min(bx[1],o[1]),max(bx[2],o[2]),max(bx[3],o[3])]; merged=True; break
            nb.append(bx)
        boxes=nb
    print(key, "frame L%s R%s T%s B%s" % (left, right, top, bot), "outside-ink groups:", len(boxes))
    for bx in sorted(boxes, key=lambda z:(z[1],z[0])):
        print("    box x%d-%d y%d-%d (%dx%d)" % (bx[0],bx[2],bx[1],bx[3],bx[2]-bx[0],bx[3]-bx[1]))
