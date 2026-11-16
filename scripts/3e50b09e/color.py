import sys, glob, os, re
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import numpy as np
Image.MAX_IMAGE_PIXELS = None
for f in sorted(glob.glob(r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_тексеру\Парақ_КЖ-*.png")):
    key = re.match(r"Парақ_КЖ-(\d+-\d+)_", os.path.basename(f)).group(1)
    a = np.asarray(Image.open(f).convert("RGB")).astype(int)
    r,g,b = a[...,0],a[...,1],a[...,2]
    green = (g > r+40) & (g > b+40)
    red = (r > g+60) & (r > b+60)
    blue = (b > r+60) & (b > g+40)
    ys, xs = np.where(green)
    box = (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else None
    print(key, "green px:", int(green.sum()), "bbox", box, "| red:", int(red.sum()), "| blue:", int(blue.sum()))
