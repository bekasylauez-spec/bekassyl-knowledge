P = r'D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\nodes.py'
s = open(P, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a)); s = s.replace(a, b)
rep("""# ================= Р2 □100x3 ends on the bottom chord side faces: fillet welds round the end
for c, u in gen.P2_ENDS:
    g = 'Узел Р2 ' + str(int(c[0])) + ' ' + str(int(c[1]))
    for a, dvec, out in (([0, -50, -50], [0, 1, 0], [0, 0, -1]), ([0, -50, 50], [0, 1, 0], [0, 0, 1]), ([0, -50, -50], [0, 0, 1], [0, -1, 0]), ([0, 50, -50], [0, 0, 1], [0, 1, 0])):
        weld(g, add(c, a), out, [-u[0], 0, 0], dvec, 4, 100)
""", """# ================= Р2 (узел 12): bolted under the bottom chord — b109_11 (plate −8 under the chord, tab + rib on the Р2, 2 bolts М16)
""")
rep("""        # tie plate −14 (x −7…+7) and the angle (leg on the plate's +X face, or −X at axis 28)""",
"""        # sheets 26 / 27: БМ1 intermediate ribs −90×6 C245 every 1200 (600 high from the top flange), both sides of the web
        if (y, off) and True:
            for k in (1, 2, 3, 4):
                if i < 27:
                    xr = x + 5 + 1200 * k
                    for s2 in (-1, 1):
                        box(g + ' рёбра', [xr - 3, min(yb + s2 * 3, yb + s2 * 93), 10390], [xr + 3, max(yb + s2 * 3, yb + s2 * 93), 10990])
        if i in (0, 27):
            # БМ2 end (150 beyond the axis): end rib −90×6 and the crane stop (sheet 26, 5-5): I 40Б2 940 high on the top flange, caps −t10 at the top and
            # at 450, bumper Гн□160×80×5 on the span side at the top
            se = 1 if i == 0 else -1; xend = x - se * 150
            for s2 in (-1, 1): box(g + ' упор', [min(xend, xend + se * 6), min(yb + s2 * 3, yb + s2 * 93), 10350], [max(xend, xend + se * 6), max(yb + s2 * 3, yb + s2 * 93), 10990])
            x0, x1 = min(xend, xend + se * 396), max(xend, xend + se * 396)
            gu = 'Упор крановый 40Б2 ' + str(int(x)) + ' ' + r + ' ' + str(int(off))
            zt0, zt1 = 11000.0, 11940.0
            box(gu, [x0, yb - 99.5, zt0], [x0 + 11.5, yb + 99.5, zt1 - 10])                # flanges (40Б2 396×199×7×11.5)
            box(gu, [x1 - 11.5, yb - 99.5, zt0], [x1, yb + 99.5, zt1 - 10])
            box(gu, [x0 + 11.5, yb - 3.5, zt0], [x1 - 11.5, yb + 3.5, zt1 - 10])           # web
            box(gu, [x0, yb - 110, zt1 - 10], [x1, yb + 110, zt1])                          # cap −t10
            for s2 in (-1, 1): box(gu, [x0 + 11.5, min(yb + s2 * 3.5, yb + s2 * 99.5), zt0 + 450 - 5], [x1 - 11.5, max(yb + s2 * 3.5, yb + s2 * 99.5), zt0 + 450 + 5])   # −t10 at 450
            bx0 = x1 if se > 0 else x0 - 80                                                  # bumper on the span side
            zb0, zb1 = zt1 - 160, zt1
            box(gu, [bx0, yb - 110, zb0], [bx0 + 80, yb + 110, zb0 + 5]); box(gu, [bx0, yb - 110, zb1 - 5], [bx0 + 80, yb + 110, zb1])
            box(gu, [bx0, yb - 110, zb0 + 5], [bx0 + 5, yb + 110, zb1 - 5]); box(gu, [bx0 + 75, yb - 110, zb0 + 5], [bx0 + 80, yb + 110, zb1 - 5])
            for sxx in (-1, 1): weld(gu, [x0 if sxx < 0 else x1, yb - 99.5, zt0], [sxx, 0, 0], [0, 0, 1], [0, 1, 0], 6, 199)
        # tie plate −14 (x −7…+7) and the angle (leg on the plate's +X face, or −X at axis 28)""")
# end stiffener full flange width 200 (−200×20 C345)
rep("""                box(g, [min(xe, xe + sx * 20), min(yb + s2 * 3, yb + s2 * 95), 10350], [max(xe, xe + sx * 20), max(yb + s2 * 3, yb + s2 * 95), 10990])""",
    """                box(g, [min(xe, xe + sx * 20), min(yb + s2 * 3, yb + s2 * 100), 10350], [max(xe, xe + sx * 20), max(yb + s2 * 3, yb + s2 * 100), 10990])""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
