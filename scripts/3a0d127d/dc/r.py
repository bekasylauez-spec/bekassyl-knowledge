import pymupdf,sys
d=sys.argv[1]
doc=pymupdf.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_тексеру\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
for i,p in enumerate(doc):
    r=p.rect
    print(i+1,round(r.width/72*25.4),round(r.height/72*25.4), p.get_text()[:0])
    pm=p.get_pixmap(dpi=100); pm.save(f"{d}\\p{i+1:02d}.png")
