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
    # ---- erase the copied template elevation; it is rebuilt from clones of the template's own objects ----
    keep = {'1ADC8'}
    op(t='eraseregion', win=A(1500, 13900) + A(17000, 19350), mode='inside', keep=[R(k) for k in keep])
    R0 = R
    def C(hh, bx, by, tx, ty):
        tg = lib.tag('c'); op(t='clone', h=hh, base=[TX + bx, TY + by], to=A(tx, ty), tag=tg); return tg
    # ---- geometry along the ригель ----
    L = sup[-1][0] - sup[0][0]
    x_end0 = sup[0][0] - sup[0][1] / 2.0; x_end1 = sup[-1][0] + sup[-1][1] / 2.0
    X_LEFT = 3845.0
    brk = None
    if x_end1 - sup[0][0] + 1400 > 28400 - X_LEFT:
        xa = sup[2][0] - sup[2][1] / 2 - 900; xb = sup[-2][0] + sup[-2][1] / 2 + 900
        brk = (xa, xb, 1200.0)
    def fx(x):
        x = x - sup[0][0]
        if brk:
            xa, xb, g = brk[0] - sup[0][0], brk[1] - sup[0][0], brk[2]
            if x > xa: x = xa + g + (x - xb) if x >= xb else xa + g / 2
        return X_LEFT + x
    vis = lambda x: not brk or x <= brk[0] or x >= brk[1]
    yb, yt0 = 17802.0, 18302.0            # template beam (h 500); stretched to h at the end
    # supports (template column stub + SPDS breaks)
    for xs, w, kind in sup:
        if not vis(xs): continue
        X = fx(xs)
        if kind == 'beam':
            t_ = C('1ADBB', 4045, 0, fx(xs - w / 2), 0)
            op(t='plset', h=t_, p=[A(X - w / 2, yt0), A(X + w / 2, yt0), A(X + w / 2, yb), A(X - w / 2, yb)], closed=True, ltype='HIDDEN2', ltscale=15)
            continue
        t_ = C('1ADAF', 3845, 0, X, 0)
        if w != 400: op(t='plset', h=t_, p=[A(X - w / 2, 18652), A(X + w / 2, 18652), A(X + w / 2, 17452), A(X - w / 2, 17452)], closed=True)
        for hb_, yy in (('1ADB0', 17452), ('1ADB1', 18652)):
            tb_ = C(hb_, 3845, 0, X, 0)
    # beam between support faces (template span polyline)
    for i in range(len(sup) - 1):
        a_ = sup[i][0] + sup[i][1] / 2; c_ = sup[i + 1][0] - sup[i + 1][1] / 2
        segs = [(a_, c_)]
        if brk:
            if a_ < brk[0] < c_: segs = [(a_, brk[0])] + ([(brk[1], c_)] if brk[1] < c_ else [])
            elif brk[0] <= a_ and c_ <= brk[1]: segs = []
            elif a_ < brk[1] < c_: segs = [(brk[1], c_)]
        for s0, s1 in segs:
            t_ = C('1ADBB', 4045, 0, fx(s0), 0)
            op(t='plset', h=t_, p=[A(fx(s0), yt0), A(fx(s1), yt0), A(fx(s1), yb), A(fx(s0), yb)], closed=True)
    if brk:
        for gx in (fx(brk[0]), fx(brk[1])):
            t_ = C('1ADB0', 3845, 17452, gx, (yb + yt0) / 2)
            op(t='xform', h=t_, base=A(gx, (yb + yt0) / 2), to=A(gx, (yb + yt0) / 2), ang=math.pi / 2, s=1.75)
    # bars (template lines), Ск1 hooks at the ends
    xs0, xs1 = x_end0 + 20, x_end1 - 20
    def bar(hh, y):
        pts_ = [(xs0, xs1)] if not brk else [(xs0, brk[0]), (brk[1], xs1)]
        for p0, p1 in pts_: op(t='lineset', h=hh, s=A(fx(p0), y), e=A(fx(p1), y))
    bar('1ADBE', 18272); bar('1ADBF', 17852)
    C('1ADC0', 3665, 0, fx(xs0), 0); C('1ADC1', 15525, 0, fx(xs1), 0)
    # ---- stirrups: template lines + ticks at zone limits; chain row as in the template ----
    ych = 16399.0
    pts = [(sup[0][0], None)]; nh = 0
    for i in range(len(sup) - 1):
        a_ = sup[i][0] + sup[i][1] / 2; c_ = sup[i + 1][0] - sup[i + 1][1] / 2
        try:
            if c_ - a_ < 2000: raise ValueError
            pos, zones, steps = colgeo.storey_hoops(a_, c_)
            n1, nm, n3 = zones
            mid = steps[n1:n1 + nm]; k200 = sum(1 for s_ in mid if abs(s_ - 200) < 1e-6); rr = [s_ for s_ in mid if abs(s_ - 200) > 1e-6]
            seg = [(pos[0], None), (pos[n1], '100х%d' % n1), (pos[n1 + nm], ('200х%d=%d' % (k200, 200 * k200)) + ('+%d' % rr[0] if rr else '')), (pos[-1], '100х%d' % n3)]
        except Exception:
            n_ = int((c_ - a_ - 100) // 100); pos = [a_ + 50 + 100 * j for j in range(n_ + 1)]
            seg = [(pos[0], None), (pos[-1], '100х%d' % n_)]
        nh += len(pos)
        for z, _ in seg:
            if vis(z):
                op(t='lineset', h='1ADDA', s=A(fx(z), 17817), e=A(fx(z), 18287)); C('1ADE4', 4095, 18045, fx(z), 18045)
        pts += seg + [(sup[i + 1][0], None)]
    for i in range(len(pts) - 1):
        p0, p1, tt = pts[i][0], pts[i + 1][0], pts[i + 1][1]
        if p1 - p0 < 1 or not (vis(p0) and vis(p1)): continue
        d_ = dict(t='dim', h='1ADEF', p1=A(fx(p0), yb), p2=A(fx(p1), yb), dl=A(fx(p0), ych), rot=0.0, txt=tt or '', layer='Размеры')
        if p1 - p0 < 450:
            axs = [s_[0] for s_ in sup]
            if any(abs(p1 - q) < 1 for q in axs): xt_ = fx(p0) - 260          # piece left of a support axis: text further left
            elif any(abs(p0 - q) < 1 for q in axs): xt_ = fx(p1) + 260        # right of the axis: further right
            else: xt_ = (fx(p0) + fx(p1)) / 2
            d_['tx'] = A(xt_, 16149)
        op(**d_)
    # ---- axes, axis chain, overall ----
    ax_x = [x for _, x in axes]
    for nm_, xa_ in axes:
        if not vis(xa_): continue
        t_ = C('1AD9F', 3845, 0, fx(xa_), 0)
        op(t='axis', h=t_, s=A(fx(xa_), 18992), e=A(fx(xa_), 14955), val=nm_)
    hid = []
    for i in range(len(ax_x) - 1 if len(ax_x) > 2 else 0):
        if vis(ax_x[i]) and vis(ax_x[i + 1]) and not (brk and ax_x[i] < brk[0] < ax_x[i + 1]):
            op(t='dim', h='1ADA5', p1=A(fx(ax_x[i]), 14955), p2=A(fx(ax_x[i + 1]), 14955), dl=A(fx(ax_x[i]), 15555), rot=0.0, txt='', layer='Размеры')
        else: hid.append(i)
    if hid:
        a_, b_ = ax_x[hid[0]], ax_x[hid[-1] + 1]
        op(t='dim', h='1ADA5', p1=A(fx(a_), 14955), p2=A(fx(b_), 14955), dl=A(fx(a_), 15555), rot=0.0, txt='%d' % (b_ - a_), layer='Размеры')
    if len(ax_x) > 1:
        op(t='dim', h='1ADA1', p1=A(fx(ax_x[0]), 14955), p2=A(fx(ax_x[-1]), 14955), dl=A(fx(ax_x[0]), 15205), rot=0.0,
           txt=('%d' % (ax_x[-1] - ax_x[0])) if brk else '', layer='Размеры')
    # ---- template callouts: bar note per span, Ск1 at the ends, Х1 at the right end, section mark ----
    for i in range(len(sup) - 1):
        xn = sup[i][0] + (sup[i + 1][0] - sup[i][0]) * 0.6
        if vis(xn): C('1ADD1', 6349, 0, fx(xn), 0)
    C('1ADCF', 3665, 0, fx(xs0), 0); C('1ADD0', 15525, 0, fx(xs1), 0); C('1B255', 15545, 0, fx(x_end1), 0)
    C('1ADD3', 5600, 0, fx(sup[0][0] + (sup[1][0] - sup[0][0]) * 0.25), 0)
    for hd in ('1ADCC', '1ADCD', '1ADCE'): C(hd, 3645, 0, fx(x_end0), 0)
    # ---- splices (template groups): bottom 750 before a support axis, top 2250 after it ----
    spl = []
    if xs1 - xs0 > 11700:
        n = int((xs1 - xs0) // 11000)
        inner = [s_[0] for s_ in sup[1:-1]]
        for k in range(1, n + 1):
            xt = xs0 + k * (xs1 - xs0) / (n + 1)
            spl.append(min(inner, key=lambda q: abs(q - xt)) if inner else xt)
    for ax_ in spl:
        if vis(ax_ - 750):
            for hh in ('1AE06', '1AE07', '1AE08', '1AE09', '1AE0A'): C(hh, 8695, 0, fx(ax_), 0)
        if vis(ax_ + 2250):
            for hh in ('1AE0B', '1AE0C', '1AE0D', '1AE10', '1AE13', '1AE14'): C(hh, 10495, 0, fx(ax_), 0)
    # ---- height: stretch everything above mid-beam by (h - 500) ----
    if h != 500:
        op(t='stretchwin', win=A(1500, 18050) + A(28950, 19400), d=[0, h - 500])
    yt = yb + h
    lib.lev(Y0 + yt - lev_top, A(fx(x_end0) + 400, yt), 50)
    # ---- section 1-1: the template section (scale 5) stretched to b x h and slab ----
    ts = r.get('slab', 0)
    k5 = 5.0; cx = 8200.0
    dwh = k5 * (b - 300) / 2.0
    if dwh:
        op(t='stretchwin', win=A(cx + 5, 7000) + A(11200, 12300), d=[dwh, 0])
        op(t='stretchwin', win=A(4800, 7000) + A(cx - 5, 12300), d=[-dwh, 0])
    d_slab = k5 * (200 - ts) if ts else 0.0
    if d_slab: op(t='stretchwin', win=A(4800, 7000) + A(11200, 10750), d=[0, d_slab])
    d_bot = -k5 * (h - 500) - d_slab
    op(t='stretchwin', win=A(4800, 7000) + A(11200, 9650 + d_slab), d=[0, d_bot])
    ybar0 = 9486 + d_slab + d_bot; ybar1 = 11486.0
    if not ts:
        op(t='erase', h=[R('1AD34'), R('1AD36'), R('1AD37'), R('1AD3B'), R('1AD38')])
        op(t='plset', h=R('1AD35'), p=[A(cx - k5 * b / 2, 11686), A(cx - k5 * b / 2, 11686 - k5 * h), A(cx + k5 * b / 2, 11686 - k5 * h), A(cx + k5 * b / 2, 11686)], closed=True)
    nb = 4 if b > 300 else 3
    xb0, xb1 = 7700.0 - dwh, 8700.0 + dwh
    xs4 = [xb0 + (xb1 - xb0) * k / (nb - 1) for k in range(nb)]
    if nb == 4:
        op(t='movegrp', h=[R('1AD48')], d=[xs4[1] - cx, 0]); op(t='movegrp', h=[R('1AD4D')], d=[xs4[1] - cx, 0])
        C('1AD43', 7700, 9486, xs4[2], ybar0); C('1AD4B', 7700, 11486, xs4[2], ybar1)
        op(t='dimpts', h=R('1AD46'), p1=A(xs4[0], ybar0), p2=A(xs4[1], ybar0))
        op(t='dimpts', h=R('1AD49'), p1=A(xs4[2], ybar0), p2=A(xs4[3], ybar0))
        op(t='dim', h='1AD46', p1=A(xs4[1], ybar0), p2=A(xs4[2], ybar0), dl=A(xs4[1], 8386 + d_slab + d_bot), rot=0.0, txt='',
           tx=A((xs4[1] + xs4[2]) / 2 + 125, 8386 + d_slab + d_bot), layer='0_ANNOT_Dimensions')
    # hoops: the template dynamic block; b>300 -> two hoops, each around 3 bars (04_Ригели)
    spans = [(0, 2), (1, 3)] if nb == 4 else [(0, 2)]
    op(t='erase', h=[R('1AD51')])
    for i0, i1 in spans:
        t_ = C('1AD51', 7700, 9486, xs4[i0], ybar0)
        op(t='dyn', h=t_, prop='Расстояние1', value=xs4[i1] - xs4[i0])
        op(t='dyn', h=t_, prop='Расстояние2', value=ybar1 - ybar0)
    op(t='erase', h=[R('1AD9C'), R('1AD9D')])
    lib.lev(Y0 + 11686.0 - lev_top, A(6723 - dwh, 11686), 50)
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
    op(t='mcrep', win=A(0, 0) + A(W, H), pairs=[['Ф20', 'Ф%d' % D], ['%%C20', '∅%d' % D], ['∅20', '∅%d' % D], ['Н5', 'Н3']])
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
