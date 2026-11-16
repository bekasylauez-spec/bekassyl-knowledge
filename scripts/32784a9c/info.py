import fitz, glob, os, sys
mm = 72/25.4
for f in sorted(glob.glob(os.path.join(sys.argv[1], '*.pdf'))):
    p = fitz.open(f)[0]
    W, H = p.rect.width, p.rect.height
    # largest rectangle-like drawing (in displayed coords)
    best = None
    for dr in p.get_drawings():
        r = dr['rect'] * p.rotation_matrix
        a = r.width*r.height
        if best is None or a > best[0]: best = (a, r)
    r = best[1]
    marg = [round(r.x0/mm,1), round(r.y0/mm,1), round((W-r.x1)/mm,1), round((H-r.y1)/mm,1)]
    # stamp name cell: x from W-5-120 to W-5-50 mm, y from H-5-20..H-5-5 ; sheet no cell
    def txt(x0, y0, x1, y1):
        R = fitz.Rect(x0*mm, y0*mm, x1*mm, y1*mm) * ~p.rotation_matrix
        return ' '.join(p.get_textbox(R).split())
    Wm, Hm = W/mm, H/mm
    name = txt(Wm-125, Hm-25, Wm-55, Hm-5)
    lst = txt(Wm-55, Hm-20, Wm-5, Hm-10)
    print(os.path.basename(f), 'frame margins L,T,R,B =', marg, '| name:', name, '| stad/list:', lst)
