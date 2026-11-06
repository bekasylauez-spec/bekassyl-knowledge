# Маслоподготовка Блок 2: LIRA beam elements -> runs (straight chains) -> supports -> marks (same geometry + section = one mark)
# units: mm, LIRA plan coordinates (x_L = axis - 1200, y_L = axis - 1350)
import pickle, json, math, collections, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
els, nodes, stf = pickle.load(open(os.path.join(HERE, 'm2.pkl'), 'rb'))
AS = None
LEVEL = {-0.05: '-0.050', 4.0: '+4.000', 4.8: '+4.800', 6.95: '+6.950', 10.5: '+10.500'}
# axes in LIRA mm
AXX = {53850: '9', 62950: '10', 72450: '11', 78450: '12', 85050: '13'}
AXY = {-1350: 'А', 5650: 'Б', 9150: 'В', 14150: 'Г', 15150: 'Д', 19650: 'Е', 20650: 'Ж', 26650: 'И', 27650: 'К'}
LEVELS = sorted(LEVEL)


def sec(s):
    m = re.search(r'S0 \S+ (\S+) (\S+)', stf[s])
    return (int(float(m.group(1)) * 10), int(float(m.group(2)) * 10)) if m else None


def P(i): n = nodes[i - 1]; return (round(n[0] * 1000), round(n[1] * 1000), round(n[2], 3))


# ---------------------------------------------------------------- elements
beams = []      # (z, (b,h), p1, p2, elem)
cols = []       # (x, y, zmin, zmax, (b,h))
for i, (ty, s, ns) in enumerate(els, 1):
    if ty != 10 or len(ns) != 2: continue
    bh = sec(s)
    if not bh: continue
    a, b = P(ns[0]), P(ns[1])
    if abs(a[2] - b[2]) < 0.005:
        beams.append((round(a[2], 2), bh, a[:2], b[:2], i))
    elif a[0] == b[0] and a[1] == b[1]:
        cols.append((a[0], a[1], min(a[2], b[2]), max(a[2], b[2]), bh))


SCHEME_SHIFT = {   # LIRA column centre -> scheme column centre (edge columns sit off the axis in LIRA)
    ('x', 53450, 'big'): 53649, ('x', 85450, 'big'): 85250, ('x', 53450, 'sm'): 53550, ('x', 85450, 'sm'): 85350,
    ('y', -1350, 'big'): -950, ('y', 27650, 'big'): 27275}


def col_rect(c):
    x, y, _, _, (b, h) = c
    kind = 'big' if (b, h) == (1300, 900) else 'sm'
    x = SCHEME_SHIFT.get(('x', x, kind), x); y = SCHEME_SHIFT.get(('y', y, kind), y)
    if (b, h) == (1300, 900): w, d = 900, 1300        # scheme: 900 along X, 1300 along Y
    else: w, d = b, h
    return (x - w / 2.0, y - d / 2.0, x + w / 2.0, y + d / 2.0)


def cols_at(z):
    out = {}
    for c in cols:
        if c[2] - 0.01 <= z <= c[3] + 0.01:
            r = col_rect(c); k = (c[0], c[1])
            if k in out:   # column below and above: take the larger outline
                o = out[k]; r = (min(o[0], r[0]), min(o[1], r[1]), max(o[2], r[2]), max(o[3], r[3]))
            out[k] = r
    return list(out.values())


# ---------------------------------------------------------------- runs (chains of collinear elements)
def unit(p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); return (dx / L, dy / L)


def runs():
    by = collections.defaultdict(list)
    for z, bh, p, q, e in beams: by[(z, bh)].append((p, q, e))
    out = []
    for (z, bh), segs in by.items():
        segs = [(p, q, e) if (q[0], q[1]) >= (p[0], p[1]) else (q, p, e) for p, q, e in segs]
        used = set()
        for i, (p, q, e) in enumerate(segs):
            if i in used: continue
            u = unit(p, q)
            chain = [(p, q, e)]; used.add(i)
            grow = True
            while grow:
                grow = False
                for j, (p2, q2, e2) in enumerate(segs):
                    if j in used: continue
                    u2 = unit(p2, q2)
                    if abs(u[0] * u2[1] - u[1] * u2[0]) > 0.02: continue
                    if p2 == chain[-1][1]: chain.append((p2, q2, e2)); used.add(j); grow = True
                    elif q2 == chain[0][0]: chain.insert(0, (p2, q2, e2)); used.add(j); grow = True
            A, B = chain[0][0], chain[-1][1]
            d = 'X' if A[1] == B[1] else 'Y' if A[0] == B[0] else 'D'
            out.append(dict(z=z, b=bh[0], h=bh[1], A=A, B=B, dir=d, L=math.hypot(B[0] - A[0], B[1] - A[1]),
                            els=[c[2] for c in chain]))
    return out


def seg_hit_rect(A, B, r, tol=1.0):
    """parameter interval [t0,t1] (mm along A->B) where the centre line is inside rectangle r, or None"""
    L = math.hypot(B[0] - A[0], B[1] - A[1]); ux, uy = (B[0] - A[0]) / L, (B[1] - A[1]) / L
    t0, t1 = -1e9, 1e9
    for p, u, lo, hi in ((A[0], ux, r[0] - tol, r[2] + tol), (A[1], uy, r[1] - tol, r[3] + tol)):
        if abs(u) < 1e-9:
            if not (lo <= p <= hi): return None
        else:
            a, b = (lo - p) / u, (hi - p) / u
            t0, t1 = max(t0, min(a, b)), min(t1, max(a, b))
    if t0 > t1 or t1 < -600 or t0 > L + 600: return None
    return (t0, t1)


def inter(A, B, C, D):
    """parameter t along A->B (mm) of the intersection with segment C-D, or None"""
    r = (B[0] - A[0], B[1] - A[1]); s = (D[0] - C[0], D[1] - C[1])
    den = r[0] * s[1] - r[1] * s[0]
    if abs(den) < 1e-9: return None
    t = ((C[0] - A[0]) * s[1] - (C[1] - A[1]) * s[0]) / den
    v = ((C[0] - A[0]) * r[1] - (C[1] - A[1]) * r[0]) / den
    if -0.002 <= t <= 1.002 and -0.002 <= v <= 1.002: return t * math.hypot(*r)
    return None


def supports(r, allruns):
    A, B, L = r['A'], r['B'], r['L']
    sup = []
    for c in cols_at(r['z']):
        h = seg_hit_rect(A, B, c)
        if h: sup.append((h[0], h[1], 'col'))
    for o in allruns:
        if o is r or o['z'] != r['z']: continue
        t = inter(A, B, o['A'], o['B'])
        if t is None: continue
        if any(a - 5 <= t <= b + 5 for a, b, _ in sup): continue
        if o['h'] >= r['h'] or t < 5 or t > L - 5:
            # crossing beam carries this one if not lower; at the run ends any beam is the support
            # width along this run: o.b / sin(angle)
            ua = ((B[0] - A[0]) / L, (B[1] - A[1]) / L); ub = ((o['B'][0] - o['A'][0]) / o['L'], (o['B'][1] - o['A'][1]) / o['L'])
            sn = abs(ua[0] * ub[1] - ua[1] * ub[0]); w = o['b'] / max(sn, 0.2)
            sup.append((t - w / 2.0, t + w / 2.0, 'beam'))
    return sorted(set((round(a), round(b), k) for a, b, k in sup))


def build():
    rr = runs()
    for r in rr:
        sp = supports(r, rr)
        E0, E1 = 0.0, r['L']
        if sp and sp[0][0] <= 5: E0 = min(0.0, sp[0][0])
        if sp and sp[-1][1] >= r['L'] - 5: E1 = max(r['L'], sp[-1][1])
        r.update(E0=E0, E1=E1, sups=sp)
    return rr


def axname(r, t):
    """axis label of a point at t along the run, else ''"""
    x = r['A'][0] + (r['B'][0] - r['A'][0]) * t / r['L']; y = r['A'][1] + (r['B'][1] - r['A'][1]) * t / r['L']
    if r['dir'] == 'X':
        for k, v in AXX.items():
            if abs(k - x) <= 450: return v
    if r['dir'] == 'Y':
        for k, v in AXY.items():
            if abs(k - y) <= 50: return v
    return ''


def where(r):
    if r['dir'] == 'X':
        c = r['A'][1]; ln = AXY.get(c) or ('%.2f' % ((c + 1350) / 1000.0))
        return 'ось %s' % ln if c in AXY else 'y=%s' % ln
    if r['dir'] == 'Y':
        c = r['A'][0]; ln = [v for k, v in AXX.items() if abs(k - c) <= 450]
        return 'ось %s' % ln[0] if ln else 'x=%.2f' % ((c + 1200) / 1000.0)
    return 'диаг.'


def sig(r):
    rel = tuple((round(a - r['E0']), round(b - r['E0']), k) for a, b, k in r['sups'])
    return (r['z'], r['b'], r['h'], round(r['E1'] - r['E0']), rel)


def sig_rev(r):
    E = r['E1'] - r['E0']
    rel = tuple(sorted((round(E - (b - r['E0'])), round(E - (a - r['E0'])), k) for a, b, k in r['sups']))
    return (r['z'], r['b'], r['h'], round(E), rel)


if __name__ == '__main__':
    rr = build()
    g = collections.OrderedDict()
    for r in sorted(rr, key=lambda r: (r['z'], -r['h'], -r['b'], r['dir'], -r['L'], r['A'][1], r['A'][0])):
        s = sig(r); s2 = sig_rev(r)
        if s in g: g[s].append((r, False))
        elif s2 in g: g[s2].append((r, True))
        else: g[s] = [(r, False)]
    print(len(rr), 'runs', len(g), 'groups')
    for s, rs in g.items():
        r = rs[0][0]
        print(LEVEL[r['z']], '%dx%d' % (r['b'], r['h']), r['dir'], 'L=%d' % (r['E1'] - r['E0']), 'sups', ''.join('c' if k == 'col' else 'b' for _, _, k in r['sups']),
              'n=%d' % len(rs), '|', '; '.join(where(x) + ('↔' if rev else '') for x, rev in rs))
    pickle.dump((rr, list(g.items())), open(os.path.join(HERE, 'groups.pkl'), 'wb'))
