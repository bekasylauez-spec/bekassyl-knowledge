import pymupdf, sys
# zm.py sheet fx0 fy0 fx1 fy1 dpi out   (fractions of page)
s,a,b,c,d,dpi,out = sys.argv[1:8]
p = pymupdf.open(r'fin/'+s+'.pdf')[0]; r=p.rect
clip = pymupdf.Rect(float(a)*r.width,float(b)*r.height,float(c)*r.width,float(d)*r.height)
p.get_pixmap(dpi=int(dpi), clip=clip).save('chk/'+out)
