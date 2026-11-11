import pymupdf,sys
d=pymupdf.open(r'D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf')
for i,p in enumerate(d):
    n=i+1
    pm=p.get_pixmap(dpi=190)
    pm.save(f'p{n:02d}.png')
    W,H=pm.width,pm.height
    for q,(a,b) in enumerate([(0,0),(1,0),(0,1),(1,1)]):
        r=pymupdf.Rect(a*W/2,b*H/2,(a+1)*W/2,(b+1)*H/2)
        pix=p.get_pixmap(dpi=190,clip=pymupdf.Rect(r.x0*72/190,r.y0*72/190,r.x1*72/190,r.y1*72/190))
        pix.save(f'p{n:02d}_q{q+1}.png')
    print(n,W,H)
