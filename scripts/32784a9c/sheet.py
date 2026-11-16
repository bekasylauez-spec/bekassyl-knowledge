import fitz, glob, os, sys
d = sys.argv[1]; out = sys.argv[2]
fs = sorted(glob.glob(os.path.join(d, '*.pdf')))
W, H = 4, (len(fs)+3)//4
cw, ch = 420, 420
sheet = fitz.open(); pg = sheet.new_page(width=cw*W, height=(ch+20)*H)
for i, f in enumerate(fs):
    s = fitz.open(f); p = s[0]
    r = p.rect; txt = len(p.get_text('words')); dr = len(p.get_drawings())
    print(os.path.basename(f), round(r.width/72*25.4), 'x', round(r.height/72*25.4), 'words', txt, 'draw', dr, 'rot', p.rotation)
    x, y = (i % W)*cw, (i//W)*(ch+20)
    pg.show_pdf_page(fitz.Rect(x+5, y+20, x+cw-5, y+ch+15), s, 0)
    pg.insert_text((x+5, y+14), os.path.basename(f), fontsize=12)
    pg.draw_rect(fitz.Rect(x+5, y+20, x+cw-5, y+ch+15), color=(1,0,0), width=0.5)
sheet[0].get_pixmap(dpi=60).save(out)
