import fitz,sys,math,os
d=fitz.open(sys.argv[1]); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
for i,p in enumerate(d):
    n=i+1
    p.get_pixmap(dpi=40).save(f"{out}/p{n:02d}_full.png")
    r=p.rect; wmm=r.width/72*25.4
    nc=2 if wmm<500 else (3 if wmm<700 else 4)
    nr=2
    for a in range(nr):
        for b in range(nc):
            x0=r.x0+r.width*b/nc; x1=r.x0+r.width*(b+1)/nc
            y0=r.y0+r.height*a/nr; y1=r.y0+r.height*(a+1)/nr
            clip=fitz.Rect(x0-10,y0-10,x1+10,y1+10)&r
            p.get_pixmap(dpi=190,clip=clip).save(f"{out}/p{n:02d}_r{a}c{b}.png")
