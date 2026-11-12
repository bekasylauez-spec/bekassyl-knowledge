import fitz, os
out = r"D:\_claude_work\obez_chk\tiles_b"
os.makedirs(out, exist_ok=True)
d = fitz.open(r"D:\_claude_work\obez_chk\album.pdf")
for p in range(14, 26):
    pg = d[p]
    r = pg.rect
    print(p+1, r.width, r.height)
    w, h = r.width, r.height
    ov = 0.02
    for i, (ix, iy) in enumerate([(0,0),(1,0),(0,1),(1,1)]):
        x0 = max(0, ix*w/2 - ov*w); x1 = min(w, (ix+1)*w/2 + ov*w)
        y0 = max(0, iy*h/2 - ov*h); y1 = min(h, (iy+1)*h/2 + ov*h)
        pix = pg.get_pixmap(dpi=180, clip=fitz.Rect(x0, y0, x1, y1))
        pix.save(os.path.join(out, f"p{p+1}_q{i+1}.png"))
