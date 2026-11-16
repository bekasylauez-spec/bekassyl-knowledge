import fitz,sys
d=fitz.open(sys.argv[1]);dpi=int(sys.argv[3])
for i,p in enumerate(d,1):
    p.get_pixmap(dpi=dpi).save(f"{sys.argv[2]}_{i:02d}.png")
