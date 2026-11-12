import fitz, os
out = r"D:\_claude_work\obez_chk\tiles_b"
d = fitz.open(r"D:\_claude_work\obez_chk\album.pdf")
def crop(p, x0,y0,x1,y1, name, dpi=300):
    d[p-1].get_pixmap(dpi=dpi, clip=fitz.Rect(x0,y0,x1,y1)).save(os.path.join(out, name))
crop(15, 250,880,340,980, "z15_a.png", 500)
crop(15, 1200,270,1290,350, "z15_b.png", 500)
