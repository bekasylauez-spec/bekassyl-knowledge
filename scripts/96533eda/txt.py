import pymupdf,re
p=r"R:\От Шерхан\Завод\Том 14 Водоподготовка ВП-В113\КМ Чертеж\227-23-П-УВПиОС-ВП-В113-КМ (Блок 1 стилі).pdf"
d=pymupdf.open(p)
pat=re.compile(r"Алматы|Royal|BIK|Блок 1|Цех|4П-18|60Ш4|тс\b|СНиП|ГОСТ Р|18\.02\.2025|Блок",re.I)
for i,pg in enumerate(d):
    for b in pg.get_text("words"):
        pass
    t=pg.get_text("blocks")
    for b in t:
        s=b[4].replace("\n"," | ")
        if pat.search(s): print(i+1,[round(x) for x in b[:4]],s[:150])
