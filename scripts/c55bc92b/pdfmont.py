import fitz, sys
from PIL import Image
doc = fitz.open(sys.argv[1]); out = sys.argv[2]; idx = [int(x) for x in sys.argv[3].split(",")]
ims = []
for i in idx:
    pix = doc[i].get_pixmap(dpi=55); im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples); ims.append(im)
W = sum(i.width for i in ims) + 10 * (len(ims) - 1); H = max(i.height for i in ims)
c = Image.new("RGB", (W, H), (255, 255, 255)); x = 0
for im in ims: c.paste(im, (x, 0)); x += im.width + 10
c.save(out); print(len(doc), "pages;", c.size)
