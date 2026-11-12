import fitz, os
out = r"D:\_claude_work\obez_chk\tiles_c"
os.makedirs(out, exist_ok=True)
d = fitz.open(r"D:\_claude_work\obez_chk\album.pdf")
for pn in range(27, 46):
    p = d[pn-1]; r = p.rect; w, h = r.width, r.height
    if pn == 27: print("size", w, h)
    for i in range(2):
        for j in range(2):
            c = fitz.Rect(r.x0 + j*w/2, r.y0 + i*h/2, r.x0 + (j+1)*w/2, r.y0 + (i+1)*h/2)
            p.get_pixmap(dpi=180, clip=c).save(os.path.join(out, "p%d_%d%d.png" % (pn,i,j)))
print("ok")
