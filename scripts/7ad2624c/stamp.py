import fitz
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
for i,p in enumerate(d,1):
    W,H=p.rect.width,p.rect.height
    out=[]
    for b in p.get_text("blocks"):
        if b[0]>W-540 and b[1]>H-160:
            t=b[4].replace("\n"," | ").strip()
            if any(k in t for k in ("Сейлханов","Кулбай","Вислов","Турлыбек","Infratech","Формат","Изм.","Стадия","Проверил","Н.контроль","227-23","Насосная")) : continue
            out.append(t)
    print(i,f"{W:.0f}x{H:.0f}",out)
