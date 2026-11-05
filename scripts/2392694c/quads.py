# 4 quarters of sheet 7.k at 190 dpi on A3 paper: python quads.py k
import sys, json, os, gx
import shot as SH
k = int(sys.argv[1]); x0, y0, x1, y1 = json.load(open(os.path.join(gx.S, 'chk', 'sheets.json'), encoding='utf-8'))['7.%d' % k]
w, h = (x1 - x0) / 2, (y1 - y0) / 2
gx.run([{'t': 'save'}], 'sv')
for i, (a, b) in enumerate(((0, 1), (1, 1), (0, 0), (1, 0))):
    out, _ = SH.shot(x0 + a * w, y0 + b * h, x0 + (a + 1) * w, y0 + (b + 1) * h, 'q%d_%d' % (k, i), 190, 'ISO без полей A3 (420.00 x 297.00 мм)', save=False)
    from PIL import Image, ImageOps
    im = Image.open(out).convert('L'); bb = ImageOps.invert(im).getbbox(); im.crop(bb).save(out); print(out)
