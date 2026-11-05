# ---------------- sections 1:25 (x2)
K = 2.0


def section(cx, cy, title, kind):
    """kind: 'low' (700x900 hoops), 'lowtop' (П at the top of the lower part), 'up' (600x600 hoops), 'uptop' (П at the top)"""
    S = lambda x, y: W(cx + K * x, cy + K * y)
    bx, by = (C.BX, C.BY) if kind.startswith('low') else (C.UB, C.UB)
    bars = C.BARS if kind.startswith('low') else C.UBARS
    pl('18CB9', [S(-bx / 2, -by / 2), S(bx / 2, -by / 2), S(bx / 2, by / 2), S(-bx / 2, by / 2)], closed=True)
    for x, y in bars: dot(S(x, y), K * C.D / 2)
    ox = bx / 2 + 250
    if kind in ('low', 'up'):
        if kind == 'low':
            for k, (a, b) in enumerate((C.X1, C.X2, C.X3)):
                if k == 1: b -= 24
                if k == 2: a -= 24
                ln([S(-a / 2, -b / 2), S(a / 2, -b / 2), S(a / 2, b / 2), S(-a / 2, b / 2)], 'диам10', 30, closed=True)
                ln([S(-a / 2, b / 2), S(-a / 2 + 55, b / 2 - 55)], 'диам10', 30)
            xs = [-bx / 2] + C.XS + [bx / 2]; ys = [-by / 2] + C.YS + [by / 2]
        else:
            a = C.X4[0]
            ln([S(-a / 2, -a / 2), S(a / 2, -a / 2), S(a / 2, a / 2), S(-a / 2, a / 2)], 'диам10', 30, closed=True)
            ln([S(-a / 2, a / 2), S(-a / 2 + 55, a / 2 - 55)], 'диам10', 30)
            r = C.X5R - 12
            ln([S(0, -r), S(r, 0), S(0, r), S(-r, 0)], 'диам10', 30, closed=True)
            xs = [-bx / 2, -C.UO, 0, C.UO, bx / 2]; ys = xs[:]
        yb_ = -by / 2
        for k, (a, b) in enumerate(zip(xs, xs[1:])):
            tx = S(a - 130, yb_ - 330) if k == 0 else (S(b + 130, yb_ - 330) if k == len(xs) - 2 else None)
            dim('18CF8', S(a, yb_), S(b, yb_), S(0, yb_ - 230), False, None, tx)
        dim('18CF8', S(-bx / 2, yb_), S(bx / 2, yb_), S(0, yb_ - 430), False)
        xl = -bx / 2
        for k, (a, b) in enumerate(zip(ys, ys[1:])):
            tx = S(xl - 330, a - 130) if k == 0 else (S(xl - 330, b + 130) if k == len(ys) - 2 else None)
            dim('18CF8', S(xl, a), S(xl, b), S(xl - 230, 0), True, None, tx)
        dim('18CF8', S(xl, -by / 2), S(xl, by / 2), S(xl - 430, 0), True)
        if kind == 'low':
            nb = lambda i: str(2 * i + 1)
            note('%s, %s...' % (1, 2 * len(sch['joints']) - 1) if len(sch['joints']) > 1 else '1', '(%%C28)', S(C.XS[-1], C.YS[-1]), S(ox, 520), 'None')
            note('%s, %s...' % (2, 2 * len(sch['joints'])) if len(sch['joints']) > 1 else '2', '(%%C28)', S(C.XS[-1], C.YS[3]), S(ox, 260), 'None')
            note('Х3', '(%%C10)', S(C.X3[0] / 2 - 12, -60), S(ox, 0), 'Oblique')
            note('Х1', '(%%C10)', S(C.X1[0] / 2, -300), S(ox, -260), 'Oblique')
            note('Х2', '(%%C10)', S(C.X2[0] / 2, -C.YS[-1] + 120), S(ox, -520), 'Oblique')
        else:
            note(str(2 * len(sch['joints']) + 1), '(%%C28)', S(C.UO, C.UO), S(ox, 330), 'None')
            note('Х4', '(%%C10)', S(C.X4[0] / 2, -150), S(ox, 0), 'Oblique')
            note('Х5', '(%%C10)', S(C.X5R / 2, -C.X5R / 2), S(ox, -330), 'Oblique')
    elif kind == 'lowtop':
        for x in C.XS: ln([S(x, C.YS[0]), S(x, C.YS[-1])], 'диам16', 40)
        for y in C.YS[1:-1]: ln([S(C.XS[0], y), S(C.XS[-1], y)], 'диам16', 40)
        note('Ск1', '(%%C16)', S(C.XS[2], C.YS[3] + 80), S(ox, by / 2 + 200), 'Oblique')
        note('Ск2', '(%%C16)', S(C.XS[-1] - 120, C.YS[1]), S(ox, C.YS[1] - 200), 'Oblique')
    else:
        for x in (-C.UO, 0, C.UO): ln([S(x, -C.UO), S(x, C.UO)], 'диам16', 40)
        ln([S(-C.UO, 0), S(C.UO, 0)], 'диам16', 40)
        note('Ск3', '(%%C16)', S(C.UO / 2, C.UO / 2), S(ox, by / 2 + 200), 'Oblique')
    h = clone('18CB6'); add(t='settext', h=h, s='{\\L%s}' % title)
    add(t='moveto', h=h, idx=0, to=S(-bx / 2, by / 2 + 300))


section(9300, 17200, 'Разрез 1 - 1', 'low')
if col['z1']:
    section(13900, 17400, 'Разрез 2 - 2', 'up')
    section(9700, 12700, 'Разрез 3 - 3', 'uptop')
else:
    section(13900, 17200, 'Разрез 2 - 2', 'lowtop')

# ---------------- ведомость деталей (own lines, text 2.5 mm = 125)
PD = {p[0]: p for p in sch['pos']}
DET = [(p, g) for p, g in (('Х1', C.X1), ('Х2', C.X2), ('Х3', C.X3), ('Х4', C.X4), ('Х5', None), ('Ск1', C.SK1), ('Ск2', C.SK2),
                           ('Ск3', C.SK3), ('К1', None), ('Хк', (C.BX - 60, C.CONS['h'] - 60))) if p in PD]
RH = 960 if len(DET) <= 6 else 760
TX0, TY1, CW0, CW = X0 + 16600, Y0 + 20250, 600, 2900
TY0 = TY1 - 400 - RH * len(DET)


def tx(x, y, s, att=5, rot=None):
    d = dict(t='mtext', at=[round(x, 1), round(y, 1)], h=125, layer='Размеры', s=s, att=att)
    if rot is not None: d['rot'] = rot
    add(**d)


tx(TX0 + (CW0 + CW) / 2, TY1 + 230, 'Ведомость деталей')
ln([[TX0, TY0], [TX0 + CW0 + CW, TY0], [TX0 + CW0 + CW, TY1], [TX0, TY1]], '0', 30, closed=True)
ln([[TX0 + CW0, TY0], [TX0 + CW0, TY1]], '0', 30)
ln([[TX0, TY1 - 400], [TX0 + CW0 + CW, TY1 - 400]], '0', 30)
tx(TX0 + CW0 / 2, TY1 - 200, 'Поз.'); tx(TX0 + CW0 + CW / 2, TY1 - 200, 'Эскиз')
for k, (pos, g) in enumerate(DET):
    yt = TY1 - 400 - RH * k; yb = yt - RH
    if k: ln([[TX0, yt], [TX0 + CW0 + CW, yt]], '0', 30)
    tx(TX0 + CW0 / 2, (yt + yb) / 2, pos)
    _, d, L, n, _ = PD[pos]
    tx(TX0 + CW0 + CW / 2, yb + 110, '%%%%C%d A500С  L=%d' % (d, L))
    sx, sy = TX0 + CW0 + 700, yb + 250
    hh = RH - 480
    if pos == 'Х5':
        r = hh / 2; cx_, cy_ = sx + 300, sy + r
        ln([[cx_, cy_ - r], [cx_ + r, cy_], [cx_, cy_ + r], [cx_ - r, cy_]], 'диам10', 30, closed=True)
        tx(cx_ + r + 150, cy_, 'ромб %dх%d' % (round(C.X5R * 2), round(C.X5R * 2)), att=4)
    elif pos == 'К1':
        ln([[sx, sy + hh * 0.4], [sx, sy + hh], [sx + 1500, sy + hh], [sx + 1500, sy]], 'диам28', 40)
        tx(sx + 750, sy + hh + 90, '%d' % ((C.CONS['l'] - 30) + (C.BY - 60))); tx(sx - 90, sy + hh * 0.7, '400', rot=math.pi / 2)
        tx(sx + 1590, sy + hh / 2, '600', rot=math.pi / 2)
    elif pos.startswith('Х'):
        a, b = g
        if a < b: h_ = hh; w = max(150, h_ * a / b)
        else: w = min(700, hh * a / b); h_ = w * b / a
        ln([[sx, sy], [sx + w, sy], [sx + w, sy + h_], [sx, sy + h_]], 'диам10', 30, closed=True)
        ln([[sx + 60, sy + h_ - 60], [sx, sy + h_]], 'диам10', 30)
        tx(sx + w / 2, sy + h_ + 90, '%d' % a); tx(sx - 90, sy + h_ / 2, '%d' % b, rot=math.pi / 2)
        tx(sx + w + 150, sy + h_ / 2, 'крюки 135°, 2х100', att=4)
    else:
        web, leg = g; w = 1300; h_ = hh * 0.8
        ln([[sx, sy], [sx, sy + h_], [sx + w, sy + h_], [sx + w, sy]], 'диам16', 40)
        tx(sx + w / 2, sy + h_ + 90, '%d' % web); tx(sx - 90, sy + h_ / 2, '%d' % leg, rot=math.pi / 2)

