import sys, glob, os, re
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
OUT = r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\3e50b09e-f733-4310-9158-fc456184a213\scratchpad\chk"
os.makedirs(OUT, exist_ok=True)
for f in sorted(glob.glob(r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_тексеру\Парақ_КЖ-*.png")):
    b = os.path.basename(f)
    m = re.match(r"Парақ_КЖ-(\d+)-(\d+)_", b)
    key = "%s-%s" % (m.group(1), m.group(2))
    im = Image.open(f).convert("RGB")
    W, H = im.size
    if W >= 6000:
        xs = [(0, 2200), (2100, 4300), (4200, W)]
        ys = [(0, 2311), (2211, H)]
    else:
        xs = [(0, 2350), (2250, W)]
        ys = [(0, 1677), (1577, H)]
    n = 0
    for r, (y0, y1) in enumerate(ys):
        for c, (x0, x1) in enumerate(xs):
            n += 1
            t = im.crop((x0, y0, x1, y1))
            t.save(os.path.join(OUT, "%s_r%dc%d.png" % (key, r+1, c+1)))
    print(key, W, H, n, "tiles")
