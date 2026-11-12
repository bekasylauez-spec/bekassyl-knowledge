import fitz,sys
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
for i in map(int,sys.argv[1:]):
    p=d[i-1]
    print("=====",i)
    # words with positions, joined by lines
    for b in p.get_text("blocks"):
        t=b[4].replace("\n"," | ").strip()
        if t: print(f"({b[0]:.0f},{b[1]:.0f}) {t}")
