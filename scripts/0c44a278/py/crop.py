import fitz,sys
pdf,out=sys.argv[1],sys.argv[2]; cl=list(map(float,sys.argv[3:7])); dpi=int(sys.argv[7]) if len(sys.argv)>7 else 250
d=fitz.open(pdf); p=d[0]; r=p.rect
p.get_pixmap(dpi=dpi,clip=fitz.Rect(r.width*cl[0],r.height*cl[1],r.width*cl[2],r.height*cl[3])).save(out)
