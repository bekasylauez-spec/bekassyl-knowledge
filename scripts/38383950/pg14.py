D = 'D:\\Бекасыл КЖ КМ\\Завод_В109_КМ\\_авто\\revit\\'
s = ''
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a)); s = s.replace(a, b)
p = D + 'gen.py'; s = open(p, encoding='utf-8').read()
# top tier: X (узел 14 — СВ2/СВ3 comes to the column at +10.340 from above; узел 1 2-2 — to the column top from below)
rep("""        mark = 'СВ2' if r in 'AM' else 'СВ3'; bw2 = 100
        ii = i
        for xc, ic in ((xa, ii), (xb, ii + 1)):
            zmax = coltop(ic, r); zmin = ts_top(ic, r); zn = (zmax + zmin) / 2      # узел 1 разрез 2-2: gusset −8 welded to the cap underside
            a, b = [xc, y, zn], [xm, y, 10340 + hs]
            th = math.atan2(abs(zn - b[2]), abs(xm - xc))
            tc = bw2 / 2 * max(math.tan(th), 1 / math.tan(th)) + 10
            pa, pb = trim(a, b, tc + 20, apex(bw2, th) + EXT)  # узел 1 разрез 2-2: the tube ends at the column flange edge (end plate 20 off), its insert inside the band
            B(mark, 'Tb', '□100x5', pa, pb)
            sx = 1 if xm > xc else -1
            BRACE_TOP.append((AX[ic], y, zmin, zmax, sx))""",
"""        # top tier СВ2 / СВ3: X too (user's узел 14 at +10.340 + узел 1 разрез 2-2 at the column top): column web +10.340 ↔ the other column's top band
        mark = 'СВ2' if r in 'AM' else 'СВ3'; bw2 = 100
        zns = []
        for xc, ic in ((xa, i), (xb, i + 1)):
            zmax = coltop(ic, r); zmin = ts_top(ic, r); zns.append((zmax + zmin) / 2)
            BRACE_TOP.append((AX[ic], y, zmin, zmax, 1 if xm > xc else -1))
        D1 = ([xa, y, 10340.0], [xb, y, zns[1]]); D2 = ([xb, y, 10340.0], [xa, y, zns[0]])
        def tcx(p, q):
            th = math.atan2(abs(q[2] - p[2]), abs(q[0] - p[0])); return bw2 / 2 * max(math.tan(th), 1 / math.tan(th)) + 10, th
        t1, th1 = tcx(*D1)
        pa, pb = trim(D1[0], D1[1], t1 + EXT, t1 + 20)                    # through diagonal: +10.340 gusset … column top band (end at the flange edge, узел 1)
        B(mark, 'Tb', '□100x5', pa, pb)
        u1, _ = unit(*D1); u2, _ = unit(*D2)
        den = u1[0] * u2[2] - u1[2] * u2[0]
        tt = ((D2[0][0] - D1[0][0]) * u2[2] - (D2[0][2] - D1[0][2]) * u2[0]) / den
        O = [D1[0][0] + u1[0] * tt, y, D1[0][2] + u1[2] * tt]
        a_ = math.acos(abs(u1[0] * u2[0] + u1[2] * u2[2])); a_ = min(a_, math.pi - a_)
        tx = bw2 / 2 / math.sin(a_) + bw2 / 2 / math.tan(a_) + 10
        t2, _ = tcx(*D2)
        q0, q1 = trim(D2[0], O, t2 + EXT, tx + EXT); B(mark, 'Tb', '□100x5', q0, q1)
        q0, q1 = trim(D2[1], O, t2 + 20, tx + EXT); B(mark, 'Tb', '□100x5', q0, q1)
        XCROSS.append(dict(o=O, u=u1, b=bw2))""")
# узел 12: Р2 under the bottom chord on a plate −8 welded to the chord bottom, tab −8 on the Р2 top, 2 bolts М16 — Р2 ends 150 off the truss axis
rep("""for y in P2Y:
    z = BC(y)
    for i in range(1, 26):
        B('Р2', 'Tb', '□100x3', [AX[i] + 60.3, y, z], [AX[i + 1] - 60.3, y, z])
        P2_ENDS.append(([AX[i] + 60.3, y, z], [-1, 0, 0])); P2_ENDS.append(([AX[i + 1] - 60.3, y, z], [1, 0, 0]))""",
"""def p2z(y):                  # узел 12: Р2 axis — plate −8 under the chord bottom (lowest over ±80), tab −8, tube 100
    return min(BC(y - 80), BC(y + 80)) - 60 - 0.5 - 16 - 50
for y in P2Y:
    z = p2z(y)
    for i in range(1, 26):
        B('Р2', 'Tb', '□100x3', [AX[i] + 150, y, z], [AX[i + 1] - 150, y, z])""")
rep("""            a, b = [xm, yb, BC(yb) + 50], [xa, yb, TC(yb) + 40]          # one plane (y = yb); top aimed 40 over the chord axis (insert clear of the bottom flange)""",
    """            a, b = [xm, yb, p2z(yb) + 50], [xa, yb, TC(yb) + 40]          # bottom on the Р2 top (узел 12: Р2 under the chord); top 40 over the chord axis""")
rep("""    for b in BRACE_TOP: f.write('\\t'.join(['T'] + ['%.3f' % v for v in b]) + '\\n')""",
    """    for b in BRACE_TOP: f.write('\\t'.join(['T'] + ['%.3f' % v for v in b]) + '\\n')
    for y in P2Y: f.write('\\t'.join(['P', '%.3f' % y, '%.3f' % (p2z(y) + 50), '%.3f' % (min(BC(y - 80), BC(y + 80)) - 60)]) + '\\n')""")
# БМ2 at axes 1 / 28: 150 beyond the axis (sheet 26, 6145)
rep("""B('БМ1', 'W', 'I660 250-200', [AX[i] + (8 if i else 0), y, 11000], [AX[i + 1] - (8 if i < 26 else 0), y, 11000])""",
    """B('БМ2' if i in (0, 26) else 'БМ1', 'W', 'I660 250-200', [AX[i] + (8 if i else -150), y, 11000], [AX[i + 1] - (8 if i < 26 else -150), y, 11000])""")
open(p, 'w', encoding='utf-8').write(s); print('ok')
