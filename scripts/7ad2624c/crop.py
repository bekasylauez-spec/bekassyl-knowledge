import fitz,sys
pg=int(sys.argv[1]); x0,y0,x1,y1=[float(v) for v in sys.argv[2:6]]; dpi=int(sys.argv[6]) if len(sys.argv)>6 else 150
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
p=d[pg-1]; W,H=p.rect.width,p.rect.height
r=fitz.Rect(x0*W,y0*H,x1*W,y1*H)
p.get_pixmap(dpi=dpi,clip=r).save(f"r/c{pg}_{int(x0*100)}_{int(y0*100)}.png")
print(f"r/c{pg}_{int(x0*100)}_{int(y0*100)}.png")
