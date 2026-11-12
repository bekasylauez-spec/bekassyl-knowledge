import fitz,sys
S=sys.argv[1]
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
print(len(d))
for i,p in enumerate(d,1):
    print(i,p.rect.width,p.rect.height,len(p.get_text()))
    p.get_pixmap(dpi=100).save(f"{S}/r/p{i:02d}.png")
