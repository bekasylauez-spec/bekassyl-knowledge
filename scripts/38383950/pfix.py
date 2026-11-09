D = 'D:\\Бекасыл КЖ КМ\\Завод_В109_КМ\\_авто\\revit\\'
s = ''
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a)); s = s.replace(a, b)
p = D + 'gen.py'; s = open(p, encoding='utf-8').read()
rep("""    pa, pb = trim(a, b, gtrim(xa, ya) + EXT, gtrim(xb, yb) + EXT)
    B('ГС1', 'Tb', '□100x3', pa, pb)""", """    pa, pb = trim(a, b, gtrim(xa, ya) + EXT, gtrim(xb, yb) + EXT)
    B('ГС1', 'Tb', '□100x3', pa, pb, gs_roll(pa, pb, [0, -dz(ya), 1]))""")
rep("""    pa, pb = trim(a, b, anx_trim(p, q) + EXT, anx_trim(q, p) + EXT)
    B('ГС1', 'Tb', '□100x3', pa, pb)""", """    pa, pb = trim(a, b, anx_trim(p, q) + EXT, anx_trim(q, p) + EXT)
    B('ГС1', 'Tb', '□100x3', pa, pb, gs_roll(pa, pb, [-150.0 / 7100.0, 0, 1]))""")
rep("GSZ = 68.0", """def gs_roll(a, b, rn):          # ГС1 tube turned about its axis so its top face lies in the roof plane (gusset / tab flat on it); Revit angle = −θ (as Пр1)
    u, _ = unit(a, b); rn = nrm(rn)
    up = nrm([-u[0] * u[2], -u[1] * u[2], 1 - u[2] * u[2]])
    c = [up[1] * rn[2] - up[2] * rn[1], up[2] * rn[0] - up[0] * rn[2], up[0] * rn[1] - up[1] * rn[0]]
    return -math.degrees(math.atan2(sum(c[i] * u[i] for i in range(3)), sum(up[i] * rn[i] for i in range(3))))
GSZ = 68.0""")
rep("""        B('Р1', 'Tb', '□100x5', [AX[i] + 160 + EXT, y, 10340], [AX[i + 1] - 160 - EXT, y, 10340])""",
    """        rx = 160 + EXT + (100 if i in BRACED else 0)            # braced bay: Р1 end beyond the СВ1 ends (one gusset with them, узел 7)
        B('Р1', 'Tb', '□100x5', [AX[i] + rx, y, 10340], [AX[i + 1] - rx, y, 10340])""")
open(p, 'w', encoding='utf-8').write(s)
p = D + 'nodes.py'; s = open(p, encoding='utf-8').read()
rep("""def colstiff(g, x, y, z, prof, sides, t=14):""", """def colstiff(g, x, y, z, prof, sides, t=14, wtop=True):""")
rep("""            weld(g, [xa, ya, z + t / 2], [sx, 0, 0], [0, 0, 1], [0, 1, 0], 6, yb - ya)""", """            weld(g, [xa, ya, z + t / 2 if wtop else z - t / 2], [sx, 0, 0], [0, 0, 1 if wtop else -1], [0, 1, 0], 6, yb - ya)""")
rep("""            colstiff(g + ' связь', x, y, top - 4, pr, (-1, 1), 8)""", """            colstiff(g + ' связь', x, y, top - 4, pr, (-1, 1), 8, False)""")
rep("""    weld(g, [x - bf / 2, ye, zb - m], [0, sy, 0], [0, 0, -1], [1, 0, 0], 6, bf)
    weld(g, [x - 125, yf, zl - 100]""", """    weld(g, [x - 125, yf, zl - 100]""")
rep("""    weld(g, [x - 150, yf, zf], [0, sy, 0], [0, 0, 1], [1, 0, 0], 8, 300)                                       # covers ↔ column flange
    weld(g, [x - 150, yf, zf - h - 16], [0, sy, 0], [0, 0, -1], [1, 0, 0], 8, 300)""", """    captop = top_of_cap(x, y)
    weld(g, [x - 150, yf, captop], [0, -sy, 0], [0, 0, 1], [1, 0, 0], 8, 300)                                  # top cover ↔ cap / column (corner over the cap)
    for xs0, xs1 in ((x - 150, x - 4.5), (x + 4.5, x + 150)):                                                  # bottom cover ↔ column flange, either side of the bracket
        weld(g, [xs0, yf, zf - h - 16], [0, sy, 0], [0, 0, -1], [1, 0, 0], 8, xs1 - xs0)""")
rep("""    zw0 = min(zf, ztop(yf + sy * 100)) - tf - 15; hw = h - 2 * tf - 30""", """    zw0 = min(zf, ztop(yf + sy * 100)) - tf - RR[mp] - 3; hw = h - 2 * tf - 2 * RR[mp] - 6     # clear of the root fillets""")
rep("""def colprof(x, y): return '60Ш3' if""", """def top_of_cap(x, y): return 14490.0 if (abs(y) < 1 or abs(y - 60000) < 1) else 15097.0
def colprof(x, y): return '60Ш3' if""")
rep("""def purlin_plate(g, P0, along, up, wid, ends):""", """def purlin_plate(g, P0, along, up, wid, ends, rib=170.0):""")
rep("""    ply(g, add(add(P0, side, 55.8), along, 0), side, up, [(0, 0), (170, 0), (45, 200), (0, 200)], 8, True)""", """    ply(g, add(add(P0, side, 55.8), along, 0), side, up, [(0, 0), (rib, 0), (45, 200), (0, 200)], 8, True)""")
rep("""        purlin_plate('Пристройка Пр1 опора ' + str(int(xp)) + ' ' + str(int(y)), [xp, y, zs], [0, 1, 0], [0, 0, 1], 130, ends)""",
    """        purlin_plate('Пристройка Пр1 опора ' + str(int(xp)) + ' ' + str(int(y)), [xp, y, zs], [0, 1, 0], [0, 0, 1], 130, ends, 100.0 if xp > -1000 else 170.0)""")
open(p, 'w', encoding='utf-8').write(s)
p = D + 'b109_11_tube_nodes.cs'; s = open(p, encoding='utf-8').read()
rep("""                foreach (var sw in new[] { 1.0, -1.0 })
                {   // cap ↔ tube welds on the four outer edges""", """                foreach (var sw in e.TopLap ? new[] { -1.0 } : new[] { 1.0, -1.0 })
                {   // cap ↔ tube welds on the outer edges (top lap: not under the tab)""")
rep("""                    welds.Add(Weld(b0, e0.Mn, -n, dir, 6, len, soW)); welds.Add(Weld(b0 + n * 10 * MM, e0.Mn, n, dir, 6, len, soW));""",
    """                    welds.Add(Weld(b0, e0.Mn, -n, dir, 6, len, soW)); if (!L[0].TopLap) welds.Add(Weld(b0 + n * 10 * MM, e0.Mn, n, dir, 6, len, soW));   // top lap: top face flush with the flange""")
rep("""                    foreach (var yy in new[] { new[] { yr - chf + ctf, yr + 2 }, new[] { yr + 16, yr + chf - ctf } })""",
    """                    foreach (var yy in new[] { new[] { yr - chf + ctf + 29, yr + 2 }, new[] { yr + 16, yr + chf - ctf - 29 } })   // clear of the root fillets (r 28)""")
open(p, 'w', encoding='utf-8').write(s); print('ok')
