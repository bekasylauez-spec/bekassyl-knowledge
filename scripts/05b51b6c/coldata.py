"""Columns of «Помещение обезвоживания» by Bekassyl's column rules (05.11.2026), «расход с запасом». Heights/sections as in LIRA.
Lower part 700 (X) x 900 (Y), 14Ø28; upper part (above +11.400) 600x600, 8Ø28 anchored 1710 into the lower part.
Main bars of the lower part break at every storey: joints with накладки Н2 (Ø28, 280, 2 per joint), corners +600, mids +1200.
Hoops Ø10 А500С: Х1 outer, Х2 inner (middle bars of the 700 faces), Х3 inner (side bars) in the lower part; Х4 outer + Х5 rhombus in the upper.
П elements Ø16: Ск1 (across Y) / Ск2 (across X) at the top of the lower part, Ск3 at the top of the upper part. Nodes: meshes С1 Ø10 @100."""
import math, sys
sys.path.insert(0, r'D:\РАБОЧКА\Bekassyl\15_Проекты\ЖК Галакси\Инструменты')
import colgeo

KG = {8: 0.395, 10: 0.617, 12: 0.888, 16: 1.578, 20: 2.466, 25: 3.853, 28: 4.834}
BX, BY = 700, 900
CC = 56
XS = [-BX / 2 + CC + k * (BX - 2 * CC) / 3 for k in range(4)]          # -294 -98 98 294
YS = [-BY / 2 + CC + k * (BY - 2 * CC) / 4 for k in range(5)]          # -394 -197 0 197 394
BARS = sorted(set([(x, YS[0]) for x in XS] + [(x, YS[-1]) for x in XS] + [(XS[0], y) for y in YS] + [(XS[-1], y) for y in YS]))
UB = 600; UO = UB / 2 - CC                                             # upper 600x600, bars at ±244
UBARS = [(x, y) for x in (-UO, 0, UO) for y in (-UO, 0, UO) if not (x == 0 and y == 0)]
D, DH = 28, 10
OFF = D / 2 + DH / 2
LAP_N = 280
ANCH = 1710                                                            # 61d
HOOK = 100
X1 = (round(XS[-1] - XS[0] + 2 * OFF), round(YS[-1] - YS[0] + 2 * OFF))           # 626 x 826
X2 = (round(XS[2] - XS[1] + 2 * OFF), X1[1])                                       # 234 x 826
X3 = (X1[0], round(YS[3] - YS[1] + 2 * OFF))                                       # 626 x 432
X4 = (round(2 * UO + 2 * OFF), round(2 * UO + 2 * OFF))                            # 526 x 526
X5R = UO + OFF                                                                     # rhombus half-diagonal 263
LH = lambda a: 2 * (a[0] + a[1]) + 2 * HOOK
L_X5 = round(4 * math.sqrt(2) * X5R + 2 * HOOK)
SK1 = (round(YS[-1] - YS[0] + D + 16), LAP_N)       # legs outside the bars: axis distance + (Ø28 + Ø16)
SK2 = (round(XS[-1] - XS[0] + D + 16), LAP_N)
SK3 = (round(2 * UO + D + 16), LAP_N)
MESH = (BX - 40, BY - 40)                # С1 660 x 860, Ø10 @100
CONS = dict(l=600, h=850)                # КН-1 (Км-4, Км-5): 600 from the column face, towards the crane line

COLS = {
    # nodes: (slab/beam top, max beam height, stubs: -1 / 1 / both 0 / none None)
    'Км-1': dict(n=4, where='Б/2-5', bot=-500, z1=None, top=6200, nodes=[(6200, 800, 0)]),
    'Км-2': dict(n=3, where='А,Б,В/7', bot=-500, z1=None, top=5950, nodes=[(5950, 700, 0)]),
    'Км-3': dict(n=3, where='А,Б,В/8', bot=-500, z1=None, top=5700, nodes=[(5700, 700, 0)]),
    'Км-4': dict(n=8, where='А,В/2-5', bot=-500, z1=11400, top=13700, nodes=[(6200, 800, 1), (11400, 600, None)], cons=True),
    'Км-5': dict(n=4, where='А,В/1,6', bot=-500, z1=11400, top=13700, nodes=[(6200, 700, 1), (11400, 850, 1)]),
    'Км-6': dict(n=2, where='Б/1,6', bot=-500, z1=11400, top=14300, nodes=[(6200, 700, 0), (11400, 850, 0)]),
}


def hoops(z0, beam_bot):
    p, z, s = colgeo.storey_hoops(z0, beam_bot)
    return p


def storeys(c):
    """lower-part storeys (z_lo, z_hi, beam_h) and the upper part (z1, top, 0)"""
    st = []; lo = c['bot']
    for zs, hb, _ in c['nodes']:
        st.append((lo, zs, hb)); lo = zs
    if c['z1']: st.append((c['z1'], c['top'], 0))
    return st


def schedule(mark):
    c = COLS[mark]
    bot, top, z1 = c['bot'], c['top'], c['z1']
    zend = (z1 or top) - 20                       # lower bars end
    st = storeys(c)
    low = [s for s in st if not z1 or s[1] <= z1]
    joints = [bot] + [s[1] for s in low[:-1]]     # storey bottoms where bars are joined
    pos = []
    k = 1
    for i, j0 in enumerate(joints):
        j1c = joints[i + 1] + 600 if i + 1 < len(joints) else zend + 0
        j1m = joints[i + 1] + 1200 if i + 1 < len(joints) else zend
        pos.append((str(k), D, j1c - (j0 + 600), 4, 'угловые, этаж %d' % (i + 1))); k += 1
        pos.append((str(k), D, j1m - (j0 + 1200), len(BARS) - 4, 'средние, этаж %d' % (i + 1))); k += 1
    if z1:
        pos.append((str(k), D, (top - 20) - (z1 - ANCH), len(UBARS), 'верхняя часть 600х600')); k += 1
    hz_low = []
    for lo, hi, hb in low: hz_low += hoops(lo, hi - hb)
    pos += [('Х1', DH, LH(X1), len(hz_low), 'хомут наружный'), ('Х2', DH, LH(X2), len(hz_low), 'хомут внутренний'),
            ('Х3', DH, LH(X3), len(hz_low), 'хомут внутренний')]
    hz_up = hoops(z1, top) if z1 else []
    if z1:
        pos += [('Х4', DH, LH(X4), len(hz_up), 'хомут верхней части'), ('Х5', DH, L_X5, len(hz_up), 'ромб верхней части')]
    pos += [('Ск1', 16, SK1[0] + 2 * SK1[1], 4, 'П-элемент'), ('Ск2', 16, SK2[0] + 2 * SK2[1], 3, 'П-элемент')]
    if z1: pos.append(('Ск3', 16, SK3[0] + 2 * SK3[1], 4, 'П-элемент верха'))
    pos.append(('Н2', D, LAP_N, len(BARS) * 2 * len(joints), 'накладки'))
    if c.get('cons'):
        pos += [('К1', D, (CONS['l'] - 30) + (BY - 60) + 600 + 400, 4, 'консоль, верх'),
                ('Хк', DH, 2 * (BX - 60 + CONS['h'] - 60) + 2 * HOOK, int((CONS['l'] - 60) // 100) + 1, 'хомут консоли')]
    n_mesh = sum(int((hb - 100) // 100) + 1 for zs, hb, _ in c['nodes'])
    mesh = [('10', DH, MESH[0], int((MESH[1] - 60) // 100) + 1), ('11', DH, MESH[1], int((MESH[0] - 60) // 100) + 1)]
    conc = BX * BY * ((z1 or top) - bot) / 1e9 + (UB * UB * (top - z1) / 1e9 if z1 else 0) + (BX * CONS['l'] * CONS['h'] / 1e9 if c.get('cons') else 0)
    return dict(pos=pos, mesh=mesh, n_mesh=n_mesh, hz_low=hz_low, hz_up=hz_up, conc=conc, joints=joints, zend=zend)


if __name__ == '__main__':
    for mk in COLS:
        s = schedule(mk); tot = 0
        for p in s['pos']:
            tot += p[2] / 1000 * KG[p[1]] * p[3]
        tot += sum(L / 1000 * KG[d] * n for _, d, L, n in s['mesh']) * s['n_mesh']
        print(mk, len(s['pos']), [(p[0], p[2], p[3]) for p in s['pos']], 'mesh', s['n_mesh'], 'total %.1f kg conc %.2f' % (tot, s['conc']))
