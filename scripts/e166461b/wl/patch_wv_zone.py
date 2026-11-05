p = 'wl/wall_vert.py'
s = open(p, encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:80], s.count(a)); s = s.replace(a, b)
rep("""        D[i][g] = make_zones(a, b, el, er, de, de, dm, sm)
""", """        D[i][g] = make_zones(a, b, el, er, de, de, dm, sm)
        if g == 0 and CFG.get('ONE0'): D[i][g] = make_zones(CFG['ONE0'][0], CFG['ONE0'][1], False, False, de, de, dm, sm) if i == 0 else []
""")
rep("""        for z in D[i][g]:
            if z[0] == kind: return z
        return max(D[i][g], key=lambda z: z[3])""", """        for z in (D[i][g] or D[0][g]):
            if z[0] == kind: return z
        return max(D[i][g] or D[0][g], key=lambda z: z[3])""")
rep("""    R = listwin(SX, SY, 59400, 42000, None)
    N = notes(SX, SY, 59400, 42000)""", """    WW, HH = CFG.get('WH', (59400, 42000))
    R = listwin(SX, SY, WW, HH, None)
    N = notes(SX, SY, WW, HH)""")
rep("""                ops.append(dict(t='pl', p=[W(AX1 + x0 + DX, bA), W(AX1 + x0 + DX, tA)], layer=lay, lw=40))
                ops.append(dict(t='pl', p=[W(AX1 + x1 + DX, bB), W(AX1 + x1 + DX, tB)], layer=lay, lw=40))""", """                ops.append(dict(t='pl', p=[W(AX1 + x0 + DX, bA), W(AX1 + x0 + DX, tA)], layer=lay, lw=40))
                ops.append(dict(t='pl', p=[W(AX1 + x1 + DX, bB), W(AX1 + x1 + DX, tB)], layer=lay, lw=40))
                VB.append((x0 + DX, bA, tA)); VB.append((x1 + DX, bB, tB))""")
rep("""                else:
                    note('S1N', '%s(%%%%C%d)' % (lab, d), 'ш.%d' % st, [SX + ox, SY + ym], [[SX + AX1 + x0 + DX, SY + ym], [SX + AX1 + x1 + DX, SY + ym]])""", """                elif ZM:
                    ZQ.append(dict(i=i, kind=kind, x0=x0 + DX, x1=x1 + DX, l1='%s(%%%%C%d)' % (lab, d), l2='ш.%d' % st, ys=ys, ye=ye))
                else:
                    note('S1N', '%s(%%%%C%d)' % (lab, d), 'ш.%d' % st, [SX + ox, SY + ym], [[SX + AX1 + x0 + DX, SY + ym], [SX + AX1 + x1 + DX, SY + ym]])
            if ZM and i == NP - 1:
                place_zone_notes(gi, ZQ); ZQ.clear()""")
rep("""                lp = max(lap_at(i, gi, z[0]) for z in D[i][gi]); gp = GAP(lp)
                xa = AX1 + min(z[1] for z in D[i][0]) + DX; xd = AX1 + CFG['CHAIN_X'][i] - 350""", """                lp = max(lap_at(i, gi, z[0]) for z in (D[i][gi] or D[0][gi])); gp = GAP(lp)
                xa = AX1 + min(z[1] for z in D[i][0]) + DX if D[i][0] else None; xd = AX1 + CFG['CHAIN_X'][i] - 350
                if ZM or xa is None:                      # extension lines from the piece's bars that start at this splice
                    csd_ = CFG.get('CHAIN_SIDE', 'L' * NP)[i]; DX1 = 20 * ((gi + 1) % 2)
                    xa = AX1 + DX1 + (min(z[1] for z in D[i][gi + 1]) if csd_ == 'L' else max(z[2] for z in D[i][gi + 1]))
                    if csd_ == 'R': xd = AX1 + PIECES[i][1] + 350""")
rep("""    for i in range(NP):
        a, b = (CFG.get('PIECES0') or PIECES)[i]
        segs""", """    for i in range(NP):
        if CFG.get('ONE0'):
            if i: continue
            a, b = CFG['ONE0']
        else: a, b = (CFG.get('PIECES0') or PIECES)[i]
        segs""")
rep("""    CH = []
""", """    CH = []
    ZM = CFG.get('NOTE_MODE') == 'zone'; ZQ = []; VB = []; PT = []      # PT: placed text boxes / shelves (wall x, sheet-rel y)
    DG = [[(p[0] - AX1, p[1]) for p in r['sp']] for r in R if r['t'] == 'LWPOLYLINE' and len(r['sp']) == 3 and r['y0'] > L[0] - 1100]
    AXR = [a_ - AX1 for a_ in CFG['AXES']]
    for i in range(NP):                                                  # Ск legs at the top (drawn later): obstacles for the notes
        for z in D[i][3]:
            for x in (z[1] - 20, z[2] + 20): VB.append((x, L[-1] - TOPC - LAP(z[3]), L[-1] - TOPC))
    def segx(p, q, y):                                                   # x where segment p-q crosses height y (or None)
        if (p[1] - y) * (q[1] - y) > 0 or p[1] == q[1]: return None
        return p[0] + (y - p[1]) / (q[1] - p[1]) * (q[0] - p[0])
    def box_hits_diag(bx0, by0, bx1, by1):
        for pl in DG:
            for p, q in zip(pl, pl[1:]):
                for k in range(21):                                       # sample the segment
                    x = p[0] + (q[0] - p[0]) * k / 20.0; y = p[1] + (q[1] - p[1]) * k / 20.0
                    if bx0 <= x <= bx1 and by0 <= y <= by1: return True
                for yy_ in (by0, by1):
                    x = segx(p, q, yy_)
                    if x is not None and bx0 <= x <= bx1: return True
        return False
    def place_zone_notes(gi, Q):
        if gi == 0 and CFG.get('ONE0'): EDGES = [CFG['ONE0'][0] - 50, CFG['ONE0'][1] + 50]
        else: EDGES = [v_ for ab in PIECES for v_ in ab]
        VL = EDGES + CFG.get('VLINES', [])
        XLIM = CFG.get('XLIM', (-1e9, 1e9))
        for q in sorted(Q, key=lambda q: (q['kind'] == 'M', q['x0'])):
            w = 190 * max(len(q['l1'].replace('%%%%C', 'D')), len(q['l2'])) + 150
            ys, ye = q['ys'], q['ye']; ypref = ys + 0.55 * (ye - ys)
            best = None
            cands = [(q['x0'], 'R')] + [(q['x0'] + 100 * k, 'R') for k in range(1, int((q['x1'] - q['x0']) / 100) + 31)] + [(q['x0'] - 100 * k, 'L') for k in range(1, 31)]
            for ox, sd in cands:
                tx0, tx1 = (ox, ox + w) if sd == 'R' else (ox - w, ox)
                if tx0 < XLIM[0] or tx1 > XLIM[1]: continue
                sx0, sx1 = min(ox, q['x0']), max(ox, q['x1'])
                for y in range(int(ys + 450), int(ye - 449), 50):
                    by0, by1 = y - 350, y + 350
                    if any(tx0 - 60 < x_ < tx1 + 60 and b0 < by1 and t0 > by0 for x_, b0, t0 in VB): continue
                    if any(tx0 - 60 < x_ < tx1 + 60 for x_ in VL + AXR): continue
                    if box_hits_diag(tx0 - 50, by0 - 30, tx1 + 50, by1 + 30) or box_hits_diag(sx0, y - 5, sx1, y + 5): continue
                    bad = False
                    for (a0, b0, a1, b1, sy0, sy1, yy0) in PT:
                        if a0 < tx1 + 80 and tx0 - 80 < a1 and b0 < by1 + 80 and by0 - 80 < b1: bad = True; break     # text / text
                        if sy0 < tx1 and tx0 < sy1 and by0 - 30 < yy0 < by1 + 30: bad = True; break                   # other shelf through my text
                        if sx0 < a1 and a0 < sx1 and b0 - 30 < y < b1 + 30: bad = True; break                         # my shelf through other text
                    if bad: continue
                    ext = max(0, q['x0'] - sx0) + max(0, sx1 - q['x1'])
                    cr = sum(1 for x_ in AXR if sx0 < x_ < sx1) * 3000 + sum(1 for x_ in VL if sx0 + 1 < x_ < sx1 - 1) * 1500
                    cr += sum(800 for x_, b0, t0 in VB if sx0 + 5 < x_ < sx1 - 5 and b0 < y < t0 and x_ not in (q['x0'], q['x1']))
                    c = ext + cr + 0.3 * abs(y - ypref)
                    if best is None or c < best[0]: best = (c, ox, sd, y, tx0, tx1, sx0, sx1)
            if best is None:
                print('NO PLACE', gi, q['i'], q['kind'], q['l1']); continue
            c, ox, sd, y, tx0, tx1, sx0, sx1 = best
            PT.append((tx0, y - 350, tx1, y + 350, sx0, sx1, y))
            note('S1N', q['l1'], q['l2'], [SX + AX1 + ox, SY + y], [[SX + AX1 + q['x0'], SY + y], [SX + AX1 + q['x1'], SY + y]])
            print('note', gi, q['i'], q['kind'], q['l1'], 'org', round(ox), sd, 'y', y, 'cost', round(c))
""")
open(p, 'w', encoding='utf-8').write(s)
print('patched')
