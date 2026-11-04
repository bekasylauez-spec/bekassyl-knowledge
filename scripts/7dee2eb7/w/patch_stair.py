s = open('gen.py', encoding='utf-8').read()
s = s.replace("def section(X, Y, num, b, h, edge, lvl=('+7.000', '+6.800')):",
              "def section(X, Y, num, b, h, edge, lvl=('+7.000', '+6.800'), lo=918, ro=819, ab=None):")
s = s.replace("""        L0 = cx - hw - 918; R = cx + hw + 819
        out = [(L0, ys)""", """        L0 = cx - hw - lo; R = cx + hw + ro
        out = [(L0, ys)""")
s = s.replace("""        add(t='mleader', h='BCEE9DFB', d=[dx, dy, 0], arrow=[cx + hw * 0.4, ys - D * 0.5])
""", """        add(t='mleader', h='BCEE9DFB', d=[dx, dy, 0], arrow=[cx + hw * 0.4, ys - D * 0.5])
    if ab:
        # АВ-1: straight bar at the top cover, 1200 into the slab past the beam face, 1300 into the stair landing
        e = cx + hw + 200; yb1 = yt - 160
        add(t='pl', pts=[[e - 4 * 1200, yb1], [e + 4 * 1300, yb1]], layer='ф14_арм', w=60)
        add(t='clone', h='BCEE9DA5', p1=[e - 4 * 1200, yt], p2=[e, yt], dl=[e - 4 * 1200, yt + 900], rotd=0, text='')
        add(t='clone', h='BCEE9DA5', p1=[e, yt], p2=[e + 4 * 1300, yt], dl=[e, yt + 900], rotd=0, text='')
        add(t='mleader', h='BCEC4EDB', to=[e + 4 * 700, yt - 2400], arrow=[e + 4 * 700, yb1])
        add(t='clone', h='BCEE9DC1', d=[dx + 4 * 1000, dy, 0], text='Площадка\\\\Pлестницы')
""")
s = s.replace("""def sections70(sh):""", """STAIR = (12950, 36250, 18650, 39300)        # stair well Е-Ж / 35-36 (LIRA stiffness 40: flights 14450..16880, landing +7.000 16880..18650)
AB1 = dict(x0=16900, x1=18500, edge=36250)   # АВ-1 Ø14 @200 into the +7.000 landing (as analog Пм1 «выпуски для лестницы»)

def stair_ab(sh):
    a, b, e = AB1['x0'], AB1['x1'], AB1['edge']
    n = int((b - a) // 200) + 1; b = a + 200 * (n - 1)
    for x in (a, b): sh.line(x, e - 1200, x, e + 1300, layer='ф14_арм')
    sh.dim((a, e + 1300), (b, e + 1300), (a, e + 1650), text='200х%d' % (n - 1))
    sh.dim((a, e - 1200), (a, e), (a - 350, e - 1200), rot=90); sh.dim((a, e), (a, e + 1300), (a - 350, e), rot=90)
    add(t='mlx', h='BCEEA57E', text='АВ-1', textloc=sh.P((a + b) / 2, e + 700), arrows=[sh.P(a, e + 500), sh.P(b, e + 500)])
    add(t='clone', h=T['secmark'], to=sh.P((a + b) / 2, e), dyn={'Расстояние1': 1700, 'Расстояние2': 1700}, att={'В1': '6', 'В2': '6', 'Г1': '6', 'Г2': '6'})
    X0, Y0 = SH[(sh.k, sh.i)]['X0'], SH[(sh.k, sh.i)]['Y0']
    section(X0 + 70000, Y0 - 9000, 6, 400, 700, False, lo=5200, ro=5600, ab=True)
    SL[sh.k]['ab1'] = n

def sections70(sh):""")
s = s.replace("""        sh.dim((12650, 39300), (12950, 39300), (12650, 40300))""", """        sh.dim((12650, 39300), (12950, 39300), (12650, 40300))
        # stair well: outline + diagonal as the analog Пм1 opening
        a, b, c, d = STAIR
        sh.pl([(a, b), (c, b), (c, d), (a, d)], closed=True, layer='Plita', lw=50, color=7)
        sh.line(a, b, c, d, layer='Plita', lw=50, color=7)
        sh.dim((12950, 39300), (18650, 39300), (12950, 40300)); sh.dim((18650, 39300), (18650, 36250), (19350, 39300), rot=90)""")
s = s.replace("""            else: dop_sheet(sh, faces)""", """            else:
                dop_sheet(sh, faces)
                if k == 'P70' and faces == (2,): stair_ab(sh)""")
open('gen.py', 'w', encoding='utf-8').write(s)

p = open('spec.py', encoding='utf-8').read()
p = p.replace("""    npos = len(body)
    t1 = 't%s_1' % tag
    # 10 position rows in the analog table
    if npos > 10: add(t='edit', h=t1, insrows=[2, 2, npos - 10], cells=[])
    elif npos < 10: add(t='edit', h=t1, delrows=[2, 10 - npos], cells=[])
    add(t='edit', h=t1, delrows=[npos + 3, 1], cells=[])           # Х1 row""", """    npos = len(body)
    t1 = 't%s_1' % tag
    base = 8 if k == 'P70' else 10                                  # position rows in the analog table (Пм1 / Пм3)
    if npos > base: add(t='edit', h=t1, insrows=[2, 2, npos - base], cells=[])
    elif npos < base: add(t='edit', h=t1, delrows=[2, base - npos], cells=[])
    if k == 'P45': add(t='edit', h=t1, delrows=[npos + 3, 1], cells=[])      # Х1 row (no opening framing)""")
p = p.replace("""    cells += [[r, 10, str(nsk)], [r, 11, '0.44'], [r, 12, f2(sk)], [r + 1, 10, str(nf)], [r + 1, 11, '0.48'], [r + 1, 12, f2(ff)], [r + 3, 10, f2(conc)]]""", """    cells += [[r, 10, str(nsk)], [r, 11, '0.44'], [r, 12, f2(sk)], [r + 1, 10, str(nf)], [r + 1, 11, '0.48'], [r + 1, 12, f2(ff)]]
    if k == 'P70':
        nab = gen.SL[k].get('ab1', 9); ab = RHO[14] * 2.5 * nab
        steel[('A500', 14)] = steel.get(('A500', 14), 0) + ab; total = sum(steel.values())
        cells += [[r + 2, 9, '2500'], [r + 2, 10, str(nab)], [r + 2, 11, f2(RHO[14] * 2.5)], [r + 2, 12, f2(ab)], [r + 4, 10, f2(conc)], [0, 11, f2(total)]]
    else: cells += [[r + 3, 10, f2(conc)]]""")
p = p.replace("""        if kind == 'dop': gen.dop_sheet(gen.Sheet(k, i), faces)""", """        if kind == 'dop':
            gen.dop_sheet(gen.Sheet(k, i), faces)
            if k == 'P70' and faces == (2,): gen.stair_ab(gen.Sheet(k, i))""")
open('spec.py', 'w', encoding='utf-8').write(p)

a = open('asm.py', encoding='utf-8').read()
a = a.replace("from gen import SH, AN_R3, AN_R3Y, AN_R1, AN_R1Y, T, FR_A3", "from gen import SH, AN_R3, AN_R3Y, AN_R1, AN_R1Y, AN_R1S, T, FR_A3")
a = a.replace("      (AN_R1[3], AN_R1Y): 'BCEC4A5B'}", "      (AN_R1[3], AN_R1Y): 'BCEC4A5B', AN_R1S: 'BCEC43E1'}")
old = a[a.index("def spec_sheet("):a.index("# ---- Пм2 (+4.500)")]
new = '''TBL1 = ['BCEC4EB3', 'BCEC4EB4', 'BCEC4EB5']        # Пм1 spec (with Ав-1): steel summary, spec body, spec header
def spec_sheet(X0, Y0, tag, big):
    src = AN_R1S if big else (AN_R3[4], AN_R3Y); tbl = TBL1 if big else TBL3
    copy_sheet(src, (X0, Y0), (42000, 29700), skip=tbl)
    frame((X0, Y0), 'А2(594х420)' if big else 'А3(420х297)', 'fr' + tag)
    if not big: add(t='erasewin', win=W(X0 + 1900, Y0 - 9300, X0 + 8400, Y0 - 7150))     # Х1 row (no opening framing here)
    add(t='erasewin', win=W(X0 + 22500, Y0 - 16600, X0 + 41800, Y0 - 14500))            # border line under the analog table
    for j, h in enumerate(tbl): add(t='clone', h=h, d=[X0 - src[0], Y0 - src[1], 0], tag='t%s_%d' % (tag, j))
    if big:
        # A2 landscape: notes and stamp texts to the new stamp corner, steel summary down to the bottom edge
        add(t='movewin', win=W(X0 + 22000, Y0 - 29705, X0 + 42005, Y0 - 20500), d=[17400, -12300, 0],
            skip=['t%s_%d' % (tag, j) for j in range(3)] + ['fr' + tag])
        add(t='edit', h='t%s_0' % tag, d=[0, -12300, 0])
        add(t='edit', h='t%s_1' % tag, d=[-1500, 0, 0]); add(t='edit', h='t%s_2' % tag, d=[-1500, 0, 0])

'''
a = a.replace(old, new)
a = a.replace("""    pairs=[['Пм3 на отм. +4.500', 'Пм1 на отм. +7.000'], ['Пм-3 на отм. +4.500', 'Пм-1 на отм. +7.000'], ['Блок 2', 'Блок 4'], ['КЖ-3,4.', 'КЖ-3-6.']])""",
              """    pairs=[['Блок 2', 'Блок 4'], ['КЖ-3,4.', 'КЖ-3-6.']])""")
open('asm.py', 'w', encoding='utf-8').write(a)
print('ok')
