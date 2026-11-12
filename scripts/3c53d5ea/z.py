import fitz, sys, os
out = r"D:\_claude_work\obez_chk\tiles_b"
d = fitz.open(r"D:\_claude_work\obez_chk\album.pdf")
def crop(p, x0,y0,x1,y1, name, dpi=330):
    pix = d[p-1].get_pixmap(dpi=dpi, clip=fitz.Rect(x0,y0,x1,y1))
    pix.save(os.path.join(out, name))
crop(16, 1340,520,1560,730, "z16_a.png")
crop(16, 1030,550,1200,640, "z16_b.png")
