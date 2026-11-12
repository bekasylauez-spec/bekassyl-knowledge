import fitz,sys
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
print(len(d))
for i,p in enumerate(d):
    print(i+1,p.rect.width,p.rect.height)
    p.get_pixmap(dpi=110).save(f"r/p{i+1:02d}.png")
