import pymupdf
d=pymupdf.open(r'R:\От Шерхан\Завод\Том 14 Водоподготовка ВП-В113\КМ Чертеж\227-23-П-УВПиОС-ВП-В113-КМ (Блок 1 стилі).pdf')
with open("all.txt","w",encoding="utf-8") as f:
    for i,pg in enumerate(d):
        f.write(f"=== PAGE {i+1}\n")
        for b in pg.get_text("blocks"):
            f.write(f"{[round(x) for x in b[:4]]} {b[4].strip().replace(chr(10),' | ')}\n")
