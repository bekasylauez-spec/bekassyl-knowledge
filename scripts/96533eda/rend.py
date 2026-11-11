import fitz,sys
p=r"R:\От Шерхан\Завод\Том 14 Водоподготовка ВП-В113\КМ Чертеж\227-23-П-УВПиОС-ВП-В113-КМ (Блок 1 стилі).pdf"
d=fitz.open(p)
print(len(d))
for i,pg in enumerate(d):
    r=pg.rect
    print(i+1,round(r.width),round(r.height), len(pg.get_text()))
    w,h=r.width,r.height
    for q,(x,y) in enumerate([(0,0),(1,0),(0,1),(1,1)]):
        c=fitz.Rect(x*w/2,y*h/2,(x+1)*w/2,(y+1)*h/2)
        pg.get_pixmap(dpi=190,clip=c).save(f"r/p{i+1:02d}_{q+1}.png")
