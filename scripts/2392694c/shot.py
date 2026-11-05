# render sheets of the live slab DWG: python shot.py x0 y0 x1 y1 name [dpi] [paper]
import sys, os, gx, fitz, shutil
sys.path.insert(0, os.path.join(gx.S, 'an'))
import plt
SNAP = os.path.join(gx.S, 'w', 'snap.dwg')


def shot(x0, y0, x1, y1, name, dpi=170, paper=None, save=True):
    if save:
        gx.run([{'t': 'save'}], 'sv')
    shutil.copy('D:/РАБОЧКА/От Алмас аға/ЖК Галакси/Кж чертеж/2.Схема каркас для клауда (плиты).dwg', SNAP)
    w, h = x1 - x0, y1 - y0
    if paper is None:
        paper = 'ISO без полей A2 (594.00 x 420.00 мм)' if max(w, h) <= 60000 else 'ISO без полей A0 (841.00 x 1189.00 мм)'
    pdf = plt.plot(SNAP, name, x0, y0, x1, y1, paper=paper)
    d = fitz.open(pdf); p = d[0]
    if (p.rect.width < p.rect.height) != (w < h): p.set_rotation(-90)
    out = os.path.join(gx.S, 'w', name + '.png')
    p.get_pixmap(dpi=dpi).save(out)
    return out, pdf


if __name__ == '__main__':
    a = sys.argv
    print(shot(*map(float, a[1:5]), a[5], int(a[6]) if len(a) > 6 else 170))
