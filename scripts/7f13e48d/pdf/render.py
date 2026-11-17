import sys, fitz
src = sys.argv[1]; out = sys.argv[2]
d = fitz.open(src)
print("pages", len(d))
for i, p in enumerate(d):
    r = p.rect
    print(i + 1, round(r.width), round(r.height), "rot", p.rotation)
    z = 1500 / max(r.width, r.height)
    pm = p.get_pixmap(matrix=fitz.Matrix(z, z))
    pm.save(out + "\\p%02d.png" % (i + 1))
try:
    print(d.get_toc())
except Exception as e:
    print("toc err", e)
