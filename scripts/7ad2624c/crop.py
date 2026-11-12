import fitz,sys
S=sys.argv[1]; pg=int(sys.argv[2]); dpi=int(sys.argv[3]); nm=sys.argv[4]
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
p=d[pg-1]; W,H=p.rect.width,p.rect.height
if nm=="Q":  # quarters
    for r in range(2):
        for c in range(2):
            clip=fitz.Rect(c*W/2,r*H/2,(c+1)*W/2,(r+1)*H/2)
            p.get_pixmap(dpi=dpi,clip=clip).save(f"{S}/r/p{pg:02d}_q{r}{c}.png")
else:
    x0,y0,x1,y1=map(float,nm.split(","))
    p.get_pixmap(dpi=dpi,clip=fitz.Rect(x0,y0,x1,y1)).save(f"{S}/r/p{pg:02d}_c.png")
