"""Compare generated text vs LIRA round-trip export: per-case load sums, counts, doc15/35/39."""
import sys, re, io, collections, math
sys.path.insert(0, sys.argv[3])
from lirparse import load
def summ(path):
    s, d, els, nodes, l6, l7 = load(path)
    tot = collections.defaultdict(float); cnt = collections.Counter(); kinds = collections.Counter()
    for e, kind, dr, row, case in l6:
        v = l7[row]
        if kind == 4: kinds[(case, e, v[0])] += 1; continue
        el = els[e - 1]; ns = [nodes[n - 1] for n in el[2:]]
        if kind == 16 and el[0] == 10: tot[case] += v[0] * math.dist(ns[0], ns[1])
        elif kind == 16: tot[case] += v[0] * abs(ns[3][0] - ns[0][0]) * abs(ns[3][1] - ns[0][1])
        elif kind == 15: tot[case] += v[0]
        elif kind == 19:
            a, b = ns[int(v[0]) - 1], ns[int(v[1]) - 1]; tot[case] += (v[2] + v[3]) / 2 * math.dist(a, b)
        cnt[(case, kind)] += 1
    return s, els, nodes, tot, cnt, kinds, d
A = summ(sys.argv[1]); B = summ(sys.argv[2])
print('elements', len(A[1]), len(B[1]), ' nodes', len(A[2]), len(B[2]))
print('types A', collections.Counter((e[0], e[1]) for e in A[1]))
print('types B', collections.Counter((e[0], e[1]) for e in B[1]))
for c in sorted(set(A[3]) | set(B[3])): print('case %2d  gen %9.3f  lira %9.3f' % (c, A[3][c], B[3][c]))
print('cnt diff', {k: (A[4][k], B[4][k]) for k in set(A[4]) | set(B[4]) if A[4][k] != B[4][k]})
print('mass A', sorted(A[5])); print('mass B', sorted(B[5]))
for key in ('35', '39'):
    m = re.search(r'\n%s;.*?/' % key, B[0], re.S); print(m.group(0) if m else 'no ' + key)
print('15:', B[6].get(15, 'NONE')[:400])
print('docs B', sorted(B[6]))
