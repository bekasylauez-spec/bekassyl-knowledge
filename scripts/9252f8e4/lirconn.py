import struct, collections
def parse(p):
    b = open(p, 'rb').read()
    nn = struct.unpack_from('<i', b, 98)[0]; ne = struct.unpack_from('<i', b, 106)[0]
    nodes = [struct.unpack_from('<ddd', b, 138 + 28*k) for k in range(nn)]
    o = 138 + 28*nn
    els = [struct.unpack_from('<8ihi', b, o + 38*k) for k in range(ne)]
    return nodes, els
R = lambda v: round(v + 0.0, 3)
nB, eB = parse(r'D:\_claude_work\Kasymova\_old_versions\Kasymova_R_1611_2230.lir')
nA, eA = parse(r'D:\_claude_work\Kasymova\Kasymova_v9.lir')
setA = set(tuple(R(c) for c in p) for p in nA)
inc = collections.defaultdict(list)
for i, r in enumerate(eB):
    ns = r[:2] if r[8] == 0 else r[:4]
    for n in set(ns): inc[n].append(i)
new_bars = []
for i, r in enumerate(eB):
    if r[8] != 0: continue
    p1, p2 = nB[r[0]], nB[r[1]]
    if (abs(p1[0]-51) < 1e-6 and abs(p2[0]-51) < 1e-6 and 5 - 1e-6 <= min(p1[1], p2[1]) and max(p1[1], p2[1]) <= 12 + 1e-6) or (abs(p1[1]-34) < 1e-6 and abs(p2[1]-34) < 1e-6 and abs(p1[2]-4.1) < 1e-6 and 29.2 < min(p1[0], p2[0]) and max(p1[0], p2[0]) < 34.8) or (abs(p1[0]-32) < 1e-6 and abs(p2[0]-32) < 1e-6 and abs(p1[2]-4.1)<1e-6 and min(p1[1],p2[1]) >= 34-1e-6 and max(p1[1],p2[1]) <= 34.5+1e-6):
        new_bars.append(i)
print('candidate bars', len(new_bars))
# per level for x=51 chain: list nodes y, whether node is new, and what else it connects to
lv = collections.defaultdict(set)
for i in new_bars:
    for n in eB[i][:2]: lv[R(nB[n][2])].add(n)
for z in sorted(lv):
    rows = []
    for n in sorted(lv[z], key=lambda n: (nB[n][0], nB[n][1])):
        others = [j for j in inc[n] if j not in new_bars]
        kinds = collections.Counter('bar' if eB[j][8] == 0 else 'pl' for j in others)
        new = tuple(R(c) for c in nB[n]) not in setA
        rows.append(f"({R(nB[n][0])},{R(nB[n][1])}){'*' if new else ''}:{dict(kinds)}")
    print(z, ' '.join(rows))
