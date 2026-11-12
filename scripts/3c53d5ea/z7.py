import fitz, os
out = r"D:\_claude_work\obez_chk\tiles_b"
d = fitz.open(r"D:\_claude_work\obez_chk\album.pdf")
def crop(p, x0,y0,x1,y1, name, dpi=300):
    d[p-1].get_pixmap(dpi=dpi, clip=fitz.Rect(x0,y0,x1,y1)).save(os.path.join(out, name))
crop(21, 720,760,1010,990, "z21_det.png", 260)
crop(21, 400,740,740,990, "z21_nodeA.png", 260)
