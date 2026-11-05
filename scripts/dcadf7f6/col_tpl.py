# -*- coding: utf-8 -*-
"""Column sheet from the user's template «Колонна Км-1» (Шаблон для Кж.dwg, frame 264717.3, 271897.8, A2 1:50).
Rules (Obsidian 03_Колонны + memory column-rules-template): 8 bars (corners + mid faces), one Ø for all columns/ригели,
hoops Ø8 X+2X+X (100|200|100, 50 from zone ends, leftover inside 200 zone), no hoops in the ригель height (mesh С1 ш.100),
bars spliced by накладки С21-Рн staggered corners +600 / mids +1200 above the support, dowels dashed, П Ск1/Ск2 Ø16 at the top."""
import math
import lib
from lib import op, tag, L_THIN
import colgeo

TX, TY = 264717.3, 271897.8
W, H = 29700, 21000
XL = 4102.7                 # column left face (rel)
TL0, TTOP = 9700.0, 19300.0  # template bottom level / top
KG = {8: 0.395, 10: 0.617, 16: 1.578, 20: 2.466, 25: 3.853}


def lv_txt(v):
    s = '%.3f' % (abs(v) / 1000.0); s = s.replace('.', ',')
    return ('+' if v > 0 else ('-' if v < 0 else '')) + s if abs(v) > 0.5 else '0,000'


def build(X0, Y0, c, num):
    mk, b, z0, ztop, hb, d, cnt, conc, hfm, below = (c[k] for k in ('mk', 'b', 'z0', 'ztop', 'hb', 'd', 'cnt', 'conc', 'hfm', 'below'))
    P = 'C%s:' % mk[-1]
    R = lambda h: P + h
    A = lambda x, y: [X0 + x, Y0 + y]
    op(t='copywin', win=[TX - 1, TY - 1, TX + W + 1, TY + H + 1], d=[X0 - TX, Y0 - TY], pre=P)
    dw = b - 400.0
    Hc = ztop - z0
    LT = TL0 + Hc                       # column top (rel)
    Lb = LT - hb                        # ригель bottom
    dY = LT - TTOP
    XR = XL + b                         # right face
    XC0, XM, XC1 = 4142.7, XL + b / 2.0, XR - 40.0
    # ---------- erase template middle storeys ----------
    mid = ['18C37', '18C3A', '18C3F', '18C3C', '18C4D', '18C4E', '18C49',
           '18C54', '18C55', '18C69', '18C6A', '18C6B', '18C6C', '18C6D', '18C6E', '18C6F', '18C70',
           '18C56', '18C57', '18C58', '18C5B', '18C5C', '18C5F', '18C60', '18C61', '18C62', '18C65', '18C68', '18C72', '18C75', '18C78',
           '18C71', '18C7B', '18C7C', '18C83', '18C7D', '18C7E', '18C80', '18C81', '18C82', '18E59', '18E5A', '18E54']
    op(t='erase', h=[R(h) for h in mid])
    # ---------- width ----------
    if dw:
        op(t='stretchwin', win=A(XM - 10, 9000) + A(7000, 21000), d=[dw, 0])
        op(t='movegrp', h=[R('18C48'), R('18C46')], d=[dw / 2, 0])
        op(t='movegrp', h=[R('18E58')], d=[dw / 2, 0])
    # ---------- storeys ----------
    sts = c.get('storeys') or [(ztop, hb)]
    Ls = [TL0] + [TL0 + (zt - z0) for zt, _ in sts]       # level lines (rel)
    hbs = [h_ for _, h_ in sts]
    # ---------- height: top group ----------
    op(t='movegrp', h=[R(h) for h in ('18C4F', '18C50', '18E55', '18E56', '18E53', '18C35')], d=[0, dY])
    for h, x in ((('18C50', 3691.7), ('18C4F', 4971.7 + dw)) if hb != 500 else ()):
        op(t='spmove', h=R(h), items=[[0, X0 + x, Y0 + LT], [1, X0 + x, Y0 + (LT + Lb) / 2], [2, X0 + x, Y0 + Lb], [3, X0 + x, Y0 + Lb]])
    # ---------- concrete: column + stubs at every node + support ----------
    xa, xb = 3691.7, 4971.7 + dw
    left = [A(XL, TL0)]; right = [A(XR, TL0)]
    for i, Lk in enumerate(Ls[1:]):
        lb_ = Lk - hbs[i]
        left += [A(XL, lb_), A(xa, lb_)]; right += [A(XR, lb_), A(xb, lb_)]
        if i < len(Ls) - 2:
            left += [A(xa, Lk), A(XL, Lk)]; right += [A(xb, Lk), A(XR, Lk)]
            for x_ in (xa, xb): lib.pl([A(x_, lb_ - 40), A(x_, Lk + 40)], layer=L_THIN)
    lib.pl(left, layer='Размеры'); lib.pl(right, layer='Размеры')
    lib.pl([A(xa, LT), A(xb, LT)], layer='Размеры')
    lib.pl([A(xa, TL0), A(xb, TL0), A(xb, TL0 - 400), A(xa, TL0 - 400)], layer='Размеры')
    op(t='erase', h=[R('18C4A')])
    lib.hatch([[A(xa, TL0 - 400), A(xb, TL0 - 400), A(xb, TL0), A(xa, TL0)]], pat='ANSI36', sc=20, layer='.', lw=None)
    # ---------- bars: break every storey, накладки corners +600 / mids +1200 above each support ----------
    lay = 'диам%d' % d
    tops = [Ls[k] + 600 for k in range(1, len(Ls) - 1)] + [LT - 20]
    topm = [Ls[k] + 1200 for k in range(1, len(Ls) - 1)] + [LT - 20]
    op(t='plset', h=R('18C51'), p=[A(XC0, TL0 + 600), A(XC0, tops[0])], layer=lay)
    op(t='plset', h=R('18C53'), p=[A(XC1, TL0 + 600), A(XC1, tops[0])], layer=lay)
    op(t='plset', h=R('18C52'), p=[A(XM, TL0 + 1200), A(XM, topm[0])], layer=lay)
    for k in range(1, len(tops)):
        for x_ in (XC0, XC1): lib.pl([A(x_, tops[k - 1]), A(x_, tops[k])], layer=lay)
        lib.pl([A(XM, topm[k - 1]), A(XM, topm[k])], layer=lay)
        for h_, x_, y_ in (('18C43', XC0, tops[k - 1]), ('18C47', XC1, tops[k - 1]), ('18C46', XM, topm[k - 1])):
            op(t='clone', h=R(h_), base=A(0, 0), to=A(0, y_ - (TL0 + 600 if h_ != '18C46' else TL0 + 1200)))
    op(t='plset', h=R('18E55'), p=[A(XC0 - 2, LT - 20 - 400), A(XC0 - 2, LT - 45), A(XC0 + 23, LT - 20), A(XC1 - 23, LT - 20), A(XC1 + 2, LT - 45), A(XC1 + 2, LT - 20 - 400)])
    # ---------- hoops (Ø8) by rule, per storey; no hoops in the ригель/плита height ----------
    allpos = []; chainp = [TL0]; chaint = []; zone_mid = []
    for i in range(len(Ls) - 1):
        lo, hi = Ls[i], Ls[i + 1] - hbs[i]
        try:
            if hi - lo < 2000: raise ValueError('short storey: all hoops 100')
            pos, zones, steps = colgeo.storey_hoops(0.0, hi - lo)
        except Exception:
            S_ = hi - lo - 100; n_ = int(S_ // 100); pos = [50 + 100 * j for j in range(n_ + 1)]; steps = [100.0] * n_
            zones = (n_, 0, 0)
        n1, nm, n3 = zones
        allpos += [lo + p for p in pos]
        for z in sorted({pos[0], pos[n1], pos[n1 + nm], pos[-1]}): lib.pl([A(XC0, lo + z), A(XC1, lo + z)], layer='диам8')
        if nm:
            mid_steps = steps[n1:n1 + nm]
            k200 = sum(1 for s in mid_steps if abs(s - 200) < 1e-6); rr = [s for s in mid_steps if abs(s - 200) > 1e-6]
            seg = [(pos[0], '50'), (pos[n1], '100х%d' % n1), (pos[n1 + nm], ('200х%d' % k200) + (('+%d' % rr[0]) if rr else '')), (pos[-1], '100х%d' % n3)]
        else:
            seg = [(pos[0], '50'), (pos[-1], '100х%d' % (len(pos) - 1))]
        for zz, tt in seg: chainp.append(lo + zz); chaint.append(tt)
        chainp += [hi, Ls[i + 1]]; chaint += ['50', '%d' % hbs[i]]
        zone_mid.append(lo + (pos[n1] + pos[n1 + nm]) / 2 if nm else lo + (pos[0] + pos[-1]) / 2)
    for i in range(len(chainp) - 1):
        if chainp[i + 1] - chainp[i] < 1: continue
        op(t='dim', h=R('18C3B'), p1=A(XR, chainp[i]), p2=A(XR, chainp[i + 1]), dl=A(5848 + dw, chainp[i]), rot=math.pi / 2, txt=chaint[i], layer='Размеры')
    # left dims: per storey + overall
    op(t='dimpts', h=R('18C3B'), p1=A(3149, LT), p2=A(3149, TL0), dl=A(2452, TL0))
    op(t='dimpts', h=R('18C3D'), p1=A(3149, Ls[1]), p2=A(3149, TL0), dl=A(2917, TL0))
    if len(Ls) > 2: op(t='dimpts', h=R('18C3E'), p1=A(3149, LT), p2=A(3149, Ls[1]), dl=A(2917, Ls[1]))
    else: op(t='erase', h=[R('18C3E')])
    # ---------- levels ----------
    op(t='erase', h=[R('18C36'), R('18C39')])
    for zz in Ls: lib.lev(Y0 + TL0 - z0, A(XL, zz), 50)
    # ---------- callouts ----------
    H1 = Ls[1] - TL0
    z1_ = min(2400, H1 * 0.35); lib.note('1', '(%%%%C%d)' % d, A(XL - 900, TL0 + z1_), A(XC0, TL0 + z1_), 50, arrow='oblique')
    lib.note('2', '(%%%%C%d)' % d, A(XL - 900, TL0 + H1 * 0.6), A(XM, TL0 + H1 * 0.6), 50, arrow='oblique')
    if len(Ls) > 2:
        lib.note('3', '(%%%%C%d)' % d, A(XL - 900, (Ls[1] + LT) / 2 + 150), A(XC0, (Ls[1] + LT) / 2 + 150), 50, arrow='oblique')
    lib.note('Х1;Х2', '', A(XR + 250, zone_mid[0] + 600), A(XC1, zone_mid[0] + 300), 50, arrow='oblique')
    op(t='movegrp', h=[R('18E5B')], d=[0, zone_mid[0] - 13418.0])
    op(t='mcset', h=R('18E52'), set={'Center': A(XM, (Lb + LT) / 2), 'Rack': A(XM - 900, Lb - 700)})
    pos = allpos; n1 = 0; nm = 0
    # ---------- sections / details (width) ----------
    if dw:
        for (cx, cy, x0, x1, y0, y1) in ((9713.6, 17988.0, 7300, 11450, 16450, 19100), (14223.0, 18041.0, 12000, 15600, 16300, 19150)):
            op(t='stretchwin', win=A(cx + 1, y0) + A(x1, y1), d=[dw, 0])
            op(t='stretchwin', win=A(x0, y0) + A(cx - 1, y1), d=[-dw, 0])
            op(t='stretchwin', win=A(x0, cy + 1) + A(x1, y1), d=[0, dw])
            op(t='stretchwin', win=A(x0, y0) + A(x1, cy - 1), d=[0, -dw])
        op(t='dyn', h=R('18CFA'), prop='Расстояние1', value=585.099 + 2 * dw)
        op(t='dyn', h=R('18CFA'), prop='Расстояние2', value=577.994 + 2 * dw)
        k = (292.0 + dw) / 292.0
        op(t='dyn', h=R('18D05'), prop='Расстояние1', value=411.928 * k)
        op(t='dyn', h=R('18D05'), prop='Расстояние2', value=408.701 * k)
        # node «Узел расположения сетки С1» (scale 2.6) and meshes С1 (scale 2)
        op(t='txtrep', win=A(9000, 10000) + A(11300, 11000), pairs=[['200', '%d' % (200 + dw / 2)], ['400', '%d' % (400 + dw)]])
        op(t='dimval', win=A(13300, 10800) + A(15000, 13000), pairs=[[370, '%d' % (370 + dw)], [335, '%d' % (335 + dw)]])
        op(t='stretchwin', win=A(18300, 10800) + A(18700, 12300), d=[2 * dw, 0])
    # ---------- texts ----------
    win = A(0, 0) + A(W, H)
    op(t='mcrep', win=win, pairs=[['Ф20', 'Ф%d' % d], ['%%C20', '∅%d' % d], ['∅20', '∅%d' % d], ['Н5', 'Н3' if d == 25 else 'Н5']])
    op(t='txtrep', win=A(0, 0) + A(7000, H), pairs=[['Ф20', 'Ф%d' % d]])
    op(t='settext', h=R('18C35'), s='{\\LКолонна %s}' % mk)
    op(t='settext', h=R('18C86'), s='Колонна %s' % mk)
    op(t='settext', h=R('19531'), s=num)
    op(t='txtrep', win=A(20000, 4000) + A(W, 7000), pairs=[['КЖ-2.1 ... 2.5', '2.1, 2.2'], ['14098-91', '14098-2014']])
    # ведомость деталей
    sx = b + 20; sy = b - 80
    dg = (292.0 + dw) * 1.4142 / 2.0
    vals = {'18DD0': '%d' % sx, '18DD6': '%d' % sx, '18DCD': '%d' % sy, '18DCE': '%d' % sy, '18DDC': '%d' % (2 * (sx + sy)),
            '18DEB': '%d' % (dg + 125), '18DF1': '%d' % (dg + 125), '18DE8': '%d' % (dg + 25), '18DE9': '%d' % (dg + 25),
            '18DF7': '%d' % (2 * (dg + 125 + dg + 25)),
            '18DA2': '%d' % (280 + dw), '18D9F': '%d' % (280 + dw), '18DA7': '%d' % (790 + dw),
            '18DB8': '%d' % (280 + dw), '18DB5': '%d' % (280 + dw), '18DBD': '%d' % (990 + dw)}
    for h, v in vals.items(): op(t='settext', h=R(h), s=v)
    # ---------- spec (only input cells: Ø col3, L col9, qty col10) ----------
    nh = len(pos)
    if len(Ls) > 2:
        L1 = int(Ls[1] - TL0); L2 = L1; L3 = int(LT - 20 - (Ls[1] + 600)); L4 = int(LT - 20 - (Ls[1] + 1200))
    else:
        L1 = int(Hc - 20 - 600); L2 = int(Hc - 20 - 1200); L3 = L4 = 0
    ndw1 = int(hfm - 50 + 600 + 300); ndw2 = int(hfm - 50 + 1200 + 300)
    if len(Ls) > 2: ndw1, ndw2 = L3, L4          # 2nd storey bars; dowels of this column -> Фм-1 spec
    nspl = 16 * (len(Ls) - 1)
    nmesh = sum(int((h_ - 100) // 100) + 1 for h_ in hbs)
    cells = [[0, 2, 'Колонна %s' % mk],
             [1, 3, '8'], [1, 9, '%d' % (2 * (sx + sy))], [1, 10, '%d' % nh],
             [2, 3, '8'], [2, 9, '%d' % (2 * (2 * dg + 150))], [2, 10, '%d' % nh],
             [3, 9, '%d' % (790 + dw)], [4, 9, '%d' % (990 + dw)],
             [5, 3, '%d' % d], [5, 9, '%d' % L1], [5, 10, '4'],
             [6, 3, '%d' % d], [6, 9, '%d' % L2], [6, 10, '4'],
             [7, 3, '%d' % d], [7, 9, '%d' % ndw1], [7, 10, '4'],
             [9, 0, 'Н3' if d == 25 else 'Н5'], [9, 3, '%d' % d], [9, 9, '250' if d == 25 else '200'], [9, 10, '%d' % nspl],
             [10, 10, '%d' % nmesh], [12, 12, '%.2f' % (b * b * Hc / 1e9)], [12, 2, '\\A1;Класс бетона %s, м³' % conc],
             [14, 9, '%d' % (b - 30)], [14, 10, '10']]
    op(t='tset', h=R('18D93'), cells=cells)
    op(t='tset', h=R('18DCA'), cells=[[6, 0, 'Колонна %s' % mk], [5, 6, '%%%%C%d' % d]])
    # dowels from the support (row 8 is free in the template)
    op(t='tset', h=R('18D93'), cells=[[8, 0, '4'], [8, 1, 'ГОСТ 34028-2016'], [8, 2, '%%C'], [8, 3, '%d' % d], [8, 4, 'A'], [8, 5, '500С'], [8, 8, 'L='],
                                    [8, 9, '%d' % ndw2], [8, 10, '4'], [8, 11, '%.2f' % (ndw2 / 1000.0 * KG[d])], [8, 12, '%.2f' % (4 * round(ndw2 / 1000.0 * KG[d], 2))]])
    op(t='trowfmt', h=R('18D93'), src=7, dst=[8])
    # ведомость расхода стали (plain numbers)
    u = lambda L, dd: round(L / 1000.0 * KG[dd], 2)
    m8 = nh * (u(2 * (sx + sy), 8) + u(2 * (2 * dg + 150), 8))
    m16 = 2 * u(790 + dw, 16) + 2 * u(990 + dw, 16)
    m10 = nmesh * 10 * u(b - 30, 10)
    md = 4 * (u(L1, d) + u(L2, d) + u(ndw1, d) + u(ndw2, d)) + nspl * (0.96 if d == 25 else 0.49)
    a500 = m10 + m16 + md
    op(t='tset', h=R('18DCA'), cells=[[6, 1, '0.00'], [6, 2, '%.2f' % m8], [6, 3, '%.2f' % m8], [6, 4, '%.2f' % m10], [6, 5, '%.2f' % m16],
                                    [6, 6, '%.2f' % md], [6, 7, '%.2f' % a500], [6, 8, '%.2f' % (m8 + a500)]])
    return dict(L1=L1, L2=L2, nh=nh, nmesh=nmesh)


COLS = [dict(mk='Км-1', b=500, z0=-4000, ztop=3500, hb=700, d=25, cnt=8, conc='C 30/37 (B40)', hfm=700, below='Фм-1'),
        dict(mk='Км-2', b=500, z0=-4000, ztop=4950, hb=500, d=25, cnt=5, conc='C 30/37 (B40)', hfm=700, below='Фм-1', storeys=[(3500, 200), (4950, 500)]),
        dict(mk='Км-3', b=500, z0=-1200, ztop=4950, hb=500, d=25, cnt=5, conc='C 25/30 (B30)', hfm=900, below='Фм-2')]
