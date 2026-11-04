# tiles.py: every sheet cut into halves (portrait: top/bottom; landscape: left/right) at 150 dpi -> pl/t_<sheet>_<i>.png
import fitz, glob, os
for f in sorted(glob.glob('../pl/s[23]?.pdf')):
    p = fitz.open(f)[0]; r = p.rect; n = os.path.basename(f)[:-4]
    parts = [fitz.Rect(0, 0, r.width, r.height * 0.52), fitz.Rect(0, r.height * 0.48, r.width, r.height)] if r.height > r.width else \
            [fitz.Rect(0, 0, r.width * 0.52, r.height), fitz.Rect(r.width * 0.48, 0, r.width, r.height)]
    for i, c in enumerate(parts): p.get_pixmap(dpi=150 if r.width < 1000 else 110, clip=c).save('../pl/t_%s_%d.png' % (n, i))
print('ok')
