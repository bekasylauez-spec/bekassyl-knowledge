import sys, fitz
from PIL import Image
d = sys.argv[1]
def mk(name, idx, cols):
    ims = [Image.open(f"{d}\\p{i:02d}.png") for i in idx]
    h = 900
    ims = [im.resize((int(im.width*h/im.height), h)) for im in ims]
    W = sum(i.width for i in ims)
    s = Image.new("RGB", (W, h), "white"); x = 0
    for im in ims: s.paste(im, (x, 0)); x += im.width
    s.save(f"{d}\\{name}.png")
mk("o1", [3,4,5], 3); mk("o2", [6,7], 2); mk("o3", [8,9], 2)
