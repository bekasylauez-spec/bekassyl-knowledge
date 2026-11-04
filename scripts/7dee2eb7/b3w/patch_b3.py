# Adapt the Block 4 generator to Block 3 (axes 22..33, three slab pieces, A2 sheets for Пм2).
s = open('gen.py', encoding='utf-8').read()
def R(old, new, cnt=1):
    global s
    assert s.count(old) >= 1, old[:80]
    s = s.replace(old, new) if cnt == 0 else s.replace(old, new, cnt)

R("# Block 4 slabs Пм1 (+7.000) and Пм2 (+4.500): build ops for the copy of the analog Б2.плита1.dwg.\n# Local plan coords (mm): x from axis 32, y from axis А.",
  "# Block 3 slabs Пм1 (+7.000) and Пм2 (+4.500): build ops for the copy of the analog Б2.плита1.dwg.\n# Local plan coords (mm): x from axis 22, y from axis А.")
R("AXX = OrderedDict([('32', 0), ('33', 650), ('34', 6650), ('35', 12650), ('36', 18650), ('37', 24850), ('38', 31850), ('39', 38850), ('40', 44850)])",
  "AXX = OrderedDict([('22', 0), ('23', 650), ('24', 5950), ('25', 11300), ('26', 17300), ('27', 23300), ('28', 29300), ('29', 35300),\n                   ('30', 41300), ('31', 47300), ('32', 53300), ('33', 53950)])")
R("""    'P70': dict(name='Пм1', lvl='+7.000', lvlb='+6.800', geo='g3.txt', ax=list(AXX), ay=list(AXY), sheets0=1),
    'P45': dict(name='Пм2', lvl='+4.500', lvlb='+4.300', geo='g2.txt', ax=['35', '36', '37'], ay=['А', 'Б'], sheets0=6),""",
  """    'P70': dict(name='Пм1', lvl='+7.000', lvlb='+6.800', geo='../b3/g3.txt', ax=list(AXX), ay=list(AXY), sheets0=1),
    'P45': dict(name='Пм2', lvl='+4.500', lvlb='+4.300', geo='../b3/g2.txt', ax=['22', '23', '24', '25', '26', '27'], ay=['А', 'Б', 'В'], sheets0=8),""")
# helpers for multi-piece slabs
R("def lines_of(geom):", """def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g): return [r for p in polys(g) for r in [p.exterior] + list(p.interiors)]
def holes(g): return [r for p in polys(g) for r in p.interiors]
HOLES = [h for h in SLABS['P70']['holes']]

def lines_of(geom):""")
# sheets: Пм1 A1 x7 (spec A1), Пм2 A2 x4 + A3 spec
R("""for i in range(5): SH[('P45', i)] = dict(X0=-791072 + i * 47000, Y0=-3200000, fmt=A3)
def org(k, i):
    s = SH[(k, i)]
    if k == 'P70': return s['X0'] + 9000, s['Y0'] - 51000
    return s['X0'] + 350, s['Y0'] - 14300""", """for i in range(5): SH[('P45', i)] = dict(X0=-791072 + i * 64000, Y0=-3200000, fmt=A2 if i < 4 else A3)
def org(k, i):
    s = SH[(k, i)]
    if k == 'P70': return s['X0'] + 5500, s['Y0'] - 51000
    return s['X0'] + 6500, s['Y0'] - 18000""")
# background
R("""    for ring in [g.exterior] + list(g.interiors):
        sh.pl(list(ring.coords)[:-1], closed=True, layer='Plita', lw=lw, color=7)
    for ring in g.interiors:""", """    for ring in rings(g):
        sh.pl(list(ring.coords)[:-1], closed=True, layer='Plita', lw=lw, color=7)
    marks = [list(r.coords) for r in holes(g)]
    if sh.k == 'P70': marks.append([(41300, -250), (44300, -250), (44300, 6300), (41300, 6300)])   # stair well cut from the edge
    for ring in marks:""")
R("""        if sh.k == 'P70' and n == '32': bx = x - 500
        if sh.k == 'P70' and n == '33': bx = x + 400""", """        names = list(ax); j = names.index(n)
        if j + 1 < len(names) and ax[names[j + 1]] - x < 1000: bx = x - 500       # close axes (650): bubbles apart
        if j > 0 and x - ax[names[j - 1]] < 1000: bx = x + 400""")
R("""    left_edge = [y for (x, y) in g.exterior.coords if abs(x - x0) < 1]
    pts = sorted(set([round(min(left_edge)), round(max(left_edge))] + ys_ax))""", """    left_edge = [y for p in polys(g) for (x, y) in p.exterior.coords if abs(x - x0) < 1]
    pts = sorted(set([round(v) for v in left_edge] + ys_ax))""")
R("""    if sh.k == 'P70':
        # right side: slab edge at Е+250 and А-250
        pts = sorted(set([-250, 36250] + [y for y in ys_ax if y <= 36000]))
        for a, b in zip(pts, pts[1:]): sh.dim((x1, a), (x1, b), (x1 + c1, a), rot=90)""", """    right_edge = [y for p in polys(g) for (x, y) in p.exterior.coords if abs(x - x1) < 1]
    pts = sorted(set([round(v) for v in right_edge] + [y for y in ys_ax if min(right_edge) <= y <= max(right_edge)]))
    for a, b in zip(pts, pts[1:]): sh.dim((x1, a), (x1, b), (x1 + c1, a), rot=90)""")
# opalubka dims
R("""        # atrium edges and openings bound to axes
        sh.dim((2000, 13900), (2000, 16400), (2000, 13900), rot=90)
        sh.dim((2000, 25500), (2000, 27500), (2000, 25500), rot=90)
        sh.dim((31550, 20000), (31850, 20000), (31550, 19000))
        sh.dim((12650, 39300), (12950, 39300), (12650, 40300))
        for (a, b, c, d) in [(26725, 1700, 29275, 7300), (39950, 17050, 44550, 25950)]:
            axv = max([v for v in AXX.values() if v <= a]); ayv = max([v for v in AXY.values() if v <= b])
            sh.dim((axv, d), (a, d), (axv, d + 700)); sh.dim((a, d), (c, d), (a, d + 700))
            xv = a - 700 if c > 40000 else c + 700; xe = a if c > 40000 else c
            sh.dim((xe, ayv), (xe, b), (xv, ayv), rot=90); sh.dim((xe, b), (xe, d), (xv, b), rot=90)""", """        # atrium edges, notch, opening and stair well bound to axes
        sh.dim((2000, 13900), (2000, 16900), (2000, 13900), rot=90)
        sh.dim((2000, 25500), (2000, 27500), (2000, 25500), rot=90)
        sh.dim((16950, 39300), (17300, 39300), (16950, 40300))
        for (a, b, c, d) in [(36700, 2400, 39900, 5600), (41300, -250, 44300, 6300)]:
            axv = max([v for v in AXX.values() if v <= a]); ayv = max([v for v in AXY.values() if v <= max(b, 0)])
            if a - axv > 1: sh.dim((axv, d), (a, d), (axv, d + 700))
            sh.dim((a, d), (c, d), (a, d + 700))
            if b - ayv > 1: sh.dim((c, ayv), (c, b), (c + 700, ayv), rot=90)
            sh.dim((c, b), (c, d), (c + 700, b), rot=90)""")
R("""    s1x = 9650 if sh.k == 'P70' else 15650
    s2 = (12650, 4500) if sh.k == 'P70' else (18650, 4500)""", """    s1x = 8600
    s2 = (11300, 4500)""")
# main sheet
R("""    if sh.k == 'P70': ax = [v for v in ax if v != 0]       # slab starts at axis 33""",
  """    ax = [v for v in ax if x0 + 100 < v < x1 - 100]; ay = [v for v in ay if y0 + 100 < v < y1 - 100]""")
R("""    if sh.k == 'P70': xm, ym = 4000, 4500\n""", "")
R("""    edges = list(zip(list(g.exterior.coords), list(g.exterior.coords)[1:]))
    for ring in g.interiors: edges += list(zip(list(ring.coords), list(ring.coords)[1:]))""",
  """    edges = []
    for ring in rings(g): edges += list(zip(list(ring.coords), list(ring.coords)[1:]))""")
# spec perimeter
R("""    per = g.exterior.length + sum(r.length for r in g.interiors)""", """    per = sum(r.length for r in rings(g))""")
# sections: Block 3 beams and plan marks
R("""SEC70 = [  # num, b, h, edge, column, row, plan mark (x, y, rot)
    (1, 400, 700, False, 0, 0, (4000, 3000, 0)),
    (2, 400, 700, True, 1, 0, (9650, -250, 0)),
    (3, 400, 1000, False, 0, 1, (18650, 4500, 90)),
    (4, 400, 1000, True, 1, 1, (44850, 4500, 90)),
    (5, 250, 600, False, 0, 2, (15650, 8250, 0)),
]
STAIR = (12950, 36250, 18650, 39300)        # stair well Е-Ж / 35-36 (LIRA stiffness 40: flights 14450..16880, landing +7.000 16880..18650)
AB1 = dict(x0=16900, x1=18500, edge=36250)   # АВ-1 Ø14 @200 into the +7.000 landing (as analog Пм1 «выпуски для лестницы»)""",
  """SEC70 = [  # num, b, h, edge, column, row, plan mark (x, y, rot) - LIRA +7.000: X beams 400x700, Y beams 400x1000, secondary 250x600
    (1, 400, 700, False, 0, 0, (3300, 9000, 0)),
    (2, 400, 700, True, 1, 0, (8600, -250, 0)),
    (3, 400, 1000, False, 0, 1, (11300, 4500, 90)),
    (4, 400, 1000, True, 1, 1, (53300, 4500, 90)),
    (5, 250, 600, False, 0, 2, (14300, 3000, 0)),
]
SECX = (69000, 75000)                         # section columns (x from the sheet's left edge); plan is 54 m wide here
AB1 = dict(y0=36450, y1=38850, edge=16950)   # АВ-1 Ø14 @200 along X into the +7.000 landing 15530..16950 (stair Е-Ж / 25-26, LIRA)""")
R("""def stair_ab(sh):
    a, b, e = AB1['x0'], AB1['x1'], AB1['edge']
    n = int((b - a) // 200) + 1; b = a + 200 * (n - 1)
    for x in (a, b): sh.line(x, e - 1200, x, e + 1300, layer='ф14_арм', lw=40)
    sh.dim((a, e + 1300), (b, e + 1300), (a, e + 1650), text='200х%d' % (n - 1))
    sh.dim((a, e - 1200), (a, e), (a - 350, e - 1200), rot=90); sh.dim((a, e), (a, e + 1300), (a - 350, e), rot=90)
    add(t='mlx', h='BCEEA57E', text='АВ-1', textloc=sh.P((a + b) / 2, e + 700), arrows=[sh.P(a, e + 500), sh.P(b, e + 500)])
    add(t='clone', h=T['secmark'], to=sh.P((a + b) / 2, e), dyn={'Расстояние1': 1700, 'Расстояние2': 1700}, att={'В1': '6', 'В2': '6', 'Г1': '6', 'Г2': '6'})
    X0, Y0 = SH[(sh.k, sh.i)]['X0'], SH[(sh.k, sh.i)]['Y0']
    section(X0 + 70000, Y0 - 9000, 6, 400, 700, False, lo=5200, ro=5600, ab=True)""",
  """def stair_ab(sh):
    # bars along X across the slab edge x = 16950: 1200 into the slab, 1300 into the landing (west)
    a, b, e = AB1['y0'], AB1['y1'], AB1['edge']
    n = int((b - a) // 200) + 1; b = a + 200 * (n - 1)
    for y in (a, b): sh.line(e - 1300, y, e + 1200, y, layer='ф14_арм', lw=40)
    sh.dim((e - 1300, a), (e - 1300, b), (e - 1650, a), rot=90, text='200х%d' % (n - 1))
    sh.dim((e - 1300, a), (e, a), (e - 1300, a - 350)); sh.dim((e, a), (e + 1200, a), (e, a - 350))
    add(t='mlx', h='BCEEA57B', text='АВ-1', textloc=sh.P(e - 700, (a + b) / 2), arrows=[sh.P(e - 500, a), sh.P(e - 500, b)])
    add(t='clone', h=T['secmark'], to=sh.P(e, (a + b) / 2), rot=90, dyn={'Расстояние1': 1700, 'Расстояние2': 1700}, att={'В1': '6', 'В2': '6', 'Г1': '6', 'Г2': '6'})
    X0, Y0 = SH[(sh.k, sh.i)]['X0'], SH[(sh.k, sh.i)]['Y0']
    section(X0 + 72000, Y0 - 9000, 6, 400, 1000, False, lo=5200, ro=5600, ab=True)""")
R("""        cx = X0 + (65000 if col == 0 else 74500)""", """        cx = X0 + SECX[col]""")
open('gen.py', 'w', encoding='utf-8').write(s)
print('ok')
