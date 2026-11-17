import sys, struct, collections
sys.path.insert(0, r'D:\_claude_work\Kasymova')
from sub import load, heads, doc
L = load(r'D:\_claude_work\Kasymova\v9\v9_final.txt'); h = heads(L)
def entries(d):
    s = ' '.join(d[1:]).replace(')', ' ')
    return [e.split() for e in s.split('/') if e.strip()]
xyz = [tuple(map(float, e)) for e in entries(doc(L, h, 4))]
el = entries(doc(L, h, 1))
def parse(p):
    b = open(p, 'rb').read()
    nn = struct.unpack_from('<i', b, 98)[0]; ne = struct.unpack_from('<i', b, 106)[0]
    nodes = [struct.unpack_from('<ddd', b, 138 + 28*k) for k in range(nn)]
    nflag = [struct.unpack_from('<i', b, 138 + 28*k + 24)[0] for k in range(nn)]
    o = 138 + 28*nn
    els = []
    for k in range(ne):
        r = struct.unpack_from('<8ihi', b, o + 38*k)
        els.append((r[8], r[9], [n for n in r[:8]]))
    return nn, ne, nodes, nflag, els, o + 38*ne, b
nA, eA, ndA, nfA, elA, endA, bA = parse(r'D:\_claude_work\Kasymova\Kasymova_v9.lir')
print('A', nA, eA, 'end of elements', endA)
# validate A against text export
bad = 0
import sys as _s
for k, e in enumerate(el):
    ns = [int(x) - 1 for x in e[2:]]
    r = elA[k]
    if r[2][:len(ns)] != ns or int(e[1]) != r[1] or any(r[2][len(ns):]): bad += 1
print('A vs text: mismatching element records', bad, 'shorts', collections.Counter(r[0] for r in elA).most_common(5))
print('types in text', collections.Counter((e[0], len(e) - 2) for e in el).most_common(8))
for k in (0, 1, 2, 3, 100, 5000, 170000, 182319):
    print(k, el[k], elA[k])
