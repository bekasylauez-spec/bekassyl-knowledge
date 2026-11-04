s = open('gen.py', encoding='utf-8').read()
a = s.index("def dop_sheet(sh, faces):"); b = s.index("# ---------------- spec ----------------")
new = '''CW, TH = 185, 250          # text char width / height at 1:100 (model mm)

def tbox(cx, cy, w, h): return box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)

def dop_sheet(sh, faces):
    # every annotation is placed at the free candidate: occupied = bars of all zones + texts placed so far
    s = SL[sh.k]; ax = [AXX[n] for n in s['ax']]; ay = [AXY[n] for n in s['ay']]; g = s['g']
    zs = [z for z in Z[sh.k] if z['f'] in faces]
    zs.sort(key=lambda z: (z['f'], -z['d'], z['pos'][0], z['L0']))
    occ = []
    for z in zs:
        a, b, L0, L1 = z['pos'][0], z['pos'][-1], z['L0'], z['L1']
        for q in sorted(set([a, b])):
            occ.append((LineString([(L0, q), (L1, q)]) if z['f'] in (0, 1) else LineString([(q, L0), (q, L1)])).buffer(60))
    def cost(geoms):
        c = 0
        for gm in geoms:
            for o in occ:
                if gm.intersects(o): c += gm.intersection(o).area + 1e5
            if not g.buffer(1500).contains(gm): c += 5e4
        return c
    def pick(cands):
        best = min(cands, key=lambda t: cost(t[0])); occ.extend(best[0]); return best[1]
    for z in zs:
        d = z['d']; L = z['L']; p = pos_of(sh.k, d, L); z['P'] = p; z['Lr'] = L
        lay = 'ф%d_арм' % d
        a, b, L0, L1 = z['pos'][0], z['pos'][-1], z['L0'], z['L1']
        n1 = len(z['pos']) - 1; st = '200х%d' % n1; Ls = str(int(round(L1 - L0)))
        X = z['f'] in (0, 1)
        if X:
            for y in sorted(set([a, b])): sh.line(L0, y, L1, y, layer=lay, lw=40)
        else:
            for x in sorted(set([a, b])): sh.line(x, L0, x, L1, layer=lay, lw=40)
        # length dim: below the first bar or above the last one
        c = []
        for side, off in (('lo', -350), ('hi', 350)):
            q = (a if side == 'lo' else b) + off
            bx = tbox((L0 + L1) / 2, q + 180, len(Ls) * CW, TH) if X else tbox(q - 180, (L0 + L1) / 2, TH, len(Ls) * CW)
            c.append(([bx, (LineString([(L0, q), (L1, q)]) if X else LineString([(q, L0), (q, L1)])).buffer(20)], q))
        q = pick(c)
        if X: sh.dim((L0, a if q < a else b), (L1, a if q < a else b), (L0, q))
        else: sh.dim((a if q < a else b, L0), (a if q < a else b, L1), (q, L0), rot=90)
        # spacing dim «200xN» at one end of the bars
        if b > a:
            c = []
            for e, off in ((L1, 350), (L0, -350)):
                q2 = e + off
                bx = tbox(q2 - 180, (a + b) / 2, TH, len(st) * CW) if X else tbox((a + b) / 2, q2 + 180, len(st) * CW, TH)
                c.append(([bx], (e, q2)))
            e, q2 = pick(c)
            if X: sh.dim((e, a), (e, b), (q2, a), rot=90, text=st)
            else: sh.dim((a, e), (b, e), (a, q2), text=st)
        # position mark (analog multileader) along the bars where it is free
        c = []
        for f in (0.35, 0.5, 0.2, 0.65, 0.8):
            m = L0 + (L1 - L0) * f
            if X: bx = tbox(m - 60, (a + b) / 2 if b > a else a + 400, TH + 100, len(str(p)) * CW + 100)
            else: bx = tbox((a + b) / 2 if b > a else a + 400, m + 300, len(str(p)) * CW + 100, TH + 100)
            c.append(([bx], m))
        m = pick(c)
        if X: sh.mark(str(p), (m, a), (m, b), True)
        else: sh.mark(str(p), (a, m), (b, m), False)
        # binding of the bar end to the nearest axis, only when free
        axs = ax if X else ay
        near = min(axs, key=lambda v: abs(v - L0))
        if 60 < abs(near - L0) < 4000 and g.boundary.distance(Point(L0, a) if X else Point(a, L0)) > 150:
            for q3 in ((a - 750, a), (b + 750, b)):
                txt = str(int(round(abs(near - L0))))
                bx = tbox((near + L0) / 2, q3[0] + 180, len(txt) * CW, TH) if X else tbox(q3[0] - 180, (near + L0) / 2, TH, len(txt) * CW)
                if cost([bx]) == 0:
                    occ.append(bx)
                    if X: sh.dim((near, q3[1]), (L0, q3[1]), (near, q3[0]))
                    else: sh.dim((q3[1], near), (q3[1], L0), (q3[0], near), rot=90)
                    break

'''
s = s[:a] + new + s[b:]
open('gen.py', 'w', encoding='utf-8').write(s)
print('ok')
