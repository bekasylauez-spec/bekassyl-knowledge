import fitz,re
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
for i,p in enumerate(d,1):
    t=p.get_text()
    m=re.findall(r'[МM]\s?1\s?:\s?\d+',t)
    print(i,m)
