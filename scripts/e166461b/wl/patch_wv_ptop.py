# wall_vert: PIECES0 entries may be None (piece merged into another basement piece), PTOP {piece: top level index}
p = 'wl/wall_vert.py'
s = open(p, encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:70], s.count(a)); s = s.replace(a, b)
rep("""    row = []
    for gi_, (g0, g1) in enumerate(G):
        if gi_ == 0 and CFG.get('PIECES0'):                            # basement pieces differ (e.g. a full wall below the openings)
            (la, lb), (el, er) = CFG['LIRA0'][i], CFG['ENDS0'][i]""", """    row = []
    for gi_, (g0, g1) in enumerate(G):
        if gi_ == len(G) - 1: g1 = TOP(i)
        if gi_ == 0 and CFG.get('PIECES0') and CFG['PIECES0'][i] is None: row.append(None); continue
        if gi_ == 0 and CFG.get('PIECES0'):                            # basement pieces differ (e.g. a full wall below the openings)
            (la, lb), (el, er) = CFG['LIRA0'][i], CFG['ENDS0'][i]""")
rep("""REQ = []
for i, ((a, b)""", """TOP = lambda i: CFG.get('PTOP', {}).get(i, G[-1][1])                    # top level index of piece i
REQ = []
for i, ((a, b)""")
rep("""    de = max([x for i in range(NP) for x in REQ[i][g][:2] if x] or [12])
    dm, sm = max([REQ[i][g][2:] for i in range(NP)], key=lambda t: (A(t[0]) * 1000 / t[1], -t[1]))
    for i, ((a, b), (el, er)) in enumerate(zip(PIECES, ENDS)):
        if g == 0 and CFG.get('PIECES0'): (a, b), (el, er) = CFG['PIECES0'][i], CFG['ENDS0'][i]""", """    de = max([x for i in range(NP) if REQ[i][g] for x in REQ[i][g][:2] if x] or [12])
    dm, sm = max([REQ[i][g][2:] for i in range(NP) if REQ[i][g]], key=lambda t: (A(t[0]) * 1000 / t[1], -t[1]))
    for i, ((a, b), (el, er)) in enumerate(zip(PIECES, ENDS)):
        if g == 0 and CFG.get('PIECES0') and CFG['PIECES0'][i] is None: D[i][g] = []; continue
        if g == 0 and CFG.get('PIECES0'): (a, b), (el, er) = CFG['PIECES0'][i], CFG['ENDS0'][i]""")
rep("""            for x in (z[1] - 20, z[2] + 20): VB.append((x, L[-1] - TOPC - LAP(z[3]), L[-1] - TOPC))""",
    """            for x in (z[1] - 20, z[2] + 20): VB.append((x, L[TOP(i)] - TOPC - LAP(z[3]), L[TOP(i)] - TOPC))""")
rep("""        yb, yt = L[g0], L[g1]
        DX = 20 * (gi % 2)
        for i in range(NP):
            for z in D[i][gi]:""", """        DX = 20 * (gi % 2)
        g1_ = g1
        for i in range(NP):
            g1 = TOP(i) if gi == len(G) - 1 else g1_
            yb, yt = L[g0], L[g1]
            for z in D[i][gi]:""")
rep("""                ys = L[g0] if (low and g1 - g0 > 1) else L[g1 - 1]; ye = (L[g0 + 1] if (low and g1 - g0 > 1) else L[g1]) - SLAB""",
    """                ys = L[g0] if (low and g1 - g0 > 1) else L[g1 - 1]; ye = (L[g0 + 1] if (low and g1 - g0 > 1) else L[g1]) - SLAB
                if ZM and ye - ys < 2400 and g1 - g0 > 1: ys, ye = L[g1 - 2], L[g1 - 1] - SLAB      # short top storey: notes one storey lower""")
rep("""            yt = L[-1] - TOPC; leg = LAP(d)""", """            yt = L[TOP(i)] - TOPC; leg = LAP(d)""")
rep("""        yy = SY + L[-1] - SLAB - 80          # analog Ск note""", """        LT = L[TOP(i)]
        yy = SY + LT - SLAB - 80          # analog Ск note""")
s = s.replace("SY + L[-1] + 450]", "SY + LT + 450]")
rep("""        else: a, b = (CFG.get('PIECES0') or PIECES)[i]
        segs""", """        else: a, b = (CFG.get('PIECES0') or PIECES)[i] or (None, None)
        if a is None: continue
        segs""")
open(p, 'w', encoding='utf-8').write(s)
print('patched')
