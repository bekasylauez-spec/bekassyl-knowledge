# -*- coding: utf-8 -*-
"""Независимая проверка otst.txt: парсит файл заново (док. 1,3,4,5,6,7,19), считает метрики и суммы нагрузок."""
import io, re, sys, math, collections, json
F = sys.argv[1]
t = io.open(F, encoding='utf-8-sig').read()
def doc(n):
    m = re.search(r'^\( %d/\n(.*?)\n ?\)' % n, t, re.S | re.M); return m.group(1)
els = []
for x in doc(1).split('/'):
    x = x.split()
    if x: els.append((int(x[0]), int(x[1]), [int(v) for v in x[2:]]))
nodes = [tuple(float(v) for v in x.split()) for x in doc(4).split('/') if x.strip()]
rows = {}
for l in doc(7).split('\n'):
    if l.strip():
        v = l.replace('/', ' ').split(); rows[int(v[0])] = [float(a) for a in v[1:]]
d6 = []
for x in doc(6).split('/'):
    x = x.split()
    if x: d6.append(tuple(int(v) for v in x))
sup = [int(x.split()[0]) for x in doc(5).split('/') if x.strip()]
wk = {int(x.split()[0]): float(x.split()[1]) for x in doc(19).split('/') if x.strip()}
stiff = {}
for l in doc(3).split('\n'):
    v = l.split()
    if v: stiff[int(v[0])] = (float(v[2]), float(v[3]), float(v[4]), float(v[6]))
names = re.findall(r'^(\d+): (.*?) ;$', t[t.index('39;'):t.index('42;')], re.M)
def P(n): return nodes[n - 1]
def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def nm(a): return math.sqrt(sum(x*x for x in a))
def dist(a, b): return nm(sub(a, b))
out = {}
out['nodes'] = len(nodes); out['elements'] = len(els)
out['types'] = dict(collections.Counter(e[0] for e in els))
out['bygroup'] = dict(collections.Counter(e[1] for e in els))
# duplicates
seen = collections.defaultdict(list)
for i, p in enumerate(nodes, 1): seen[tuple(round(v, 3) for v in p)].append(i)
dups = [v for v in seen.values() if len(v) > 1]
# fuzzy duplicates within 1e-3
import itertools
cells = collections.defaultdict(list)
for i, p in enumerate(nodes, 1): cells[tuple(int(math.floor(v / 0.01)) for v in p)].append(i)
fz = 0
for c, lst in cells.items():
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1): cand += cells.get((c[0]+dx, c[1]+dy, c[2]+dz), [])
    for a in lst:
        for b in cand:
            if a < b and dist(P(a), P(b)) < 1e-3: fz += 1
out['dup_nodes_exact3'] = len(dups); out['dup_nodes_lt1mm'] = fz
# geometry
G = {}
bad_area = []; bad_ratio = []; nonplanar = 0; ratios = []
for i, (tp, g, ns) in enumerate(els, 1):
    p = [P(n) for n in ns]
    if tp == 42:
        av = cross(sub(p[1], p[0]), sub(p[2], p[0])); A = 0.5 * nm(av)
        edges = [dist(p[0], p[1]), dist(p[1], p[2]), dist(p[2], p[0])]
        c = tuple(sum(q[k] for q in p) / 3 for k in range(3))
    else:
        av = cross(sub(p[3], p[0]), sub(p[2], p[1])); A = 0.5 * nm(av)
        edges = [dist(p[0], p[1]), dist(p[1], p[3]), dist(p[3], p[2]), dist(p[2], p[0])]
        def tri(a, b, cc):
            v = cross(sub(b, a), sub(cc, a)); return 0.5 * nm(v), tuple((a[k]+b[k]+cc[k])/3 for k in range(3))
        a1, c1 = tri(p[0], p[1], p[3]); a2, c2 = tri(p[0], p[3], p[2])
        c = tuple((a1*c1[k] + a2*c2[k]) / (a1 + a2) for k in range(3))
        # planarity: distance of p3 from plane(p0,p1,p2)
        n0 = cross(sub(p[1], p[0]), sub(p[2], p[0]))
        if nm(n0) > 0:
            dd = abs(sum(a*b for a, b in zip(sub(p[3], p[0]), n0))) / nm(n0)
            if dd > 2e-3: nonplanar += 1
    G[i] = (A, tuple(x / nm(av) for x in av) if nm(av) > 0 else (0, 0, 0), c)
    if A < 1e-9: bad_area.append(i)
    r = max(edges) / min(edges); ratios.append(r)
    if r > 4: bad_ratio.append((i, g, round(r, 2)))
out['zero_area'] = len(bad_area); out['nonplanar'] = nonplanar
out['ratio_max'] = max(ratios); out['ratio_gt4'] = len(bad_ratio)
bg = collections.Counter(b[1] for b in bad_ratio)
out['ratio_gt4_by_group'] = dict(bg)
out['ratio_gt4_max'] = max([b[2] for b in bad_ratio], default=0)
rb = collections.defaultdict(float)
for (i, g, r) in [(i + 1, els[i][1], ratios[i]) for i in range(len(els))]: rb[g] = max(rb[g], r)
out['ratio_max_by_group'] = {g: round(v, 2) for g, v in sorted(rb.items())}
# connectivity + edges
par = list(range(len(nodes) + 1))
def f(x):
    while par[x] != x: par[x] = par[par[x]]; x = par[x]
    return x
used = set()
edgecnt = collections.Counter()
for tp, g, ns in els:
    for n in ns: used.add(n)
    k = len(ns)
    per = ns if tp == 42 else [ns[0], ns[1], ns[3], ns[2]]
    for a, b in zip(per, per[1:] + per[:1]): edgecnt[(min(a, b), max(a, b))] += 1
    for n in ns[1:]: par[f(n)] = f(ns[0])
out['unused_nodes'] = len(nodes) - len(used)
out['components'] = len({f(n) for n in used})
mult = collections.Counter(edgecnt.values())
out['edge_mult'] = dict(mult)
# edge classes for non-manifold (>2) and free (==1)
def cls(a, b):
    pa, pb = P(a), P(b); r = (math.hypot(pa[0]-30, pa[1]) , math.hypot(pb[0]-30, pb[1]))
    return pa, pb
free = collections.Counter(); nonm = collections.Counter()
for (a, b), c in edgecnt.items():
    pa, pb = P(a), P(b)
    if pa[0] > 20: key = ('cam', round((pa[2]+pb[2])/2, 2))
    else:
        ra, rb_ = math.hypot(pa[0], pa[1]), math.hypot(pb[0], pb[1])
        key = ('bowl', round((ra+rb_)/2, 2) if abs(pa[2]-pb[2]) < 1e-6 else 'meridian', round((pa[2]+pb[2])/2, 2) if abs(pa[2]-pb[2]) < 1e-6 else '')
    if c == 1: free[key if key[0]=='bowl' and key[1] != 'meridian' else key[:1] + ('r' if key[0]=='bowl' else 'edge',)] += 1
    if c > 2: nonm[key] += 1
out['free_edges_total'] = sum(free.values())
# free edges at specific known places
fr = collections.Counter()
for (a, b), c in edgecnt.items():
    if c != 1: continue
    pa, pb = P(a), P(b)
    if pa[0] > 20:
        z = round((pa[2] + pb[2]) / 2, 2)
        fr[('cam', 'horiz z=%s' % z if abs(pa[2]-pb[2]) < 1e-6 else 'vert x=%.2f y=%.2f' % (pa[0]-30, pa[1]))] += 1
    else:
        ra, rb_ = math.hypot(pa[0], pa[1]), math.hypot(pb[0], pb[1])
        if abs(pa[2]-pb[2]) < 1e-6 and abs(ra-rb_) < 5e-3: fr[('bowl', 'circle R=%.3f z=%.3f' % ((ra+rb_)/2, pa[2]))] += 1
        else: fr[('bowl', 'other')] += 1
out['free_edge_classes'] = {'%s %s' % k: v for k, v in sorted(fr.items(), key=lambda kv: str(kv[0]))}
nmc = collections.Counter()
for (a, b), c in edgecnt.items():
    if c > 2:
        pa, pb = P(a), P(b)
        if pa[0] > 20: nmc['cam z=%.2f' % ((pa[2]+pb[2])/2)] += 1
        else:
            ra, rb_ = math.hypot(pa[0], pa[1]), math.hypot(pb[0], pb[1])
            nmc['bowl R=%.3f z=%.3f' % ((ra+rb_)/2, (pa[2]+pb[2])/2)] += 1
out['nonmanifold_classes'] = dict(nmc)
# ---- loads
sums = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
loads_by_case_kind = collections.Counter()
for e, kind, dr, rw, case in d6:
    v = rows[rw]
    if kind == 16:
        A = G[e][0]; sums[case][dr - 1] += -v[0] * A; loads_by_case_kind[(case, 16)] += 1
    elif kind == 0:
        sums[case][dr - 1] += -v[0]; loads_by_case_kind[(case, 0)] += 1
out['sums'] = {c: [round(x, 3) for x in s] for c, s in sorted(sums.items())}
mass_rows = [(e, rows[rw][0], case) for e, kind, dr, rw, case in d6 if kind == 4]
out['mass'] = mass_rows
# per-group area & mass
ga = collections.defaultdict(float)
for i, (tp, g, ns) in enumerate(els, 1): ga[g] += G[i][0]
out['group_area'] = {g: ga[g] for g in sorted(ga)}
out['stiff'] = stiff
out['n_support'] = len(sup); out['n_winkler'] = len(wk)
out['winkler_groups'] = dict(collections.Counter(els[e - 1][1] for e in wk))
out['winkler_C1'] = sorted(set(wk.values()))
out['names'] = names
out['doc_ids'] = re.findall(r'^\( (\d+)/', t, re.M)
out['load_counts'] = {'%d/%d' % k: v for k, v in sorted(loads_by_case_kind.items())}
out['rows'] = len(rows)
# element loaded by case 2 pressure min/max
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: out[k] for k in out if k not in ('mass', 'names')}, ensure_ascii=False, indent=1, default=str))
