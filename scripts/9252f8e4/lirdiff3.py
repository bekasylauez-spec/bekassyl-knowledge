import json, collections
d = json.load(open('lirdiff2.json'))
print('deleted walls (v9 only):')
for kind, pts, n in sorted(d['onlyA'], key=lambda t: (min(p[2] for p in t[1]), t[1])):
    xs = sorted({p[0] for p in pts}); ys = sorted({p[1] for p in pts}); zs = sorted({p[2] for p in pts})
    print('  x', xs, 'y', ys, 'z', zs, 'x', n)
print('added bars (22:30 only) by level:')
g = collections.defaultdict(list)
for kind, pts, n in d['onlyB']:
    g[pts[0][2]].append((pts, n))
for z in sorted(g):
    segs = g[z]
    lines = collections.defaultdict(list)
    for pts, n in segs:
        (x1, y1, _), (x2, y2, _) = pts
        if abs(y1 - y2) < 1e-6: lines[('y=', y1)].append((min(x1, x2), max(x1, x2)))
        elif abs(x1 - x2) < 1e-6: lines[('x=', x1)].append((min(y1, y2), max(y1, y2)))
        else: lines[('diag',)].append(pts)
    desc = []
    for k, v in sorted(lines.items()):
        v.sort()
        if k[0] == 'diag': desc.append(f'diag {v}'); continue
        desc.append(f'{k[0]}{k[1]}: {v[0][0]}..{v[-1][1]} ({len(v)} seg, gaps {[ (a[1], b[0]) for a, b in zip(v, v[1:]) if abs(a[1]-b[0])>1e-6]})')
    print(f'  z={z}:', '; '.join(desc))
