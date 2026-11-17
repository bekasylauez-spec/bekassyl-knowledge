import sys, struct
sys.path.insert(0, r'D:\_claude_work\Kasymova')
from sub import load, heads, doc
L = load(r'D:\_claude_work\Kasymova\v9\v9_final.txt'); h = heads(L)
def entries(d):
    s = ' '.join(d[1:]).replace(')', ' ')
    return [e.split() for e in s.split('/') if e.strip()]
xyz = [tuple(map(float, e)) for e in entries(doc(L, h, 4))]
el = entries(doc(L, h, 1))
print('nodes', len(xyz), 'elements', len(el))
print('n1..3', xyz[:3]); print('e1..3', el[:3])
b1 = open(r'D:\_claude_work\Kasymova\Kasymova_v9.lir', 'rb').read()
for fmt in ('<ddd', '<fff'):
    pat = struct.pack(fmt, *xyz[0])
    i = b1.find(pat)
    print(fmt, 'node1 at', i)
    if i >= 0:
        pat2 = struct.pack(fmt, *xyz[1]); j = b1.find(pat2, i)
        print('  node2 at', j, 'stride', j - i)
# also just x of node1 as double
i = b1.find(struct.pack('<d', xyz[0][0])); print('x1 double at', i)
