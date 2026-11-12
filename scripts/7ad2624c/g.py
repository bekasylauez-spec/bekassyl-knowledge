import fitz,re
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
for i,p in enumerate(d):
    for w in p.get_text("words"):
        if re.fullmatch(r'У\d+[а-яa-z]?|U\d+[a-z]?',w[4]): print(i+1,w[4],[round(x) for x in w[:4]])
# stray single digits within the drawing area on scheme pages
for n in (9,12,13,25,26,27):
    p=d[n-1]; W=p.rect.width;H=p.rect.height
    s=[(w[4],round(w[0]),round(w[1])) for w in p.get_text("words") if re.fullmatch(r'\d',w[4])]
    print(n,len(s),s[:40])
