import sys
from PIL import Image
ims = [Image.open(p).convert("RGB").crop((2430, 1870, 3570, 2170)) for p in sys.argv[2:]]
W = max(i.width for i in ims); H = sum(i.height for i in ims) + 8 * (len(ims) - 1)
c = Image.new("RGB", (W, H), (255, 255, 255)); y = 0
for im in ims: c.paste(im, (0, y)); y += im.height + 8
c.save(sys.argv[1]); print(c.size)
