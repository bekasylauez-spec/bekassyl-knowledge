import fitz,sys
d=fitz.open(r'D:\Бекасыл КЖ КМ\Завод_В113_КМ\_тексеру\227-23-П-УВПиОС-ВП-В113-КМ.pdf')
for i,p in enumerate(d,1):
    p.get_pixmap(dpi=150).save(rf'r2\p{i:02d}.png')
    print(i,p.rect, len(p.get_text("words")))
