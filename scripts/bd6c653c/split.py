import sys
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB"); W, H = im.size
im.resize((2000, int(2000*H/W)), Image.LANCZOS).save(out + r"\u01_all.png")
for n,(x0,y0) in enumerate([(0,0),(W//2,0),(0,H//2),(W//2,H//2)]):
    im.crop((x0, y0, x0+W//2, y0+H//2)).resize((1750, int(1750*(H//2)/(W//2))), Image.LANCZOS).save(out + rf"\u01_q{n+1}.png")