"""Columns of «Помещение обезвоживания» — reinforcement by Bekassyl's column rules (05.11.2026), «расход с запасом».
Section 700 (X) x 900 (Y), 14Ø28 (4 bars on the 700 faces, 5 on the 900 faces), cover to bar centre 56 (42 to the surface).
Hoops Ø10 A500С: X1 outer, X2 inner around the two middle bars of the 700 faces, X3 inner around the side bars y=±197.
Main bars on dowels Вп1 (corners, +600) / Вп2 (mids, +1200) with накладки Н2 (Ø28, L=280, 2 per joint).
Top: П elements Ø16 — Ск1 across Y (4 pcs), Ск2 across X (3 pcs). Nodes: meshes С1 Ø10 @100 in the beam height."""
import math, sys
sys.path.insert(0, r'D:\РАБОЧКА\Bekassyl\15_Проекты\ЖК Галакси\Инструменты')
import colgeo

KG = {8: 0.395, 10: 0.617, 12: 0.888, 16: 1.578, 20: 2.466, 25: 3.853, 28: 4.834}
BX, BY = 700, 900
CC = 56
XS = [-BX / 2 + CC + k * (BX - 2 * CC) / 3 for k in range(4)]          # -294 -98 98 294
YS = [-BY / 2 + CC + k * (BY - 2 * CC) / 4 for k in range(5)]          # -394 -197 0 197 394
BARS = sorted(set([(x, YS[0]) for x in XS] + [(x, YS[-1]) for x in XS] + [(XS[0], y) for y in YS] + [(XS[-1], y) for y in YS]))
CORNER = [(x, y) for x in (XS[0], XS[-1]) for y in (YS[0], YS[-1])]
D, DH = 28, 10
OFF = D / 2 + DH / 2                                                   # hoop centreline from the bar centre
LAP_N = 280                                                            # накладка Н2 for Ø28
HOOK = 100
X1 = (round(XS[-1] - XS[0] + 2 * OFF), round(YS[-1] - YS[0] + 2 * OFF))           # 626 x 826
X2 = (round(XS[2] - XS[1] + 2 * OFF), X1[1])                                       # 234 x 826
X3 = (X1[0], round(YS[3] - YS[1] + 2 * OFF))                                       # 626 x 432
LH = lambda a: 2 * (a[0] + a[1]) + 2 * HOOK
SK1 = (round(YS[-1] - YS[0]), LAP_N)     # web, legs
SK2 = (round(XS[-1] - XS[0]), LAP_N)
MESH = (BX - 40, BY - 40)                # С1 660 x 860, Ø10 @100


def hoops(z0, beam_bot):
    p, z, s = colgeo.storey_hoops(z0, beam_bot)
    return p


COLS = {
    # mark: dict(n, where, levels of nodes [(slab top, max beam height)], bottom, top)
    'Км-1': dict(n=4, where='Б/2-5', bot=-500, nodes=[(6200, 800)], top=6200),
}


def schedule(mark):
    c = COLS[mark]
    bot, top = c['bot'], c['top']
    zb = top - 20
    hz = []
    lo = bot
    for zs, hb in c['nodes']:
        hz += hoops(lo, zs - hb); lo = zs
    n_h = len(hz)
    n_mesh = sum(int((hb - 100) // 100) + 1 for zs, hb in c['nodes'])
    pos = [  # (pos, d, L, n, note)
        ('1', D, zb - (bot + 600), 4, 'угловые'),
        ('2', D, zb - (bot + 1200), len(BARS) - 4, 'средние'),
        ('Х1', DH, LH(X1), n_h, 'хомут наружный'),
        ('Х2', DH, LH(X2), n_h, 'хомут внутренний'),
        ('Х3', DH, LH(X3), n_h, 'хомут внутренний'),
        ('Ск1', 16, SK1[0] + 2 * SK1[1], 4, 'П-элемент'),
        ('Ск2', 16, SK2[0] + 2 * SK2[1], 3, 'П-элемент'),
        ('Н2', D, LAP_N, len(BARS) * 2, 'накладки'),
    ]
    nx = int(MESH[1] // 100) + 1 if MESH[1] % 100 else int(MESH[1] / 100)
    mesh = [('10', DH, MESH[0], int((MESH[1] - 60) // 100) + 1), ('11', DH, MESH[1], int((MESH[0] - 60) // 100) + 1)]
    conc = BX * BY * (top - bot) / 1e9
    return dict(pos=pos, mesh=mesh, n_mesh=n_mesh, hz=hz, conc=conc)


if __name__ == '__main__':
    for mk in COLS:
        s = schedule(mk)
        tot = 0
        for p in s['pos']:
            m = p[2] / 1000 * KG[p[1]] * p[3]; tot += m
            print(mk, p[0], 'Ø%d' % p[1], p[2], p[3], round(m, 1))
        mm = sum(L / 1000 * KG[d] * n for _, d, L, n in s['mesh'])
        print('mesh', s['mesh'], 'per С1 %.2f kg x %d' % (mm, s['n_mesh']))
        tot += mm * s['n_mesh']
        print(mk, 'total %.1f kg, concrete %.2f, hoops %d' % (tot, s['conc'], len(s['hz'])), X1, X2, X3, LH(X1), LH(X2), LH(X3))
