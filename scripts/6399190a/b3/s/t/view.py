import fitz, json, sys, os
W = os.path.dirname(os.path.abspath(__file__)) + r'\w'
LP = json.load(open(W + r'\layplan.json'))
K = 72 / 25.4
def view(sheet, x, y, r=1500, out=None, dpi=200, pdfdir='pdf'):
    sc = LP[sheet]['scale']
    d = fitz.open(f'{W}/{pdfdir}/{sheet}.pdf'); p = d[0]
    H = p.rect.height / K
    px, py = x / sc, H - y / sc; rr = r / sc
    clip = fitz.Rect((px - rr) * K, (py - rr) * K, (px + rr) * K, (py + rr) * K)
    out = out or f'{W}/pv/v_{sheet}_{int(x)}_{int(y)}.png'
    p.get_pixmap(dpi=dpi, clip=clip).save(out); return out
if __name__ == '__main__':
    a = sys.argv; print(view(a[1], float(a[2]), float(a[3]), float(a[4]) if len(a) > 4 else 1500))
