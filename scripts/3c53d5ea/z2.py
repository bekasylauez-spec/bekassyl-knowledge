import fitz, os
out = r"D:\_claude_work\obez_chk\tiles_b"
d = fitz.open(r"D:\_claude_work\obez_chk\album.pdf")
def crop(p, x0,y0,x1,y1, name, dpi=330):
    d[p-1].get_pixmap(dpi=dpi, clip=fitz.Rect(x0,y0,x1,y1)).save(os.path.join(out, name))
# q1 scale 2000px/(0.52*1684)=2.284 ; origin 0,0
crop(17, 320,150,560,280, "z17_a.png")
crop(17, 440,470,560,580, "z17_b.png")
