import sys, struct
sys.path.insert(0, r'D:\_claude_work\Kasymova')
from sub import load, heads, doc
L = load(r'D:\_claude_work\Kasymova\v9\v9_final.txt'); h = heads(L)
def entries(d):
    s = ' '.join(d[1:]).replace(')', ' ')
    return [e.split() for e in s.split('/') if e.strip()]
xyz = [tuple(map(float, e)) for e in entries(doc(L, h, 4))]
el = entries(doc(L, h, 1))
b1 = open(r'D:\_claude_work\Kasymova\Kasymova_v9.lir', 'rb').read()
N = len(xyz)
# verify node table
ok = all(struct.unpack_from('<ddd', b1, 138 + 28*k) == xyz[k] for k in range(0, N, 997))
print('node table ok', ok, 'extra 4 bytes of first nodes:', [b1[138+28*k+24:138+28*k+28].hex() for k in range(5)])
end = 138 + 28*N
print('node table end', end)
print(b1[end:end+200].hex(' '))
for pat in (struct.pack('<iiii', 1, 8964, 8285, 2),):
    i = b1.find(pat, end); print('el1 nodes int32 at', i)
    if i > 0:
        print(b1[i-40:i+80].hex(' '))
        e2 = struct.pack('<iiii', *map(int, el[1][2:6])); j = b1.find(e2, i); print('el2 at', j, 'stride', j-i)
