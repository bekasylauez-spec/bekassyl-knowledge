import pymupdf,sys
d=sys.argv[1]
doc=pymupdf.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_тексеру\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
for i,p in enumerate(doc):
    pm=p.get_pixmap(dpi=190)
    from PIL import Image
    im=Image.frombytes("RGB",(pm.width,pm.height),pm.samples)
    W,H=im.size
    for r in range(2):
        for c in range(2):
            im.crop((c*W//2-(60 if c else 0),r*H//2-(60 if r else 0),(c+1)*W//2,(r+1)*H//2)).save(f"{d}\\q{i+1:02d}_{r}{c}.png")
