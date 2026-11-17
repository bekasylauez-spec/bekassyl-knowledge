import sys
from PIL import Image, ImageEnhance
src = sys.argv[1]; out = sys.argv[2]
im = Image.open(src).convert("RGB")
w, h = im.size
def crop(name, box, k=8, contrast=1.8):
    c = im.crop(box)
    c = c.resize((c.size[0] * k, c.size[1] * k), Image.LANCZOS)
    c = ImageEnhance.Contrast(c).enhance(contrast)
    c.save(out + "\\" + name)
    print(name, c.size)
crop("z_bottom.png", (40, 440, 330, 591), 5)      # ground line + dims
crop("z_top.png", (90, 20, 290, 130), 6)          # roof + top landing
crop("z_mid.png", (70, 130, 290, 300), 6)         # middle flights
crop("z_low.png", (60, 290, 300, 480), 6)         # lower flights
