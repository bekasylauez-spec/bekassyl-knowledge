import pymupdf, sys, os
src, dst = sys.argv[1], sys.argv[2]
for s in sys.argv[3:]:
    d = pymupdf.open(os.path.join(src, s + '.pdf'))
    p = d[0]; r = p.rect
    print(s, round(r.width/72*25.4), round(r.height/72*25.4), len(d))
    p.get_pixmap(dpi=40).save(os.path.join(dst, f'{s}_full.png'))
    W, H = r.width/2, r.height/2
    for i,(x,y) in enumerate([(0,0),(1,0),(0,1),(1,1)]):
        clip = pymupdf.Rect(x*W, y*H, x*W+W, y*H+H)
        p.get_pixmap(dpi=170, clip=clip).save(os.path.join(dst, f'{s}_q{i+1}.png'))
