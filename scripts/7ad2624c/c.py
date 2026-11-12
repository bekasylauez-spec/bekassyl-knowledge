import fitz,sys
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
pg,x0,y0,x1,y1,dpi=map(float,sys.argv[1:7]); dpi=int(dpi)
p=d[int(pg)-1]
p.get_pixmap(dpi=dpi,clip=fitz.Rect(x0,y0,x1,y1)).save(sys.argv[7])
