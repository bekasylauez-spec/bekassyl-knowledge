import pymupdf,re
doc=pymupdf.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_тексеру\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
for i,p in enumerate(doc):
    t=p.get_text()
    lines=[l.strip() for l in t.split("\n") if l.strip()]
    title=[l for l in lines if re.search(r"(Схема|Разрез|Узл|База|Развертка|Общие|Ведомость|Нагрузки|Титул|Техническая)",l)][:3]
    dec=sorted(set(re.findall(r"(?<![\d,.+\-−])\d{3,}[,.]\d+(?![\d])",t)))
    print(i+1,title)
    # stamp: numbers
    print("   dec:",dec[:15])
