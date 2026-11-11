import fitz,sys
d=fitz.open(sys.argv[1]); pn=int(sys.argv[2]); x0,y0,x1,y1=map(float,sys.argv[3:7]); out=sys.argv[7]; dpi=int(sys.argv[8])
pg=d[pn-1]; r=pg.rect
pg.get_pixmap(dpi=dpi,clip=fitz.Rect(r.width*x0,r.height*y0,r.width*x1,r.height*y1)).save(out)
