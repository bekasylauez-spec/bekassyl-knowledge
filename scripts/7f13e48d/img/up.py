import sys
from PIL import Image
src = sys.argv[1]; out = sys.argv[2]
im = Image.open(src)
print(im.size, im.mode)
w, h = im.size
big = im.resize((w * 4, h * 4), Image.LANCZOS)
big.save(out + "\\sk_full.png")
# halves
big.crop((0, 0, w * 4, h * 2)).save(out + "\\sk_top.png")
big.crop((0, h * 2, w * 4, h * 4)).save(out + "\\sk_bot.png")
