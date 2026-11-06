# python spot.py k relx rely [half=2500] [name]  — crop render around a finding on sheet 7.k
import sys, json, os, gx
import shot as SH
k = int(sys.argv[1]); rx, ry = float(sys.argv[2]), float(sys.argv[3]); h = float(sys.argv[4]) if len(sys.argv) > 4 else 2500
nm = sys.argv[5] if len(sys.argv) > 5 else 'spot'
x0, y0, x1, y1 = json.load(open(os.path.join(gx.S, 'chk', 'sheets.json'), encoding='utf-8'))['7.%d' % k]
out, _ = SH.shot(x0 + rx - h * 1.414, y0 + ry - h, x0 + rx + h * 1.414, y0 + ry + h, nm, 200, 'ISO без полей A3 (420.00 x 297.00 мм)')
from PIL import Image, ImageOps
im = Image.open(out).convert('L'); bb = ImageOps.invert(im).getbbox(); im.crop(bb).save(out); print(out)
