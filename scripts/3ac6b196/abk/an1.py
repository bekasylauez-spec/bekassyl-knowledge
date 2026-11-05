import sys, collections
sys.path.insert(0, sys.argv[2])
from lirparse import load
s, d, els, nodes, l6, l7 = load(sys.argv[1])
print('elements', len(els), 'nodes', len(nodes))
print('types', collections.Counter((e[0], e[1]) for e in els))
zs = collections.Counter(round(n[2], 3) for n in nodes); print('Z levels', sorted(zs.items()))
xs = sorted(set(round(n[0], 2) for n in nodes)); ys = sorted(set(round(n[1], 2) for n in nodes))
print('X range', xs[0], xs[-1], len(xs), 'Y range', ys[0], ys[-1], len(ys))
# per load case summary
agg = collections.defaultdict(lambda: collections.Counter())
for e, kind, dr, row, case in l6:
    el = els[e - 1]
    zc = sum(nodes[n - 1][2] for n in el[2:]) / len(el[2:])
    agg[case][(kind, dr, tuple(l7[row]), el[0], el[1], round(zc, 2))] += 1
for c in sorted(agg):
    print('=== case', c)
    for k, v in sorted(agg[c].items()):
        print('   kind %s dir %s val %s  KE %s stiff %s z=%s  : %d' % (k + (v,)))
