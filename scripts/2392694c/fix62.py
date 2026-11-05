import gx, os, math
import gen62 as G
OX, OY, SX1, SY1 = G.OX, G.OY, G.SX1, G.SY1
gx.run([{'t': 'list', 'win': [OX - 400, OY - 4000, OX + 23000, OY + 33500]}], 'ls')
top, right = [], []
for l in open(os.environ['TEMP'] + '/pl_log.txt', encoding='utf-8').read().splitlines():
    r = l.split('\t')
    if len(r) > 4 and r[0] == 'L' and r[1] == 'DIMENSION':
        e = [float(v) for v in r[4][1:].split(',')]
        if e[1] >= OY + SY1 - 10 and e[0] < OX + SX1 - 10: top.append(r[2])
        elif e[0] >= OX + SX1 - 10: right.append(r[2])
print(len(top), len(right))
new = G.place(G.chain(G.SX0, G.SX1, G.RX), False) + G.place(G.chain(G.SY0, G.SY1, G.RY), True)
for o in new:
    o['h'] = top[0] if o['rot'] == 0 else right[0]
    o.setdefault('txt', '')
ops = new + [{'t': 'erase', 'h': top + right}, {'t': 'save'}]
print([l for l in gx.run(ops, 'f62').splitlines() if 'ERR' in l or 'done' in l])
