import fitz,sys
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
for i in map(int,sys.argv[1:]):
    print("=====",i); print(d[i-1].get_text())
