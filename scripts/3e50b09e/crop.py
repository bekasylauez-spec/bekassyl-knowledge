import sys, os, glob
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
OUT = r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\3e50b09e-f733-4310-9158-fc456184a213\scratchpad\chk"
# usage: crop.py key x0 y0 x1 y1 name [scale]
key, x0, y0, x1, y1, name = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
sc = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
f = glob.glob(r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_тексеру\Парақ_КЖ-%s_*.png" % key)[0]
im = Image.open(f).convert("RGB").crop((x0, y0, x1, y1))
if sc != 1.0:
    im = im.resize((int(im.size[0]*sc), int(im.size[1]*sc)), Image.LANCZOS)
p = os.path.join(OUT, name + ".png"); im.save(p); print(p, im.size)
