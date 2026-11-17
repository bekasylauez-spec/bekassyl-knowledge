import sys
from PIL import Image
d = sys.argv[1]
for n in ("p07", "p09", "p10", "p11", "p12", "p13", "p14"):
    im = Image.open(d + "\\" + n + ".png")
    k = 1050 / max(im.size)
    im.resize((int(im.size[0] * k), int(im.size[1] * k)), Image.LANCZOS).save(d + "\\" + n + "_s.png")
    print(n, im.size)
