# look.py oc_output.txt -> pl/look_N.png : crop every flagged spot from the sheet PDFs (5x5 cm), 6 per image, with labels
import sys, re, json, fitz
from PIL import Image, ImageDraw
SH = json.load(open('sheets.json', encoding='utf-8'))
PDF = {'2.1': 's21', '2.2': 's22', '2.3': 's23', '3.1': 's31', '3.2': 's32', '3.3': 's33', '3.4': 's34', '3.5': 's35', '3.6': 's36', '3.7': 's37'}
k = 72 / 25.4; cur = None; spots = []
for ln in open(sys.argv[1], encoding='utf-8'):
    m = re.match(r'== (\S+) (\d+)', ln)
    if m: cur = m.group(1); continue
    m = re.search(r'@\((-?\d+), (-?\d+)\)', ln)
    if m and cur:
        key = (cur, round(int(m.group(1)) / 400), round(int(m.group(2)) / 400))
        if key not in [s[0] for s in spots]: spots.append((key, cur, int(m.group(1)), int(m.group(2)), ln.strip()[:60]))
imgs = []
for key, sh, x, y, lab in spots:
    x0, y0, x1, y1 = SH[sh]; sc = 25 if sh == '3.7' else (50 if sh == '2.3' else 100)
    p = fitz.open('../pl/%s.pdf' % PDF[sh])[0]; H = p.rect.height / k
    X, Y = x / sc, H - y / sc
    pm = p.get_pixmap(dpi=200, clip=fitz.Rect((X - 25) * k, (Y - 25) * k, (X + 25) * k, (Y + 25) * k))
    im = Image.frombytes('RGB', (pm.width, pm.height), pm.samples); d = ImageDraw.Draw(im)
    d.ellipse([im.width / 2 - 12, im.height / 2 - 12, im.width / 2 + 12, im.height / 2 + 12], outline=(255, 0, 0), width=2)
    d.text((5, 5), sh + ' ' + lab, fill=(255, 0, 0)); imgs.append(im)
for i in range(0, len(imgs), 6):
    g = imgs[i:i + 6]; w, h = g[0].size; out = Image.new('RGB', (w * 3, h * 2), 'white')
    for j, im in enumerate(g): out.paste(im, ((j % 3) * w, (j // 3) * h))
    out.save('../pl/look_%d.png' % (i // 6)); print('../pl/look_%d.png' % (i // 6))
