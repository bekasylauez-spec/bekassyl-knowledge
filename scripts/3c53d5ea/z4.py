import fitz, os
out = r"D:\_claude_work\obez_chk\tiles_b"
d = fitz.open(r"D:\_claude_work\obez_chk\album.pdf")
def crop(p, x0,y0,x1,y1, name, dpi=300):
    d[p-1].get_pixmap(dpi=dpi, clip=fitz.Rect(x0,y0,x1,y1)).save(os.path.join(out, name))
crop(19, 140,100,520,340, "z19_s11.png")
crop(19, 540,100,930,340, "z19_s22.png")
crop(19, 50,480,450,660, "z19_s33.png", 400)
