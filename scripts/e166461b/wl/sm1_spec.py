# См-1 specification (table 141248) and steel summary (1415ED) on the user's A3 sheet: input cells only, formulas kept/rewritten
import sys, json, math, collections; sys.path.insert(0, 'wl'); from common import *
SP, ST = '141248', '1415ED'
vj = json.load(open('wl/sm1_vert.json', encoding='utf-8')); hj = json.load(open('wl/sm1_hor.json', encoding='utf-8'))
GOST = {8: '214-210-0101-0002', 10: '214-210-0501-0005', 12: '214-210-0502-0001', 14: '214-210-0502-0002', 16: '214-210-0502-0003',
        18: '214-210-0502-0004', 20: '214-210-0502-0005', 22: '214-210-0502-0006', 25: '214-210-0502-0007'}
rows = []                                           # (pos, d, cls, L, count_formula)
ROWS_H = 115                                        # hoop rows over the height (analog: 115 per hoop position)
rows += [('Х1*', 8, '240', 930, '%d*2' % ROWS_H), ('Х2*', 8, '240', 980, '%d*12' % ROWS_H), ('Х3*', 8, '240', 830, '%d*4' % ROWS_H)]
cnt = collections.defaultdict(int); dl = {}
for b in vj['BARS']: cnt[str(b['pos'])] += b['n']; dl[str(b['pos'])] = (b['d'], b['L'])
for k in sorted([k for k in cnt if k.startswith('Ск')]): rows.append((k + '*', dl[k][0], '500С', dl[k][1], str(cnt[k])))
for k in sorted([k for k in cnt if not k.startswith('Ск')], key=int): rows.append((k, dl[k][0], '500С', dl[k][1], str(cnt[k])))
hc = collections.defaultdict(int); hd = {}
for b in hj['BARS']: hc[b['pos']] += b['n']; hd[b['pos']] = (b['d'], b['L'])
for k in sorted(hc): rows.append((str(k), hd[k][0], '500С', hd[k][1], str(hc[k])))
N0 = 3; have = 32                                   # analog body rows 3..34
ops = []
if len(rows) < have: ops.append(dict(t='trows', h=SP, mode='del', at=N0 + len(rows), n=have - len(rows)))
cells = []
for j, (p, d, cls, L, n) in enumerate(rows):
    r = N0 + j
    cells += [[r, 0, p], [r, 1, 'ГОСТ 34028-2016 (%s)' % GOST[d]], [r, 3, str(d)], [r, 5, cls], [r, 9, str(L)], [r, 10, n]]
ops.append(dict(t='tset', h=SP, cells=cells))
last = N0 + len(rows)                               # 0-based index of the first trailing row
fm = [[1, 12, 'Sum(M%d:M%d)' % (N0 + 1, last + 1)]]
# concrete: our pieces 1.10 + 1.85 + 1.85 + 1.10 m (analog 6.35 m -> 33.05 m3)
fm.append([last + 2, 12, '%.4f' % (33.0525 * 5.90 / 6.35)])
ops.append(dict(t='tformula', h=SP, cells=fm))
# steel summary: columns 4..9 = Ø12 Ø14 Ø16 Ø18 Ø20 Ø25 (A500С), 2 = Ø8 (A240)
COLS = {12: 4, 14: 5, 16: 6, 18: 7, 20: 8, 25: 9}
hdr = [[5, c, '%%%%C%d' % d] for d, c in COLS.items()]
ops.append(dict(t='tset', h=ST, cells=hdr))
byd = collections.defaultdict(list)
for j, row in enumerate(rows): byd[row[1]].append(N0 + j + 1)
def ev(lst): return '+'.join('Table({T:%s}).Evaluate(Sum(M%d:M%d))' % (SP, a, a) for a in lst) if lst else '0'
sf = [[6, 2, ev(byd[8])]]
for d, c in COLS.items(): sf.append([6, c, ev(byd[d])])
missing = [d for d in byd if d not in COLS and d != 8]
ops.append(dict(t='tformula', h=ST, cells=sf))
ops.append(dict(t='save'))
print(len(rows), 'rows; Ø not in summary:', missing)
for r in rows: print(r)
if '--run' in sys.argv:
    out = gx.run(ops, 'sm1spec'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
