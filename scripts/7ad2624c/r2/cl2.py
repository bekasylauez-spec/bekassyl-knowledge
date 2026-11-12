import fitz,sys
# args: page dpi x0 y0 x1 y1 in 150dpi-display-of-2000 coordinates? use fraction of page
d=fitz.open(r'D:\Бекасыл КЖ КМ\Завод_В113_КМ\_тексеру\227-23-П-УВПиОС-ВП-В113-КМ.pdf')
pg=int(sys.argv[1]);dpi=int(sys.argv[2]);x0,y0,x1,y1=[float(a) for a in sys.argv[3:7]]
f=d[pg-1].rect.width/2000.0
d[pg-1].get_pixmap(dpi=dpi,clip=fitz.Rect(x0*f,y0*f,x1*f,y1*f)).save(rf'r2\{sys.argv[7]}.png')
