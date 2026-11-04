import fitz,sys
# ras.py pdf out.png dpi [crop fx0 fy0 fx1 fy1 fractions]
d=fitz.open(sys.argv[1]); p=d[0]; r=p.rect
dpi=int(sys.argv[3])
clip=None
if len(sys.argv)>4:
    a=[float(v) for v in sys.argv[4:8]]; clip=fitz.Rect(r.x0+a[0]*r.width, r.y0+a[1]*r.height, r.x0+a[2]*r.width, r.y0+a[3]*r.height)
pix=p.get_pixmap(dpi=dpi,clip=clip); pix.save(sys.argv[2]); print(pix.width,pix.height)
