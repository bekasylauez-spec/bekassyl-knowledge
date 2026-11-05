# ---------------- sections 1:25 (x2)
K = 2.0


def section(cx, cy, title, pi):
    S = lambda x, y: W(cx + K * x, cy + K * y)
    pl('18CB9', [S(-C.BX / 2, -C.BY / 2), S(C.BX / 2, -C.BY / 2), S(C.BX / 2, C.BY / 2), S(-C.BX / 2, C.BY / 2)], closed=True)
    for x, y in C.BARS: dot(S(x, y), K * C.D / 2)
    if pi:
        for k, (a, b) in enumerate((C.X1, C.X2, C.X3)):
            if k == 1: b -= 24
            if k == 2: a -= 24
            ln([S(-a / 2, -b / 2), S(a / 2, -b / 2), S(a / 2, b / 2), S(-a / 2, b / 2)], 'диам10', 30, closed=True)
            ln([S(-a / 2, b / 2), S(-a / 2 + 55, b / 2 - 55)], 'диам10', 30)
        # dims: bottom (cover/bar steps), left
        yb_ = -C.BY / 2
        xs = [-C.BX / 2] + C.XS + [C.BX / 2]
        for k, (a, b) in enumerate(zip(xs, xs[1:])):
            tx = None
            if k == 0: tx = S(a - 130, yb_ - 330)
            if k == len(xs) - 2: tx = S(b + 130, yb_ - 330)
            dim('18CF8', S(a, yb_), S(b, yb_), S(0, yb_ - 230), False, None, tx)
        for a, b in ((-C.BX / 2, 0), (0, C.BX / 2)):
            dim('18CF8', S(a, yb_), S(b, yb_), S(0, yb_ - 430), False)
        ys = [-C.BY / 2] + C.YS + [C.BY / 2]
        xl = -C.BX / 2
        for k, (a, b) in enumerate(zip(ys, ys[1:])):
            tx = None
            if k == 0: tx = S(xl - 330, a - 130)
            if k == len(ys) - 2: tx = S(xl - 330, b + 130)
            dim('18CF8', S(xl, a), S(xl, b), S(xl - 230, 0), True, None, tx)
        for a, b in ((-C.BY / 2, 0), (0, C.BY / 2)):
            dim('18CF8', S(xl, a), S(xl, b), S(xl - 430, 0), True)
        ox = C.BX / 2 + 250
        note('1', '(%%C28)', S(C.XS[-1], C.YS[-1]), S(ox, 520), 'None')
        note('2', '(%%C28)', S(C.XS[-1], C.YS[3]), S(ox, 260), 'None')
        note('Х3', '(%%C10)', S(C.X3[0] / 2 - 12, -60), S(ox, 0), 'Oblique')
        note('Х1', '(%%C10)', S(C.X1[0] / 2, -300), S(ox, -260), 'Oblique')
        note('Х2', '(%%C10)', S(C.X2[0] / 2, -C.YS[-1] + 120), S(ox, -520), 'Oblique')
    else:
        for x in C.XS:
            ln([S(x, C.YS[0]), S(x, C.YS[-1])], 'диам16', 40)
        for y in C.YS[1:-1]:
            ln([S(C.XS[0], y), S(C.XS[-1], y)], 'диам16', 40)
        note('Ск1', '(%%C16)', S(C.XS[2], C.YS[3] + 80), S(C.BX / 2 + 220, C.BY / 2 + 200), 'Oblique')
        note('Ск2', '(%%C16)', S(C.XS[-1] - 120, C.YS[1]), S(C.BX / 2 + 220, C.YS[1] - 200), 'Oblique')
    h = clone('18CB6'); add(t='settext', h=h, s='{\\L%s}' % title)
    add(t='moveto', h=h, idx=0, to=S(-C.BX / 2, C.BY / 2 + 300))


section(9300, 17200, 'Разрез 1 - 1', True)
section(13900, 17200, 'Разрез 2 - 2', False)

