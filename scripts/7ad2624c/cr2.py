import fitz,sys
S=sys.argv[1]; pg=int(sys.argv[2]); dpi=int(sys.argv[3]); x0,y0,x1,y1=map(float,sys.argv[4].split(",")); out=sys.argv[5]
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
d[pg-1].get_pixmap(dpi=dpi,clip=fitz.Rect(x0,y0,x1,y1)).save(f"{S}/r/{out}.png")
