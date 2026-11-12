import fitz, os
d = fitz.open(r"D:\_claude_work\obez_chk\album.pdf")
out = r"D:\_claude_work\obez_chk\tiles_c"
def crop(pn):
    p=d[pn-1]; r=p.rect; w,h=r.width,r.height
    c=fitz.Rect(r.x0+w/2+0.58*w/2, r.y0+h/2+0.70*h/2, r.x0+w, r.y0+h*0.995)
    return p.get_pixmap(dpi=110, clip=c)
pages=list(range(27,46))
for k in range(0,len(pages),5):
    grp=pages[k:k+5]
    pix=[crop(p) for p in grp]
    W=max(x.width for x in pix); H=sum(x.height for x in pix)
    big=fitz.Pixmap(fitz.csRGB, fitz.IRect(0,0,W,H), False)
    big.clear_with(255)
    y=0
    for x in pix:
        x2=fitz.Pixmap(fitz.csRGB,x) if x.n!=3 else x
        x2.set_origin(0,y); big.copy(x2, x2.irect); y+=x.height
    big.save(os.path.join(out,"stamps_%d.png"%(k//5)))
print("ok")
