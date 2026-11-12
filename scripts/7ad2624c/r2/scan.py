import fitz,re
d=fitz.open(r'D:\Бекасыл КЖ КМ\Завод_В113_КМ\_тексеру\227-23-П-УВПиОС-ВП-В113-КМ.pdf')
pat=re.compile(r'30М|Гн|шаг 3000|7б|7г|16 мм|40Ш1|\b388\b|\d+[,.]\d+$')
for i,p in enumerate(d,1):
    txt=p.get_text()
    for m in re.finditer(r'30М|Гн\s*\[|шаг 3000|7[бг]\b|16 мм|40Ш1|\b388\b',txt):
        print(i,'OLD',m.group(),repr(txt[max(0,m.start()-20):m.end()+20]))
    for w in p.get_text("words"):
        t=w[4]
        if re.fullmatch(r'\d+[.,]\d+',t) and not re.fullmatch(r'[+\-−]?\d+,\d{3}',t) :
            print(i,'FRAC',t,[round(x) for x in w[:4]])
