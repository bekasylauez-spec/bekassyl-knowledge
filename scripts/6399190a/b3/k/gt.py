# -*- coding: utf-8 -*-
"""Маслоподготовка Блок 3 — column sheet from the user's template «Колонна Км-1» (Шаблон для Кж.dwg, A2 1:50, sections x2).
Based on Аэротенк col_tpl.py (facade, hoops by rule, spec) + ЖК Галакси gen_km.py (sections, pins, meshes),
generalised to b x h, nb x nh bars Ø28, hoops/pins Ø10 (X1 + Шп1/Шп2), one storey (column bottom -> ригель top)."""
import math, json
import lib
from lib import op
import colgeo

TX, TY = 264717.3, 271897.8
W, H = 29700, 21000
XL = 4102.7
TL0, TTOP = 9700.0, 19300.0
KG = {8: 0.395, 10: 0.617, 16: 1.578, 28: 4.834}
D = 28; DW = 10
E = 40 + D / 2.0                     # bar centre from the face
OB = r'D:\РАБОЧКА\От Маке\Завод\Обезвоживание\КЖ Помещение обезвоживания.dwg'


def lvs(v):
    if abs(v) < 0.5: return '±0,000'
    return ('+' if v > 0 else '-') + '%d,%03d' % (abs(v) // 1000, abs(v) % 1000)


def build(X0, Y0, T, num):
    mk = T['mark']; b, h = float(T['b']), float(T['h']); nb, nh = T['nb'], T['nh']
    base = T['base']; Ltop = T['top']; hb = float(T['hb'])
    P = 'C%s:' % mk.split('-')[1]
    R = lambda hh: P + hh
    A = lambda x, y: [X0 + x, Y0 + y]
    op(t='copywin', win=[TX - 1, TY - 1, TX + W + 1, TY + H + 1], d=[X0 - TX, Y0 - TY], pre=P)
    dw = b - 400.0
    Hc = float(Ltop)                      # column bottom -> ригель top (rel)
    LT = TL0 + Hc; Lb = LT - hb; dY = LT - TTOP
    XR = XL + b; XM = XL + b / 2.0
    XC0, XC1 = XL + E, XR - E
    MIDS = [XL + E + i * (b - 2 * E) / (nb - 1) for i in range(1, nb - 1)]
    # ---------- erase template middle storey ----------
    mid = ['18C37', '18C3A', '18C3F', '18C3C', '18C4D', '18C4E', '18C49',
           '18C54', '18C55', '18C69', '18C6A', '18C6B', '18C6C', '18C6D', '18C6E', '18C6F', '18C70',
           '18C56', '18C57', '18C58', '18C5B', '18C5C', '18C5F', '18C60', '18C61', '18C62', '18C65', '18C68', '18C72', '18C75', '18C78',
           '18C71', '18C7B', '18C7C', '18C83', '18C7D', '18C7E', '18C80', '18C81', '18C82', '18E59', '18E5A', '18E54', '18E5C']
    op(t='erase', h=[R(x) for x in mid])
    # ---------- width of the facade ----------
    if dw:
        op(t='stretchwin', win=A(XM - dw / 2 - 10, 9000) + A(7000, 21000), d=[dw, 0])
        op(t='movegrp', h=[R('18C48'), R('18C46'), R('18E58')], d=[dw / 2, 0])
    # ---------- top group to the ригель top ----------
    op(t='movegrp', h=[R(x) for x in ('18C4F', '18C50', '18E55', '18E56', '18E53', '18C35', '18C39')], d=[0, dY])
    xa, xb = 3691.7, 4971.7 + dw
    for hh, x in (('18C50', xa), ('18C4F', xb)):
        op(t='spmove', h=R(hh), items=[[0, X0 + x, Y0 + LT], [1, X0 + x, Y0 + (LT + Lb) / 2], [2, X0 + x, Y0 + Lb], [3, X0 + x, Y0 + Lb]])
    # ---------- concrete: column, ригель stubs, support ----------
    lib.pl([A(XL, TL0), A(XL, Lb), A(xa, Lb)], layer='Размеры')
    lib.pl([A(XR, TL0), A(XR, Lb), A(xb, Lb)], layer='Размеры')
    lib.pl([A(xa, LT), A(xb, LT)], layer='Размеры')
    lib.pl([A(xa, TL0), A(xb, TL0), A(xb, TL0 - 400), A(xa, TL0 - 400)], layer='Размеры')
    op(t='erase', h=[R('18C4A'), R('18C3C')])
    lib.hatch([[A(xa, TL0 - 400), A(xb, TL0 - 400), A(xb, TL0), A(xa, TL0)]], pat='ANSI36', sc=20, layer='.', lw=None)
    # ---------- bars: corners from +600, mids from +1200 (накладки С21-Рн) ----------
    lay = 'диам%d' % D
    op(t='plset', h=R('18C51'), p=[A(XC0, TL0 + 600), A(XC0, LT - 20)], layer=lay)
    op(t='plset', h=R('18C53'), p=[A(XC1, TL0 + 600), A(XC1, LT - 20)], layer=lay)
    op(t='plset', h=R('18C52'), p=[A(MIDS[0], TL0 + 1200), A(MIDS[0], LT - 20)], layer=lay)
    for x in MIDS[1:]: lib.pl([A(x, TL0 + 1200), A(x, LT - 20)], layer=lay, lw=40)
    op(t='movegrp', h=[R('18C43'), R('18C44')], d=[XC0 - 4142.7, 0])
    op(t='movegrp', h=[R('18C47'), R('18C45')], d=[XC1 - (4462.7 + dw), 0])
    op(t='movegrp', h=[R('18C46'), R('18C48')], d=[MIDS[0] - XM, 0])
    for i, x in enumerate(MIDS[1:]):
        for hh in ('18C46', '18C48'):
            op(t='clone', h=R(hh), base=A(MIDS[0], 0), to=A(x, 0), tag=R('M%d_%s' % (i, hh)))
    op(t='plset', h=R('18E55'), p=[A(XC0 - 2, LT - 20 - 400), A(XC0 - 2, LT - 45), A(XC0 + 23, LT - 20), A(XC1 - 23, LT - 20), A(XC1 + 2, LT - 45), A(XC1 + 2, LT - 20 - 400)], layer='диам16')
    # ---------- hoops Ø10 (rule 100|200|100, or step 100 by Asw) ----------
    lo, hi = TL0, Lb
    S_ = hi - lo - 100
    if T['hoop'] == '100' or hi - lo < 2000:
        n_ = int(round(S_ / 100)); pos = [50 + 100 * j for j in range(n_ + 1)]; steps = [100.0] * n_; zones = (n_, 0, 0)
    else:
        pos, zones, steps = colgeo.storey_hoops(0.0, hi - lo)
    n1, nm, n3 = zones
    for z in sorted({pos[0], pos[n1], pos[n1 + nm], pos[-1]}): lib.pl([A(XC0, lo + z), A(XC1, lo + z)], layer='диам10')
    if nm:
        ms = steps[n1:n1 + nm]; k200 = sum(1 for s in ms if abs(s - 200) < 1e-6); rr = [s for s in ms if abs(s - 200) > 1e-6]
        seg = [(pos[0], '50'), (pos[n1], '100х%d' % n1), (pos[n1 + nm], ('200х%d' % k200) + (('+%d' % rr[0]) if rr else '')), (pos[-1], '100х%d' % n3)]
    else:
        seg = [(pos[0], '50'), (pos[-1], '100х%d' % (len(pos) - 1))]
    chp = [lo] + [lo + zz for zz, _ in seg] + [hi, LT]; cht = [t_ for _, t_ in seg] + ['50', '%d' % hb]
    for i in range(len(chp) - 1):
        o = dict(t='dim', h=R('18C3B'), p1=A(XR, chp[i]), p2=A(XR, chp[i + 1]), dl=A(5848 + dw, chp[i]), rot=math.pi / 2, txt=cht[i], layer='Размеры')
        if chp[i + 1] - chp[i] < 300: o['tx'] = A(5848 + dw + 360, (chp[i] + chp[i + 1]) / 2)
        op(**o)
    zmid = lo + (pos[n1] + pos[n1 + nm]) / 2 if nm else lo + (pos[0] + pos[-1]) / 2
    # left dims
    op(t='dimpts', h=R('18C3B'), p1=A(3149, LT), p2=A(3149, TL0), dl=A(2452, TL0))
    op(t='dimpts', h=R('18C3D'), p1=A(3149, Lb), p2=A(3149, TL0), dl=A(2917, TL0))
    op(t='dimpts', h=R('18C3E'), p1=A(3149, LT), p2=A(3149, Lb), dl=A(2917, Lb))
    op(t='dimpts', h=R('18C40'), p1=A(3286, TL0), p2=A(XC0, TL0 + 600))
    op(t='dimpts', h=R('18C41'), p1=A(3286, TL0 + 600), p2=A(MIDS[0], TL0 + 1200))
    # ---------- level marks (template marks; 7-char values from the Обезвоживание mark) ----------
    marks = [('18C36', TL0, base), ('18C3A', Lb, base + Hc - hb), ('18C39', LT, base + Hc)]
    for hh, y, val in marks:
        txt = lvs(val)
        old = '-2.000' if hh == '18C36' else lvs(y - 11700)
        if hh == '18C3A':
            op(t='clone', h=R('18C39'), base=A(0, LT), to=A(0, y), tag=R('LVB'))
            hh = 'LVB'
        if len(txt) == 7:
            pre = R('L%s:' % hh)
            op(t='import', file=OB, h=['4EF372'], base=[-598253.005, -1731772.311], to=A(XL, y), pre=pre)
            op(t='levelval', h=pre + '4EF372', old='+13,700', value=txt)
            op(t='erase', h=[R(hh)])
        else:
            op(t='levelval', h=R(hh), old=old, value=txt)
    # ---------- callouts on the facade ----------
    DIA = '(%%%%C%d)' % D
    H1 = Lb - TL0
    for l1_, yy_, xt_ in (('1', TL0 + min(2400, H1 * 0.35), XC0), ('2', TL0 + H1 * 0.62, MIDS[0])):
        op(t='note', l1=l1_, l2=DIA, origin=A(XL - 355, yy_), targets=[A(xt_, yy_)], angle=math.pi, scale=50, ts=2.5, style='ГОСТ 2.304',
           layer='Размеры', arrow='oblique', fixed=True)
    op(t='note', l1='Х1;Шп1;Шп2', l2='', origin=A(XR + 250, zmid + 600), target=A(XC1, zmid + 300), scale=50, ts=2.5, arrow='oblique', layer='Размеры', align='Center', fixed=True)
    op(t='movegrp', h=[R('18E5B')], d=[0, zmid - 13418.0])
    if dw > 300: op(t='sp_set', h=R('18E53'), pts=[[1, X0 + XR + 900, Y0 + LT + 235]])
    op(t='mcset', h=R('18E52'), set={'Center': A(XM, (Lb + LT) / 2), 'Rack': A(XM - 900 - dw / 2, Lb - 700)})
    op(t='mcset', h=R('1988A'), set={'Center': A(XC1, TL0 + 600), 'Rack': A(XC1 + 345, TL0 + 600 - 369), 'Knot': 'А'})
    # ---------- sections 1-1 / 2-2 (x2) ----------
    K = 2.0
    oy = 18388.0 - K * h
    ox1 = max(7900.0, min(9314.0, 16500.0 - 1300 - 3400 - 4 * b))
    ox2 = max(13824.0 if b <= 500 else 0.0, ox1 + K * b + 3400)
    def cpos(n_, L_): return [E + i * (L_ - 2 * E) / (n_ - 1) for i in range(n_)]
    fx, fy = cpos(nb, b), cpos(nh, h)
    per = sorted({(x, y) for x in fx for y in fy if x in (fx[0], fx[-1]) or y in (fy[0], fy[-1])})
    def section(ox, out, bars, bproto, dims, axes, title, tcx, tag):
        op(t='spmove', h=R(out), items=[[0, X0 + ox + K * b, Y0 + oy], [1, X0 + ox + K * b, Y0 + oy + K * h], [2, X0 + ox, Y0 + oy + K * h], [3, X0 + ox, Y0 + oy]])
        bx, by, bc = bproto
        for i, (x, y) in enumerate(per): op(t='clone', h=R(bc), base=A(bx, by), to=A(ox + K * x, oy + K * y), tag=R('%sB%d' % (tag, i)))
        op(t='erase', h=[R(x) for x in bars])
        (b40l, b1l, b1r, b40r, bhl, bhr), (l40b, l1b, l1t, l40t, lhb, lht) = dims
        xs = [0, 40, b / 2, b - 40, b]; ys = [0, 40, h / 2, h - 40, h]
        yb1, yb2 = oy - 518, oy - 1129; xl1, xl2 = ox - 518, ox - 911
        for hh, i in ((b40l, 0), (b1l, 1), (b1r, 2), (b40r, 3)):
            op(t='dimpts', h=R(hh), p1=A(ox + K * xs[i], oy), p2=A(ox + K * xs[i + 1], oy), dl=A(ox + K * (xs[i] + xs[i + 1]) / 2, yb1))
        op(t='dimpts', h=R(bhl), p1=A(ox, oy), p2=A(ox + K * b / 2, oy), dl=A(ox + K * b / 4, yb2))
        op(t='dimpts', h=R(bhr), p1=A(ox + K * b / 2, oy), p2=A(ox + K * b, oy), dl=A(ox + K * 3 * b / 4, yb2))
        for hh, i in ((l40b, 0), (l1b, 1), (l1t, 2), (l40t, 3)):
            op(t='dimpts', h=R(hh), p1=A(ox, oy + K * ys[i]), p2=A(ox, oy + K * ys[i + 1]), dl=A(xl1, oy + K * (ys[i] + ys[i + 1]) / 2))
        op(t='dimpts', h=R(lhb), p1=A(ox, oy), p2=A(ox, oy + K * h / 2), dl=A(xl2, oy + K * h / 4))
        op(t='dimpts', h=R(lht), p1=A(ox, oy + K * h / 2), p2=A(ox, oy + K * h), dl=A(xl2, oy + K * 3 * h / 4))
        op(t='dimtx', h=R(b40l), at=A(ox - 300, yb1)); op(t='dimtx', h=R(b40r), at=A(ox + K * b + 300, yb1))
        op(t='dimtx', h=R(l40b), at=A(xl1, oy - 300)); op(t='dimtx', h=R(l40t), at=A(xl1, oy + K * h + 300))
        for hh, yy in ((lhb, oy + K * h / 4), (lht, oy + K * 3 * h / 4)): op(t='dimtx', h=R(hh), at=A(xl2 - 73, yy))
        sx_, sy_ = (b - 2 * E) / (nb - 1), (h - 2 * E) / (nh - 1)
        op(t='dim', h=R(b1l), p1=A(ox + K * fx[0], oy + K * h), p2=A(ox + K * fx[-1], oy + K * h), dl=A(ox + K * b / 2, oy + K * h + 230), rot=0,
           txt='%dх%d=%d' % (round(sx_), nb - 1, round(sx_ * (nb - 1))))
        if tag == 's1' and abs(sy_ - sx_) > 2:
            op(t='dim', h=R(l1b), p1=A(ox, oy + K * fy[0]), p2=A(ox, oy + K * fy[-1]), dl=A(ox - 1300, oy + K * h / 2), rot=math.pi / 2,
               txt='%dх%d=%d' % (round(sy_), nh - 1, round(sy_ * (nh - 1))))
        av, ah = axes; cx, cy = ox + K * b / 2, oy + K * h / 2
        op(t='spmove', h=R(av), items=[[0, X0 + cx, Y0 + oy + K * h + 900], [1, X0 + cx, Y0 + oy - 1060]])
        op(t='spmove', h=R(ah), items=[[0, X0 + ox + K * b + 900, Y0 + cy], [1, X0 + ox - (1750 if (tag == 's1' and abs(sy_ - sx_) > 2) else 1090), Y0 + cy]])
        op(t='movegrp', h=[R(title)], d=[(ox + K * b / 2) - tcx, 0])
    section(ox1, '18CB9', ['18CBA', '18CC1', '18CC8', '18CCF', '18CD6', '18CDD', '18CE4', '18CEB'], (9422, 18267, '18CBA'),
            (('18CF2', '18D12', '18D13', '18CF3', '18CF6', '18CF7'), ('18CF5', '18D14', '18D15', '18CF4', '18CF9', '18CF8')),
            ('18CB5', '18CB8'), '18CB6', 9625.0, 's1')
    # hoop X1 (template dynamic block) and pins Шп1/Шп2 (template «Шпилька_динамическая2», 19EC6)
    op(t='movegrp', h=[R('18CFA')], d=[(ox1 + 112) - 9421, (oy + 112) - 17699])
    op(t='scalegrp', h=[R('18CFA')], s=776 / 584.0, base=A(ox1 + 112, oy + 112))
    op(t='dyn', h=R('18CFA'), prop='Расстояние1', value=K * b - 224)
    op(t='dyn', h=R('18CFA'), prop='Расстояние2', value=K * h - 224)
    op(t='erase', h=[R('18D05')])
    for k, y in enumerate(fy[1:-1]):
        tg = R('PH%d' % k); ins = A(ox1 + K * E, oy + K * y)
        op(t='clone', h='19EC6', base=[304063, 294024], to=ins, tag=tg)
        op(t='dyn', h=tg, prop='Расстояние1', value=K * (b - 2 * E) + 1)
    for k, x in enumerate(fx[1:-1]):
        tg = R('PV%d' % k); ins = A(ox1 + K * x, oy + K * E)
        op(t='clone', h='19EC6', base=[304063, 294024], to=ins, tag=tg)
        op(t='xform', h=tg, base=ins, to=ins, ang=math.pi / 2)
        op(t='dyn', h=tg, prop='Расстояние1', value=K * (h - 2 * E) + 1)
    op(t='erase', h=[R('18D10'), R('18D11')])
    top = sorted([(ox1 + K * x, oy + K * fy[-1]) for x in fx], reverse=True); bot = sorted([(ox1 + K * x, oy + K * fy[0]) for x in fx], reverse=True)
    NOTE = dict(scale=50, ts=2.5, style='ГОСТ 2.304', layer='Размеры')
    op(t='note', l1='1, 2', l2=DIA, origin=A(ox1 + K * b + 520, oy + K * h + 230), targets=[A(*p_) for p_ in top], arrow='none', fixed=True, **NOTE)
    op(t='note', l1='1, 2', l2=DIA, origin=A(ox1 + K * b + 520, oy - 230), targets=[A(*p_) for p_ in bot], arrow='none', fixed=True, **NOTE)
    t2 = A(ox1 + K * b * 0.75, oy + K * fy[1]) if nh > 2 else A(ox1 + K * b * 0.75, oy + K * h * 0.75)
    op(t='spmove', h=R('18D16'), items=[[0, X0 + ox1 + K * b + 520, Y0 + oy + K * h / 2 + 120], [1, X0 + ox1 + K * b - 64, Y0 + oy + K * h * 0.72], [2, t2[0], t2[1]]])
    op(t='mcset', h=R('18D16'), set={'FirstLine': 'Х1;Шп1;Шп2'})
    section(ox2, '18E08', ['18E1A', '18E21', '18E28', '18E2F', '18E36', '18E3D', '18E44', '18E4B'], (13932, 18320, '18E1A'),
            (('18E09', '18E11', '18E12', '18E0A', '18E0D', '18E0E'), ('18E0C', '18E13', '18E14', '18E0B', '18E10', '18E0F')),
            ('18E04', '18E07'), '18E05', 14224.0, 's2')
    Pp = lambda x, y: A(ox2 + K * x, oy + K * y)
    op(t='erase', h=[R('18E15'), R('18E16'), R('18E17'), R('18E18')])
    for y in fy: lib.pl([Pp(fx[0], y), Pp(fx[-1], y)], layer='диам16', lw=40)          # Ск1 along b
    for x in fx[1:-1]: lib.pl([Pp(x, fy[0]), Pp(x, fy[-1])], layer='диам16', lw=40)    # Ск2 along h
    op(t='spmove', h=R('18E19'), items=[[0, X0 + ox2 + K * b + 300, Y0 + oy - 120], [1, X0 + ox2 + K * fx[-1], Y0 + oy + K * fy[-1]],
                                       [2, X0 + ox2 + K * fx[-2], Y0 + oy + K * h * 0.3]])
    op(t='mcset', h=R('18E19'), set={'FirstLine': 'Ск1;Ск2'})
    # ---------- node «Узел расположения сетки С1» ----------
    nmesh = int(round((hb - 100) / 100)) + 1
    for hh, s_ in (('18D6E', '%d' % hb), ('18D8B', '50'), ('18D85', '100х%d' % (nmesh - 1)), ('18D88', '100'),
                   ('18D66', '%d' % (b / 2)), ('18D69', '%d' % (b / 2)), ('18D74', '%d' % b)):
        op(t='dimtext', h=R(hh), s=s_)
    # ---------- mesh С1 sketches (x2): rods Ø10 ш.100 ----------
    def rods(L_):
        return [35 + 100 * i for i in range(int((L_ - 40 - 35 - 100) // 100) + 1)]
    rx_, ry_ = rods(b), rods(h)
    LX, LY = K * (b - 40), K * (h - 40)
    x0, y0 = 13769.0, 11403.0
    rx = [x0 + K * v for v in rx_]
    for x in rx: op(t='lineset', h=R('18D26'), s=A(x, y0), e=A(x, y0 + LY))
    yc = y0 + LY - 70
    op(t='lineset', h=R('18D27'), s=A(x0, yc), e=A(x0 + LX, yc))
    op(t='erase', h=[R('18D26'), R('18D2B'), R('18D2C'), R('18D27')])
    op(t='dimpts', h=R('18D17'), p1=A(rx[0], y0), p2=A(x0, y0))
    op(t='dimpts', h=R('18D2D'), p1=A(rx[0], y0), p2=A(rx[-1], y0)); op(t='dimtext', h=R('18D2D'), s='100х%d' % (len(rx) - 1))
    op(t='dimtx', h=R('18D2D'), at=A((rx[0] + rx[-1]) / 2, 11150))
    op(t='dimpts', h=R('18D28'), p1=A(rx[-1], y0), p2=A(x0 + LX, yc))
    op(t='dimtx', h=R('18D28'), at=A(x0 + LX + 300, 11150))
    op(t='dimpts', h=R('18D1A'), p1=A(x0 + LX, yc), p2=A(x0, yc))
    op(t='dimpts', h=R('18D1D'), p1=A(x0 + LX, yc), p2=A(rx[-1], y0 + LY))
    op(t='dimpts', h=R('18D20'), p1=A(x0 + LX, yc), p2=A(rx[-1], y0))
    op(t='dimpts', h=R('18D23'), p1=A(rx[-1], y0 + LY), p2=A(rx[-1], y0))
    op(t='erase', h=[R('18D30')])
    lib.note('11', 'ш.100', A(12980, 11792), A(rx[0], 11792), 50, arrow='oblique')
    op(t='spmove', h=R('18D31'), items=[[1, X0 + 14144, Y0 + yc]]); op(t='mcset', h=R('18D31'), set={'FirstLine': '10'})
    xa2 = max(17797.0, x0 + LX + 1600); yb_ = 11121.0
    ry = [yb_ + K * v for v in ry_]
    for y in ry: op(t='lineset', h=R('18D43'), s=A(xa2, y), e=A(xa2 + LX, y))
    xr = xa2 + LX - 70
    op(t='lineset', h=R('18D44'), s=A(xr, yb_), e=A(xr, yb_ + LY))
    op(t='erase', h=[R('18D43'), R('18D48'), R('18D49'), R('18D44')])
    op(t='dimpts', h=R('18D34'), p1=A(xa2, ry[0]), p2=A(xa2, yb_))
    op(t='dimpts', h=R('18D4A'), p1=A(xa2, ry[0]), p2=A(xa2, ry[-1])); op(t='dimtext', h=R('18D4A'), s='100х%d' % (len(ry) - 1))
    op(t='dimtx', h=R('18D4A'), at=A(xa2 - 377, (ry[0] + ry[-1]) / 2))
    op(t='dimpts', h=R('18D45'), p1=A(xa2, ry[-1]), p2=A(xr, yb_ + LY))
    op(t='dimtx', h=R('18D45'), at=A(xa2 - 377, yb_ + LY + 300))
    op(t='dimpts', h=R('18D37'), p1=A(xr, yb_), p2=A(xr, yb_ + LY))
    op(t='dimpts', h=R('18D3A'), p1=A(xr, yb_ + LY), p2=A(xa2 + LX, ry[-1]))
    op(t='dimpts', h=R('18D3D'), p1=A(xr, yb_ + LY), p2=A(xa2, ry[-1]))
    op(t='dimpts', h=R('18D40'), p1=A(xa2 + LX, ry[-1]), p2=A(xa2, ry[-1]))
    op(t='erase', h=[R('18D4D')])
    lib.note('10', 'ш.100', A(xa2 + 389, 10698), A(xa2 + 389, ry[0]), 50, arrow='oblique')
    op(t='spmove', h=R('18D4E'), items=[[1, X0 + xr, Y0 + 11686]]); op(t='mcset', h=R('18D4E'), set={'FirstLine': '11'})
    op(t='spmove', h=R('18D4F'), items=[[1, X0 + xr, Y0 + ry[0]]])
    # ---------- ведомость деталей ----------
    sxh, syh = b - 80, h - 80
    X1L = int(2 * (sxh + syh) + 200)
    PL1, PL2 = int(b - 2 * E + 200), int(h - 2 * E + 200)
    SK1, SK2 = int(round(b - 2 * E)), int(round(h - 2 * E))
    LEG = 280
    vals = {'18DD6': '%d' % (sxh + 100), '18DCD': '%d' % sxh, '18DCE': '%d' % syh, '18DD0': '%d' % (syh + 100), '18DDC': '%d' % X1L,
            '18D9F': LEG, '18D9E': SK1, '18DA2': LEG, '18DA7': '%d' % (2 * LEG + SK1),
            '18DB5': LEG, '18DB4': SK2, '18DB8': LEG, '18DBD': '%d' % (2 * LEG + SK2),
            '18DF1': ('%d' % PL1) if PL1 == PL2 else '%d; %d' % (PL1, PL2), '18DE9': '', '18DEB': '', '18DE8': '',
            '18DF7': ('%d' % PL1) if PL1 == PL2 else '%d; %d' % (PL1, PL2), '18DCC': 'Шп1;\\PШп2'}
    for hh, v in vals.items(): op(t='settext', h=R(hh), s='%s' % v)
    op(t='erase', h=[R('18E00')])
    pin = A(17973, 18250)
    op(t='clone', h='19EC6', base=[304063, 294024], to=pin, tag=R('PSK'))
    op(t='dyn', h=R('PSK'), prop='Расстояние1', value=700)
    # ---------- specification (input cells) + ведомость расхода стали ----------
    nh_ = len(pos)
    L1, L2 = int(Hc - 20 - 600), int(Hc - 20 - 1200)
    nbar = 2 * nb + 2 * nh - 4
    npin1, npin2 = nh - 2, nb - 2
    nC1 = nmesh
    m = lambda L, d: round(L / 1000.0 * KG[d], 2)
    rows = [(1, 'Х1', DW, X1L, nh_), (2, 'Шп1', DW, PL1, nh_ * npin1), (3, 'Шп2', DW, PL2, nh_ * npin2),
            (4, 'Ск1', 16, 2 * LEG + SK1, nh), (5, 'Ск2', 16, 2 * LEG + SK2, nb - 2),
            (6, '1', D, L1, 4), (7, '2', D, L2, nbar - 4)]
    cells = [[0, 2, 'Колонна %s' % mk]]
    for r, name, d, L, q in rows:
        cells += [[r, 0, name], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 3, '%d' % d], [r, 4, 'A'], [r, 5, '500С'], [r, 8, 'L='],
                  [r, 9, '%d' % L], [r, 10, '%d' % q], [r, 11, '%.2f' % m(L, d)], [r, 12, '%.2f' % (q * m(L, d))]]
    cells += [[8, 0, ''], [8, 1, ''], [8, 2, ''], [8, 3, ''], [8, 4, ''], [8, 5, ''], [8, 8, ''], [8, 9, ''], [8, 10, ''], [8, 11, ''], [8, 12, '']]
    NK = 2 * nbar
    mesh1 = KG[10] * ((b - 40) * (len(ry_) + 1) + (h - 40) * (len(rx_) + 1)) / 1000.0
    cells += [[9, 0, 'Н2'], [9, 3, '%d' % D], [9, 9, '280'], [9, 10, '%d' % NK], [9, 11, '1.35'], [9, 12, '%.2f' % (NK * 1.35)],
              [10, 10, '%d' % nC1], [10, 11, '%.2f' % mesh1], [10, 12, '%.2f' % (nC1 * mesh1)],
              [12, 12, '%.2f' % (b * h * Hc / 1e9)], [12, 2, '\\A1;Класс бетона C20/25 (B25), м³'],
              [14, 0, '10'], [14, 3, '10'], [14, 9, '%d' % (b - 40)], [14, 10, '%d' % (len(ry_) + 1)],
              [14, 11, '%.2f' % m(b - 40, 10)], [14, 12, '%.2f' % ((len(ry_) + 1) * m(b - 40, 10))]]
    op(t='tset', h=R('18D93'), cells=cells)
    op(t='trows', h=R('18D93'), mode='ins', at=15, n=1, **{'from': 14})
    op(t='tset', h=R('18D93'), cells=[[15, 0, '11'], [15, 1, 'ГОСТ 34028-2016'], [15, 2, '%%C'], [15, 3, '10'], [15, 4, 'A'], [15, 5, '500С'], [15, 8, 'L='],
                                     [15, 9, '%d' % (h - 40)], [15, 10, '%d' % (len(rx_) + 1)], [15, 11, '%.2f' % m(h - 40, 10)],
                                     [15, 12, '%.2f' % ((len(rx_) + 1) * m(h - 40, 10))]])
    m10 = sum(q * m(L, d) for r, nme, d, L, q in rows if d == 10) + nC1 * mesh1
    m16 = sum(q * m(L, d) for r, nme, d, L, q in rows if d == 16)
    m28 = sum(q * m(L, d) for r, nme, d, L, q in rows if d == 28) + NK * 1.35
    tot = m10 + m16 + m28
    cells[0:0] = []
    op(t='tset', h=R('18D93'), cells=[[0, 12, '%.2f' % tot]])
    op(t='tset', h=R('18DCA'), cells=[[6, 0, 'Колонна %s' % mk], [5, 4, '%%C10'], [5, 5, '%%C16'], [5, 6, '%%C28'],
                                     [6, 1, '0.00'], [6, 2, '0.00'], [6, 3, '0.00'], [6, 4, '%.2f' % m10], [6, 5, '%.2f' % m16],
                                     [6, 6, '%.2f' % m28], [6, 7, '%.2f' % tot], [6, 8, '%.2f' % tot]])
    # ---------- texts ----------
    win = A(0, 0) + A(W, H)
    op(t='mcrep', win=win, pairs=[['Ф20', 'Ф%d' % D], ['%%C20', '∅%d' % D], ['∅20', '∅%d' % D], ['Н5', 'Н2']])
    op(t='txtrep', win=A(0, 0) + A(7000, H), pairs=[['Ф20', 'Ф%d' % D]])
    op(t='settext', h=R('18C35'), s='{\\LКолонна %s (%d шт.)}' % (mk, T['n']))
    op(t='settext', h=R('18C86'), s='Колонна %s' % mk)
    op(t='settext', h=R('19531'), s=num)
    notes = ['Схему расположения колонн см. лист 4.1. Армирование - по расчёту ЛИРА-САПР "массаподготовка блок 3 униф".',
             'Бетонирование узлов вести после установки арматуры ригелей и сеток С1. Защитный слой - 40 мм до грани продольной арматуры.',
             'Сварка ручная дуговая, электроды Э-42А по ГОСТ 9467-75. Стыки продольной арматуры - С21-Рн (ГОСТ 14098-2014), вразбежку.',
             'Сетки С1 - из двух взаимно перпендикулярных элементов (поз. 10, 11). Бетон C20/25 (B25), арматура А500С.']
    if T.get('note7'): notes.append(T['note7'])
    op(t='settext', h=R('18CB3'), s='{\\C0;' + '\\P'.join('%d. %s' % (i + 1, s) for i, s in enumerate(notes)) + '}')
    return dict(mark=mk, mass=round(tot, 2), hoops=nh_, X1L=X1L, L1=L1, L2=L2, vol=round(b * h * Hc / 1e9, 2), As=round(nbar * 6.158, 1))
