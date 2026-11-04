# spec (now sheet 3.9): add shear positions 56.. (L=720, analog 25–27) to the body table and the steel summary
import json, gx
from collections import Counter
src = open('gen_fm3.py', encoding='utf-8').read(); src = src[:src.index('# ---- frame portrait')]
ns = {}; exec(src, ns)
items, KG, GOST = ns['items'], ns['KG'], ns['GOST']
Z = json.load(open('arm/fm_shear.json')); POS = {int(k): v for k, v in json.load(open('arm/fm_shear_pos.json')).items()}
c = Counter()
for z in Z: c[z['d']] += z['nx'] * z['ny']
sh = [(POS[d], d, '720', c[d], KG[d] * 0.72) for d in sorted(c)]
allit = items + sh
tot = sum(n * m for _, _, _, n, m in allit)
r0 = 1 + len(items)
ops = [{'t': 'trows', 'h': 'F0D7A', 'mode': 'ins', 'at': r0, 'from': r0 - 1, 'n': len(sh)}]
cells = [[0, 12, '%.2f' % tot]]
for i, (p, d, L, n, mu) in enumerate(sh):
    r = r0 + i
    cells += [[r, 0, p], [r, 1, 'ГОСТ 34028-2016(%s)' % GOST[d]], [r, 2, '%%C'], [r, 3, str(d)], [r, 4, 'A'], [r, 5, '500С'],
              [r, 8, 'L='], [r, 9, L], [r, 10, str(n)], [r, 11, '%.2f' % mu], [r, 12, '%.2f' % (n * mu)]]
ops.append({'t': 'tset', 'h': 'F0D7A', 'cells': cells})
by = {}
for p, d, L, n, mu in allit: by[d] = by.get(d, 0) + n * mu
DS = [10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
sc = [[6, 11, '%.1f' % tot], [6, 12, '%.1f' % tot]] + [[6, 1 + j, '%.1f' % by.get(d, 0)] for j, d in enumerate(DS)]
ops.append({'t': 'tset', 'h': 'F0D09', 'cells': sc})
json.dump(ops, open('ops/fm3c.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(len(sh), 'shear rows', round(tot), 'kg total')
