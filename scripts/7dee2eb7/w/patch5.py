s = open('gen.py', encoding='utf-8').read()
old = "    gin = slab_geom(k).buffer(-30, join_style=2); out = []\n    occ = defaultdict(list)"
assert old in s
new = """    gin = slab_geom(k).buffer(-30, join_style=2); out = []
    premerge(k)
    occ = defaultdict(list)"""
s = s.replace(old, new)
s = s.replace("def split_by_slab(k):", '''def zrect(z):
    a, b = z['pos'][0] - 100, z['pos'][-1] + 100
    return box(z['L0'], a, z['L1'], b) if z['f'] in (0, 1) else box(a, z['L0'], b, z['L1'])

def premerge(k, small=10e6, grow=1.6):
    # small neighbouring zones of one face (any Ø) become one zone with the larger Ø when the envelope stays compact
    Zk = Z[k]; ch = True
    while ch:
        ch = False; best = None
        for i in range(len(Zk)):
            for j in range(i + 1, len(Zk)):
                p, q = Zk[i], Zk[j]
                if p['f'] != q['f']: continue
                rp, rq = zrect(p), zrect(q)
                if rp.area > small and rq.area > small: continue
                if rp.distance(rq) > 400: continue
                env = rp.union(rq).envelope
                r = env.area / max(rp.union(rq).area, 1)
                if r <= grow and (best is None or r < best[0]): best = (r, i, j, env)
        if best:
            _, i, j, env = best; p, q = Zk[i], Zk[j]
            x0, y0, x1, y1 = env.bounds
            if p['f'] in (0, 1): L0, L1, P0, P1 = x0, x1, y0, y1
            else: L0, L1, P0, P1 = y0, y1, x0, x1
            pos = [float(v) for v in range(int(P0 + 100), int(P1 - 100) + 1, 200)]
            Zk[i] = dict(f=p['f'], d=max(p['d'], q['d']), pos=pos, n=len(pos), L0=L0, L1=L1)
            Zk.pop(j); ch = True

def split_by_slab(k):''', 1)
open('gen.py', 'w', encoding='utf-8').write(s)
print('ok')
