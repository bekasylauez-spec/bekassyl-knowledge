import fitz,sys
# args: page(1-based) x0 y0 x1 y1 (fractions) out dpi
d=fitz.open("D:/Бекасыл КЖ КМ/Завод_В113_КМ/227-23-П-УВПиОС-ВП-В113-КМ.pdf")
p=d[int(sys.argv[1])-1]; r=p.rect
f=[float(x) for x in sys.argv[2:6]]
clip=fitz.Rect(r.width*f[0],r.height*f[1],r.width*f[2],r.height*f[3])
p.get_pixmap(dpi=int(sys.argv[7]) if len(sys.argv)>7 else 250,clip=clip).save(sys.argv[6])
