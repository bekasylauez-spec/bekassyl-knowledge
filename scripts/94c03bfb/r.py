import fitz,sys
base="D:/_claude_work/Kasymova/revit/_check/"
out=base+"dc/v_"
for n in ["sec3","sec4","sec7"]:
    d=fitz.open(base+n+".pdf")
    for i,p in enumerate(d):
        r=p.rect
        p.get_pixmap(dpi=70).save(f"{out}{n}_{i+1}_all.png")
        w,h=r.width,r.height
        for q,(x,y) in enumerate([(0,0),(1,0),(0,1),(1,1)]):
            c=fitz.Rect(x*w/2,y*h/2,(x+1)*w/2,(y+1)*h/2)
            p.get_pixmap(dpi=190,clip=c).save(f"{out}{n}_{i+1}_q{q}.png")
        print(n,i+1,w,h,file=open(out+"log.txt","a"))
