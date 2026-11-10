import sys, pymupdf
SH="C:/Users/beka/AppData/Local/Temp/claude/208a25b89c99599c/b9d48af9-f7a2-4623-89d1-541fa9dfc459/scratchpad/uz4/sh/"
OUT="C:/Users/beka/AppData/Local/Temp/claude/208a25b89c99599c/b9d48af9-f7a2-4623-89d1-541fa9dfc459/scratchpad/aud/c/"
s,x0,y0,x1,y1=sys.argv[1],*map(float,sys.argv[2:6]); dpi=int(sys.argv[6]) if len(sys.argv)>6 else 400
k=1191/2000
p=pymupdf.open(SH+s+".pdf")[0]
pix=p.get_pixmap(dpi=dpi,clip=pymupdf.Rect(x0*k,y0*k,x1*k,y1*k))
fn=OUT+"%s_%d_%d.png"%(s,x0,y0); pix.save(fn); print(fn,pix.width,pix.height)
