# -*- coding: utf-8 -*-
"""Ригель sheets from the user's template «Ригель Рм-1» (Шаблон для Кж.dwg, frame 336417.3, 271897.8, A2 1:50).
Rules (Obsidian 04_Ригели): ригель from edge to edge = one element, marks Рм-N (variants Рм-N.1); main Ø20..32 (one Ø for all
columns/ригели -> Ø25); b>300 -> 4+4 bars and 2 hoops (each around 3 bars), b<=300 -> 3+3 and one hoop; hoops Ø8 A240
X+2X+X per clear span (100 / 200 / 100), Ск1 Ø16 at the ends, bars spliced with накладки С21-Рн (bottom over supports, top in span)."""
import math
import lib
from lib import op, L_THIN
import colgeo

TX, TY = 336417.3, 271897.8
W, H = 29700, 21000
KG = {8: 0.395, 10: 0.617, 12: 0.888, 16: 1.578, 20: 2.466, 25: 3.853}
D = 25
YB = 17802.0             # beam bottom line in the template elevation (rel)
X_LEFT = 2600.0          # first support axis (rel)
X_MAX = 28300.0          # elevation must end before this x (rel)


def lv_txt(v):
    s = ('%.3f' % (abs(v) / 1000.0)).replace('.', ',')
    return ('+' if v > 0 else '-') + s if abs(v) > 0.5 else '0,000'


def brk_v(A, x, y0, y1):
    ym = (y0 + y1) / 2
    lib.pl([A(x, y0 - 60), A(x, ym - 60), A(x - 40, ym - 20), A(x + 40, ym + 20), A(x, ym + 60), A(x, y1 + 60)], layer=L_THIN)


def brk_h(A, y, x0, x1):
    xm = (x0 + x1) / 2
    lib.pl([A(x0 - 60, y), A(xm - 60, y), A(xm - 20, y + 40), A(xm + 20, y - 40), A(xm + 60, y), A(x1 + 60, y)], layer=L_THIN)


def build(X0, Y0, r, num):
    mk, b, h, sup, axes, lev_top, cnt, conc = (r[k] for k in ('mk', 'b', 'h', 'sup', 'axes', 'ztop', 'cnt', 'conc'))
    P = 'R%s:' % mk.replace('Рм-', 'm').replace('Рб-', 'b').replace('.', '_')
    R = lambda hh: P + hh
    A = lambda x, y: [X0 + x, Y0 + y]
    op(t='copywin', win=[TX - 1, TY - 1, TX + W + 1, TY + H + 1], d=[X0 - TX, Y0 - TY], pre=P)
    # ---- erase template elevation + section drawing (keep titles, tables, details) ----
    keep = {'1ADC8', '1AD4F'}
    PR = {}
    for hp in ('1ADE9', '1ADA9', '1ADA1', '1AD9F', '1AD4E'):
        PR[hp] = P + 'PR' + hp; op(t='clone', h=R(hp), tag=PR[hp]); op(t='move', h=[PR[hp]], d=[0, -30000])
    op(t='eraseregion', win=A(1500, 13900) + A(16600, 19350), mode='inside', keep=[R(k) for k in keep])
    op(t='eraseregion', win=A(3800, 6900) + A(11200, 12600), mode='inside', keep=[R(k) for k in keep])
    R0 = R
    R = lambda hh: PR.get(hh) or R0(hh)
    # ---- geometry along the ригель: x = 0 at the first support axis ----
    L = sup[-1][0] - sup[0][0]
    x_end0 = sup[0][0] - sup[0][1] / 2.0; x_end1 = sup[-1][0] + sup[-1][1] / 2.0
    avail = X_MAX - X_LEFT
    brk = None
    if x_end1 - sup[0][0] + 400 > avail:      # break: keep the first 2 spans and the last span
        xa = sup[2][0] - sup[2][1] / 2 - 900; xb = sup[-2][0] + sup[-2][1] / 2 + 900
        brk = (xa, xb, 1200.0)
    def fx(x):
        x = x - sup[0][0]
        if brk:
            xa, xb, g = brk[0] - sup[0][0], brk[1] - sup[0][0], brk[2]
            if x > xa: x = xa + g + (x - xb) if x >= xb else xa + g / 2
        return X_LEFT + x
    def vis(x):
        return not brk or x <= brk[0] or x >= brk[1]
    yb, yt = YB, YB + h
    # ---- concrete: spans and supports ----
    for i in range(len(sup) - 1):
        a = sup[i][0] + sup[i][1] / 2; c = sup[i + 1][0] - sup[i + 1][1] / 2
        segs = [(a, c)]
        if brk and a < brk[0] < c: segs = [(a, brk[0]), (brk[1], c)] if brk[1] < c else [(a, brk[0])]
        elif brk and a < brk[1] < c and a > brk[0]: segs = [(brk[1], c)]
        elif brk and brk[0] <= a and c <= brk[1]: segs = []
        for s0, s1 in segs:
            lib.pl([A(fx(s0), yb), A(fx(s1), yb)], layer='Размеры'); lib.pl([A(fx(s0), yt), A(fx(s1), yt)], layer='Размеры')
    for xs, w, kind in sup:
        if not vis(xs): continue
        x0, x1 = fx(xs - w / 2), fx(xs + w / 2)
        if kind == 'beam':
            lib.rect(*(A(x0, yb) + A(x1, yt)), layer=L_THIN, ltype='HIDDEN2', ltscale=15)
            continue
        lo = yb - 350 if kind != 'wall_top' else yb
        lib.pl([A(x0, yt + 350), A(x0, lo)], layer='Размеры'); lib.pl([A(x1, yt + 350), A(x1, lo)], layer='Размеры')
        brk_h(A, yt + 350, x0, x1); brk_h(A, lo, x0, x1)
    if brk:
        gx0, gx1 = fx(brk[0]), fx(brk[1])
        for gx in (gx0, gx1): brk_v(A, gx, yb, yt)
    # ---- bars ----
    cv = 30 + 8 + D / 2.0
    lay = 'диам%d' % D
    xs0, xs1 = x_end0 + 20, x_end1 - 20
    def bar(y, z0, z1):
        pts = [(z0, z1)] if not brk else [(z0, brk[0]), (brk[1], z1)]
        for p0, p1 in pts: lib.pl([A(fx(p0), y), A(fx(p1), y)], layer=lay)
    bar(yb + cv, xs0, xs1); bar(yt - cv, xs0, xs1)
    if h >= 600: bar((yb + yt) / 2, xs0, xs1)
    for xe, sg in ((xs0, 1), (xs1, -1)):    # Ск1 at the ends
        lib.pl([A(fx(xe) + sg * 200, yb + cv - 20), A(fx(xe), yb + cv - 20), A(fx(xe), yt - cv + 20), A(fx(xe) + sg * 200, yt - cv + 20)], layer='диам16')
    # splices (накладки) every 11.7 m stock: bottom over supports, top at mid-span
    spl = []
    if xs1 - xs0 > 11700:
        n = int((xs1 - xs0) // 11000)
        inner = [s[0] for s in sup[1:-1]]
        for k in range(1, n + 1):
            xt = xs0 + k * (xs1 - xs0) / (n + 1)
            xbtm = min(inner, key=lambda q: abs(q - xt)) if inner else xt
            spl.append((xbtm, yb + cv)); spl.append((xt + 400, yt - cv))
    for xsp, ysp in spl:
        if vis(xsp): lib.rect(*(A(fx(xsp) - 100, ysp - 15) + A(fx(xsp) + 100, ysp + 15)), layer=lay)
    # ---- stirrups per clear span (X + 2X + X) + chain ----
    ych = 16399.0
    chain = []; nh = 0
    for i in range(len(sup) - 1):
        a = sup[i][0] + sup[i][1] / 2; c = sup[i + 1][0] - sup[i + 1][1] / 2
        try:
            if c - a < 2000: raise ValueError
            pos, zones, steps = colgeo.storey_hoops(a, c)
            n1, nm, n3 = zones
            mid = steps[n1:n1 + nm]; k200 = sum(1 for s in mid if abs(s - 200) < 1e-6); rr = [s for s in mid if abs(s - 200) > 1e-6]
            seg = [(a, None), (pos[0], '50'), (pos[n1], '100х%d' % n1), (pos[n1 + nm], ('200х%d' % k200) + ('+%d' % rr[0] if rr else '')), (pos[-1], '100х%d' % n3), (c, '50')]
            bnd = [pos[0], pos[n1], pos[n1 + nm], pos[-1]]
        except Exception:
            n_ = int((c - a - 100) // 100); pos = [a + 50 + 100 * j for j in range(n_ + 1)]
            seg = [(a, None), (pos[0], '50'), (pos[-1], '100х%d' % n_), (c, '%d' % (c - pos[-1]))]
            bnd = [pos[0], pos[-1]]
        nh += len(pos)
        for z in bnd:
            if vis(z): lib.pl([A(fx(z), yb + 15), A(fx(z), yt - 15)], layer='диам8')
        chain += seg
    pts = [sup[0][0] - sup[0][1] / 2] + [p for p, t in chain]
    for i in range(len(chain)):
        p0 = chain[i - 1][0] if i else sup[0][0] - sup[0][1] / 2
        p1, tt = chain[i]
        if p1 - p0 < 1 or not (vis(p0) and vis(p1)): continue
        op(t='dim', h=R('1ADE9'), p1=A(fx(p0), yb), p2=A(fx(p1), yb), dl=A(fx(p0), ych), rot=0.0, txt=tt or '', layer='Размеры')
    # ---- axes + axis chain + overall ----
    for (nm_, xa_) in axes:
        if not vis(xa_): continue
        t = lib.tag('ax'); op(t='clone', h=R('1AD9F'), tag=t)
        op(t='axis', h=t, s=A(fx(xa_), yt + 700), e=A(fx(xa_), 14955), val=nm_, scale=50)
    ax_x = [x for _, x in axes]
    for i in range(len(ax_x) - 1):
        if vis(ax_x[i]) and vis(ax_x[i + 1]):
            op(t='dim', h=R('1ADA9'), p1=A(fx(ax_x[i]), 14955), p2=A(fx(ax_x[i + 1]), 14955), dl=A(fx(ax_x[i]), 15555), rot=0.0, txt='', layer='Размеры')
        elif brk:
            op(t='dim', h=R('1ADA9'), p1=A(fx(ax_x[i]), 14955), p2=A(fx(ax_x[i + 1]), 14955), dl=A(fx(ax_x[i]), 15555), rot=0.0,
               txt='%d' % (ax_x[i + 1] - ax_x[i]), layer='Размеры')
    op(t='dim', h=R('1ADA1'), p1=A(fx(ax_x[0]), 14955), p2=A(fx(ax_x[-1]), 14955), dl=A(fx(ax_x[0]), 15205), rot=0.0,
       txt=('%d' % (ax_x[-1] - ax_x[0])) if brk else '', layer='Размеры')
    # ---- levels (top of ригель) and beam height dims ----
    lib.lev(Y0 + yt - lev_top, A(fx(x_end0) - 100, yt), 50)
    op(t='dim', h=R('1ADE9'), p1=A(fx(x_end0) - 400, yb), p2=A(fx(x_end0) - 400, yt), dl=A(fx(x_end0) - 700, yb), rot=math.pi / 2, txt='', layer='Размеры')
    # ---- callouts ----
    xm1 = (sup[0][0] + sup[1][0]) / 2
    lib.note('1', '(%%%%C%d)' % D, A(fx(xm1) + 500, yt + 600), A(fx(xm1), yt - cv), 50, arrow='oblique')
    lib.note('1', '(%%%%C%d)' % D, A(fx(xm1) + 500, yb - 500), A(fx(xm1), yb + cv), 50, arrow='oblique')
    if h >= 600: lib.note('2', '(%%C12)', A(fx(xm1) + 1700, yb - 500), A(fx(xm1) + 1200, (yb + yt) / 2), 50, arrow='oblique')
    lib.note('Х1(%%C8)', 'ш.100;200', A(fx(x_end1) + 300, yb - 300), A(fx(x_end1) - sup[-1][1] - 60, yb + 15), 50, arrow='oblique')
    lib.note('Ск1', '(%%C16)', A(fx(x_end0) - 900, yt + 500), A(fx(xs0), yt - cv + 20), 50, arrow='oblique')
    # section mark 1-1 in the first span
    xsec = fx(xm1 + 600)
    lib.section('1', A(xsec, yt + 450), A(xsec, yb - 350), 50)
    # ---- section 1-1 (x2 drawing) ----
    k2 = 2.0; SX, SY = 7300.0 - k2 * b / 2, 12350.0 - k2 * h
    S = lambda x, y: A(SX + k2 * x, SY + k2 * y)
    lib.pl([S(0, 0), S(b, 0), S(b, h), S(0, h)], layer='Размеры', closed=True)
    nb = 4 if b > 300 else 3
    bx = [cv + (b - 2 * cv) * k / (nb - 1) for k in range(nb)]
    hc = 30 + 4
    if nb == 4:
        for i0, i1 in ((0, 2), (1, 3)):
            lib.pl([S(bx[i0] - D / 2 - 4, hc), S(bx[i1] + D / 2 + 4, hc), S(bx[i1] + D / 2 + 4, h - hc), S(bx[i0] - D / 2 - 4, h - hc)], layer='диам8', closed=True)
    else:
        lib.pl([S(hc, hc), S(b - hc, hc), S(b - hc, h - hc), S(hc, h - hc)], layer='диам8', closed=True)
    for x in bx:
        for y in (cv, h - cv): op(t='circle', c=S(x, y), r=k2 * D / 2, layer=lay)
    if h >= 600:
        for x in (cv, b - cv): op(t='circle', c=S(x, h / 2), r=k2 * 6, layer='диам12')
        lib.pl([S(hc, h / 2), S(b - hc, h / 2)], layer='диам8')
    dd = R('1AD4E')
    chain_x = [0, cv - D / 2] + [x for x in bx] + [b - cv + D / 2, b]
    for i in range(len(chain_x) - 1):
        if chain_x[i + 1] - chain_x[i] < 1: continue
        op(t='dim', h=dd, p1=S(chain_x[i], 0), p2=S(chain_x[i + 1], 0), dl=S(chain_x[i], -150), rot=0.0, layer='0_ANNOT_Dimensions')
    op(t='dim', h=dd, p1=S(0, 0), p2=S(b, 0), dl=S(0, -300), rot=0.0, layer='0_ANNOT_Dimensions')
    op(t='dim', h=dd, p1=S(0, 0), p2=S(0, h), dl=S(-250, 0), rot=math.pi / 2, layer='0_ANNOT_Dimensions')
    lib.note('1', '%d(%%%%C%d)' % (nb, D), S(b + 150, h + 200), S(bx[-1], h - cv), 50, arrow='oblique')
    lib.note('1', '%d(%%%%C%d)' % (nb, D), S(b + 150, -200), S(bx[-1], cv), 50, arrow='oblique')
    lib.note('Х1(%%C8)', 'ш.100;200', S(b + 250, h * 0.6), S(b - hc, h * 0.55), 50, arrow='oblique')
    op(t='movegrp', h=[R('1AD4F')], d=[0, 0])
    # ---- texts ----
    op(t='settext', h=R('1ADC8'), s='{\\LРигель %s}' % mk if mk.startswith('Рм') else '{\\LРандбалка %s}' % mk)
    nm_full = ('Ригель ' if mk.startswith('Рм') else 'Рандбалка ') + mk
    op(t='settext', h=R('1AE19'), s=nm_full); op(t='settext', h=R('1AE1B'), s=num)
    # ведомость деталей: Х1 (one hoop size), Ск1
    hw = int(round((b - 80 - D) * 2 / 3.0 + D)) if nb == 4 else b - 80
    hh = h - 80
    for hd, v in (('1AD68', hh), ('1AD71', hh + 100), ('1AD69', hw), ('1AD6B', hw + 100), ('1AD77', 2 * (hh + hw) + 200),
                  ('1AD85', hh), ('1AD8E', hh + 400)):
        op(t='settext', h=R(hd), s='%d' % v)
    # ---- spec: rows Х1, Ск1, 1, [2 side], Н3, concrete ----
    lb = (L + sup[0][1] / 2 + sup[-1][1] / 2 - 40) / 1000.0
    n_main = 2 * nb
    pm1 = round(n_main * lb + len(spl) * 0.0, 2)
    pm2 = round(2 * lb, 2) if h >= 600 else 0.0
    Lx = 2 * (hh + hw) + 200
    nx = nh * (2 if nb == 4 else 1)
    u = lambda Lmm, dd_: round(Lmm / 1000.0 * KG[dd_], 2)
    m_x = nx * u(Lx, 8); m_ck = 4 * u(hh + 400, 16); m1 = round(pm1 * KG[D], 2); m2 = round(pm2 * KG[12], 2)
    nspl = len(spl) * nb; m_n = nspl * 2 * 0.96
    if h >= 600:
        op(t='trows', h=R('1AD99'), mode='ins', at=4, **{'from': 3}, n=1)
    rs = 4 if h >= 600 else None
    cells = [[0, 2, nm_full], [0, 12, '%.2f' % (m_x + m_ck + m1 + m2 + m_n)],
             [1, 9, '%d' % Lx], [1, 10, '%d' % nx], [1, 11, '%.2f' % u(Lx, 8)], [1, 12, '%.2f' % m_x],
             [2, 9, '%d' % (hh + 400)], [2, 10, '4'], [2, 11, '%.2f' % u(hh + 400, 16)], [2, 12, '%.2f' % m_ck],
             [3, 3, '%d' % D], [3, 10, '%.2f' % pm1], [3, 11, '%.2f' % KG[D]], [3, 12, '%.2f' % m1]]
    rn = 4
    if rs:
        cells += [[4, 0, '2'], [4, 1, 'ГОСТ 34028-2016'], [4, 2, '%%C'], [4, 3, '12'], [4, 4, 'A'], [4, 5, '500С'], [4, 8, 'L='], [4, 9, 'пог.м.'], [4, 10, '%.2f' % pm2], [4, 11, '%.2f' % KG[12]], [4, 12, '%.2f' % m2]]; rn = 5
    cells += [[rn, 0, 'Н3'], [rn, 3, '%d' % D], [rn, 9, '250'], [rn, 10, '%d' % (2 * nspl)], [rn, 11, '0.96'], [rn, 12, '%.2f' % m_n],
              [rn + 2, 2, '\\A1;Класс бетона %s, м³' % conc], [rn + 2, 12, '%.2f' % (b * (h - r.get('slab', 0)) * L / 1e9)]]
    op(t='tset', h=R('1AD99'), cells=cells)
    a500 = m_ck + m1 + m2 + m_n
    op(t='tset', h=R('1AD9B'), cells=[[6, 0, nm_full], [5, 7, '%%%%C%d' % D], [6, 1, '%.2f' % m_x], [6, 2, '0.00'], [6, 3, '%.2f' % m_x],
                                    [6, 4, '%.2f' % m2], [6, 5, '0.00'], [6, 6, '%.2f' % m_ck], [6, 7, '%.2f' % (m1 + m_n)],
                                    [6, 8, '%.2f' % a500], [6, 9, '%.2f' % (m_x + a500)]])
    op(t='mcrep', win=A(0, 0) + A(W, H), pairs=[['Ф20', 'Ф%d' % D], ['Н5', 'Н3']])
    op(t='erase', h=list(PR.values()))
    return dict(total=m_x + a500)


# supports: (x along the ригель, width, kind) ; axes: (name, x)
def _sup(xs, kinds):
    return [(x, 500 if k == 'col' else (350 if k == 'beam' else 400), k) for x, k in zip(xs, kinds)]

RIGS = [
    dict(mk='Рм-1', b=350, h=700, slab=200, ztop=3500, cnt=2, conc='C 30/37 (B40)',
         sup=_sup([6800, 13350, 19350, 25350, 31350, 37800], ['wall', 'col', 'col', 'col', 'col', 'wall']),
         axes=[('2', 6800), ('3', 13350), ('4', 19350), ('5', 25350), ('6', 31350), ('7', 37800)]),
    dict(mk='Рм-2', b=350, h=700, slab=200, ztop=3500, cnt=3, conc='C 30/37 (B40)',
         sup=_sup([0, 6200, 12350, 18500, 24700], ['wall', 'col', 'wall', 'col', 'wall']),
         axes=[('А', 0), ('Б', 6200), ('В', 12350), ('Г', 18500), ('Д', 24700)]),
    dict(mk='Рм-3', b=300, h=650, slab=200, ztop=3500, cnt=6, conc='C 30/37 (B40)',
         sup=_sup([0, 6200, 12350, 18500, 24700], ['wall', 'beam', 'wall', 'beam', 'wall']),
         axes=[('А', 0), ('Б', 6200), ('В', 12350), ('Г', 18500), ('Д', 24700)]),
    dict(mk='Рм-3.1', b=300, h=650, slab=200, ztop=3500, cnt=1, conc='C 30/37 (B40)',
         sup=_sup([0, 4600, 10950, 13750, 20100, 24700], ['wall'] * 6),
         axes=[('А', 0), ('Д', 24700)]),
    dict(mk='Рм-4', b=300, h=650, slab=200, ztop=3500, cnt=2, conc='C 30/37 (B40)',
         sup=_sup([0, 6200, 10500], ['wall', 'beam', 'wall']), axes=[('А', 0), ('Б', 6200)]),
    dict(mk='Рм-5', b=300, h=650, slab=200, ztop=3500, cnt=2, conc='C 30/37 (B40)',
         sup=_sup([0, 4600], ['wall', 'wall']), axes=[('А', 0)]),
    dict(mk='Рм-6', b=350, h=500, slab=150, ztop=4950, cnt=5, conc='C 25/30 (B30)',
         sup=_sup([0, 6800], ['col', 'col']), axes=[('1', 0), ('2', 6800)]),
    dict(mk='Рм-7', b=350, h=500, slab=150, ztop=4950, cnt=1, conc='C 25/30 (B30)',
         sup=_sup([0, 5890], ['col', 'col']), axes=[('А', 0)]),
    dict(mk='Рм-8', b=350, h=500, slab=150, ztop=4950, cnt=1, conc='C 25/30 (B30)',
         sup=_sup([13810, 19170, 24700], ['col', 'col', 'col']), axes=[('Г', 18500), ('Д', 24700)]),
    dict(mk='Рм-9', b=350, h=500, slab=150, ztop=4950, cnt=1, conc='C 25/30 (B30)',
         sup=_sup([0, 5890, 13810, 19170, 24700], ['col'] * 5), axes=[('А', 0), ('Б', 6200), ('В', 12350), ('Г', 18500), ('Д', 24700)]),
    dict(mk='Рб-1', b=300, h=600, slab=0, ztop=-600, cnt=5, conc='C 25/30 (B30)',
         sup=_sup([0, 6800], ['col', 'wall']), axes=[('1', 0), ('2', 6800)]),
    dict(mk='Рб-2', b=300, h=600, slab=0, ztop=-600, cnt=1, conc='C 25/30 (B30)',
         sup=_sup([0, 5890], ['col', 'col']), axes=[('А', 0)]),
    dict(mk='Рб-3', b=300, h=600, slab=0, ztop=-600, cnt=1, conc='C 25/30 (B30)',
         sup=_sup([13810, 19170, 24700], ['col', 'col', 'col']), axes=[('Г', 18500), ('Д', 24700)]),
]
