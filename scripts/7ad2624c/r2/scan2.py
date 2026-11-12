import fitz,re,sys
sys.stdout.reconfigure(encoding='utf-8')
d=fitz.open(r'D:\Бекасыл КЖ КМ\Завод_В113_КМ\_тексеру\227-23-П-УВПиОС-ВП-В113-КМ.pdf')
for i,p in enumerate(d,1):
    txt=p.get_text()
    for m in re.finditer(r'30\s*М|Гн\s*\[|шаг\s*3000|7[бг]\b|16\s*мм|40Ш1|388',txt):
        print(i,'OLD',repr(txt[max(0,m.start()-25):m.end()+25]))
    if i in (3,4,5,6,8,1,2): continue
    for w in p.get_text("words"):
        t=w[4]
        if re.fullmatch(r'[\d]+[.,]\d+',t):
            print(i,'FRAC',t,[round(x) for x in w[:4]])
