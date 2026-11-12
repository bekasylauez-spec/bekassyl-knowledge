import fitz, os
out = r"D:\_claude_work\obez_chk\tiles_b"
d = fitz.open(r"D:\_claude_work\obez_chk\album.pdf")
def crop(p, x0,y0,x1,y1, name, dpi=300):
    d[p-1].get_pixmap(dpi=dpi, clip=fitz.Rect(x0,y0,x1,y1)).save(os.path.join(out, name))
crop(24, 150,170,440,400, "z24_console.png", 300)
