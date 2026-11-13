import sys, fitz
d = fitz.open(sys.argv[1])
print("pages", len(d))
for i, p in enumerate(d):
    r = p.rect
    z = 1500 / max(r.width, r.height)
    p.get_pixmap(matrix=fitz.Matrix(z, z)).save(f"{sys.argv[2]}\\p{i:02d}.png")
    print(i, round(r.width/72*25.4), round(r.height/72*25.4))
