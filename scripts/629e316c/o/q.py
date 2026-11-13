import fitz
d=fitz.open('km.pdf')
for i,p in enumerate(d):
    r=p.rect; w,h=r.width,r.height
    for j,(a,b) in enumerate([(0,0),(1,0),(0,1),(1,1)]):
        c=fitz.Rect(a*w*0.48,b*h*0.48,a*w*0.48+w*0.52,b*h*0.48+h*0.52)
        p.get_pixmap(dpi=190,clip=c).save('q%d_%d.png'%(i+1,j+1))
    p.get_pixmap(dpi=60).save('full%d.png'%(i+1))
