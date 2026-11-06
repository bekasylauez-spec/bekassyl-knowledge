# live plot of a model window -> PNG:  python pv.py x0 y0 x1 y1 name [dpi] [media]
import sys, os, gx, fitz
W = os.path.join(gx.S, 'w')


def pv(x0, y0, x1, y1, name, dpi=150, media=None):
    pdf = os.path.join(W, name + '.pdf')
    if os.path.exists(pdf): os.remove(pdf)
    w, h = x1 - x0, y1 - y0
    if media is None:
        media = 'ISO_full_bleed_A3_(420.00_x_297.00_MM)' if max(w, h) < 25000 else 'ISO_full_bleed_A1_(841.00_x_594.00_MM)'
    out = gx.run([dict(t='plotpdf', win=[x0, y0, x1, y1], file=pdf, media=media)], 'pv')
    if not os.path.exists(pdf): print(out); return None
    d = fitz.open(pdf); p = d[0]
    png = os.path.join(W, name + '.png')
    p.get_pixmap(dpi=dpi).save(png)
    return png


if __name__ == '__main__':
    a = sys.argv
    print(pv(*map(float, a[1:5]), a[5], int(a[6]) if len(a) > 6 else 150, a[7] if len(a) > 7 else None))
