s = open('gen.py', encoding='utf-8').read()

# 1) zones: clip by slab, then no two zones of one face share a bar position (stronger first), then 300 module
old = s[s.index("def split_by_slab(k):"):s.index("# ---------------- sheet placement")]
new = '''def split_by_slab(k):
    # every bar clipped to the slab (cover 30); a bar position belongs to one zone only (Bekassyl 04.11:
    # «2 түрлі доп арматура 1 жерге түсе алмайды») - stronger / larger zones take it first, weaker ones are cut around;
    # then bars with the same piece and step 200 form one zone, length down to the 300 module, centred in the piece
    gin = slab_geom(k).buffer(-30, join_style=2); out = []
    occ = defaultdict(list)                     # (face, pos) -> taken intervals
    order = sorted(Z[k], key=lambda z: (-z['d'], -len(z['pos']) * (z['L1'] - z['L0'])))
    for z in order:
        alongx = z['f'] in (0, 1); groups = defaultdict(list)
        for p in z['pos']:
            ln = LineString([(z['L0'] - 1, p), (z['L1'] + 1, p)]) if alongx else LineString([(p, z['L0'] - 1), (p, z['L1'] + 1)])
            for q in lines_of(ln.intersection(gin)):
                a, b = (q.bounds[0], q.bounds[2]) if alongx else (q.bounds[1], q.bounds[3])
                free = [(a, b)]
                for (u, v) in occ[(z['f'], p)]:
                    nxt = []
                    for (c, d) in free:
                        if v <= c or u >= d: nxt.append((c, d)); continue
                        if u - 50 > c: nxt.append((c, u - 50))
                        if v + 50 < d: nxt.append((v + 50, d))
                    free = nxt
                for (c, d) in free:
                    if d - c >= 1000: groups[(round(c), round(d))].append(p)
        for (a, b), ps in groups.items():
            ps.sort(); run = [ps[0]]
            for p in ps[1:] + [None]:
                if p is not None and p - run[-1] <= 201: run.append(p); continue
                Lr = int((b - a) // 300 * 300); a2 = math.ceil((a + (b - a - Lr) / 2) / 10.0) * 10
                out.append(dict(f=z['f'], d=z['d'], pos=run, n=len(run), L0=a2, L1=a2 + Lr, L=Lr))
                for q in run: occ[(z['f'], q)].append((a, b))
                if p is not None: run = [p]
    Z[k] = out

'''
s = s.replace(old, new)

# 2) contour 0.05 on reinforcement sheets; opening symbol as the user drew it (layer _0, 0.20) on every Пм1 sheet
old = """    lw = 50 if kind == 'opal' else 30
    for ring in [g.exterior] + list(g.interiors):
        sh.pl(list(ring.coords)[:-1], closed=True, layer='Plita', lw=lw, color=7)
    if kind == 'opal':
        for ring in g.interiors:
            xs = [p[0] for p in ring.coords]; ys = [p[1] for p in ring.coords]
            sh.line(min(xs), min(ys), max(xs), max(ys), layer='Plita', lw=lw, color=7)"""
new = """    lw = 50 if kind == 'opal' else 5            # Bekassyl 04.11: contour 0.05 where reinforcement is drawn
    for ring in [g.exterior] + list(g.interiors):
        sh.pl(list(ring.coords)[:-1], closed=True, layer='Plita', lw=lw, color=7)
    for ring in g.interiors:
        # opening mark copied from the user's own fix (Б4.плита1 v2, 04.11): corner -> kink near the top-left -> opposite corner
        xs = [p[0] for p in ring.coords]; ys = [p[1] for p in ring.coords]
        a, b, c, d = min(xs), min(ys), max(xs), max(ys)
        kx, ky = OPEN_KINK.get((round(c - a), round(d - b)), (0.15 * (c - a), 0.89 * (d - b)))
        sh.pl([(a, b), (a + kx, b + ky), (c, d)], layer='_0', lw=20)"""
assert old in s; s = s.replace(old, new)
s = s.replace("def background(sh, kind):", "OPEN_KINK = {(4600, 8900): (699, 7958), (2550, 5600): (576, 4837)}\n\ndef background(sh, kind):", 1)

# 3) stair well outline removed by the user - not drawn
old = """        # stair well: outline + diagonal as the analog Пм1 opening
        a, b, c, d = STAIR
        sh.pl([(a, b), (c, b), (c, d), (a, d)], closed=True, layer='Plita', lw=50, color=7)
        sh.line(a, b, c, d, layer='Plita', lw=50, color=7)
        sh.dim((12950, 39300), (18650, 39300), (12950, 40300)); sh.dim((18650, 39300), (18650, 36250), (19350, 39300), rot=90)
"""
assert old in s; s = s.replace(old, "")

# 4) rebar lines 0.40
s = s.replace("sh.line(a, b, c, d, layer='ф10_арм')", "sh.line(a, b, c, d, layer='ф10_арм', lw=40)")
s = s.replace("sh.line(L0, y, L1, y, layer=lay)", "sh.line(L0, y, L1, y, layer=lay, lw=40)")
s = s.replace("sh.line(x, L0, x, L1, layer=lay)", "sh.line(x, L0, x, L1, layer=lay, lw=40)")
s = s.replace("sh.line(x, e - 1200, x, e + 1300, layer='ф14_арм')", "sh.line(x, e - 1200, x, e + 1300, layer='ф14_арм', lw=40)")
open('gen.py', 'w', encoding='utf-8').write(s)

a = open('asm.py', encoding='utf-8').read()
a = a.replace("add(t='erasewin', win=W(X0 + 800, Y0 - 41800, X0 + 59000, Y0 - 2700))", "add(t='erasewin', win=W(X0 + 200, Y0 - 41800, X0 + 59000, Y0 - 2700))")
open('asm.py', 'w', encoding='utf-8').write(a)
print('ok', s.count("lw=40"))
