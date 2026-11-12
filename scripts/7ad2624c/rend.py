import fitz,sys
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
out=sys.argv[1]
print(len(d))
for i,p in enumerate(d,1):
    print(i,p.rect.width,p.rect.height, len(p.get_text()))
    p.get_pixmap(dpi=60).save(f"{out}/s{i:02d}.png")
