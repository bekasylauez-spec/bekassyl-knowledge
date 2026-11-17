import struct, collections, json
def parse(p):
    b = open(p, 'rb').read()
    nn = struct.unpack_from('<i', b, 98)[0]; ne = struct.unpack_from('<i', b, 106)[0]
    nodes = [struct.unpack_from('<ddd', b, 138 + 28*k) for k in range(nn)]
    o = 138 + 28*nn
    els = [struct.unpack_from('<8ihi', b, o + 38*k) for k in range(ne)]
    return nodes, els
R = lambda v: round(v + 0.0, 3)
def keys(nodes, els):
    out = collections.Counter(); where = {}
    for i, r in enumerate(els):
        kind = r[8]; ns = r[:2] if kind == 0 else r[:4]
        pts = tuple(sorted(set(tuple(R(c) for c in nodes[n]) for n in ns)))
        k = (kind, pts); out[k] += 1; where.setdefault(k, i + 1)
    return out, where
nA, eA = parse(r'D:\_claude_work\Kasymova\Kasymova_v9.lir')
nB, eB = parse(r'D:\_claude_work\Kasymova\_old_versions\Kasymova_R_1611_2230.lir')
print('nodes', len(nA), len(nB), 'elements', len(eA), len(eB))
# node comparison
sA = collections.Counter(tuple(R(c) for c in p) for p in nA); sB = collections.Counter(tuple(R(c) for c in p) for p in nB)
print('nodes only in v9', sum((sA - sB).values()), ' only in 22:30', sum((sB - sA).values()))
print('first node index differing:', next((k for k in range(min(len(nA), len(nB))) if nA[k] != nB[k]), None))
kA, wA = keys(nA, eA); kB, wB = keys(nB, eB)
onlyA = kA - kB; onlyB = kB - kA
print('elements only in v9', sum(onlyA.values()), ' only in 22:30', sum(onlyB.values()))
def summ(c, tag):
    g = collections.Counter()
    for (kind, pts), n in c.items():
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; zs = [p[2] for p in pts]
        orient = 'bar' if kind == 0 else ('horiz' if max(zs) - min(zs) < 1e-6 else ('vert' if (max(xs)-min(xs) < 1e-6 or max(ys)-min(ys) < 1e-6) else 'incl'))
        g[(orient, round(min(zs), 3), round(max(zs), 3))] += n
    print(tag)
    for k, n in sorted(g.items(), key=lambda t: (t[0][1], t[0][0])): print('  ', k, n)
summ(onlyA, '--- only in v9 (deleted in 22:30)')
summ(onlyB, '--- only in 22:30 (added)')
json.dump({'onlyA': [[k[0], k[1], n] for k, n in onlyA.items()], 'onlyB': [[k[0], k[1], n] for k, n in onlyB.items()]}, open('lirdiff2.json', 'w'))
