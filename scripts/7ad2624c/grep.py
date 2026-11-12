import fitz,re,sys
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
pat=re.compile(sys.argv[1])
for i,p in enumerate(d,1):
    t=p.get_text()
    for m in pat.finditer(t):
        a=max(0,m.start()-50); print(i,repr(t[a:m.end()+50]))
