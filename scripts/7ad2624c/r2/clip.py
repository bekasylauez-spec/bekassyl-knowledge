import fitz,sys
d=fitz.open(r'D:\Бекасыл КЖ КМ\Завод_В113_КМ\_тексеру\227-23-П-УВПиОС-ВП-В113-КМ.pdf')
pg,dpi,x0,y0,x1,y1=[float(a) for a in sys.argv[1:7]]
name=sys.argv[7]
d[int(pg)-1].get_pixmap(dpi=int(dpi),clip=fitz.Rect(x0,y0,x1,y1)).save(rf'r2\{name}.png')
