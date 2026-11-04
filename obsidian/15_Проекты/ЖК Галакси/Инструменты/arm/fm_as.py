import sys, pickle, csv, collections, json
sys.path.insert(0, '.')
import model as M
els, nodes = pickle.load(open('lira6/m.pkl', 'rb'))
# AS per element: max over rows of the element (two rows per element: design + check)
AS = {}
for r in csv.reader(open('arm/as_pl.csv', encoding='cp1251', errors='replace'), delimiter=';'):
    if len(r) < 12 or not r[4].strip().isdigit(): continue
    try: v = [float(x) for x in r[8:12]]
    except ValueError: continue
    e = int(r[4]); AS[e] = [max(a, b) for a, b in zip(AS.get(e, [0, 0, 0, 0]), v)]
cells = []
for i, r in enumerate(els):
    t, st = int(r[0]), int(r[1])
    if t not in (41, 42, 44) or st not in (6, 7): continue
    ns = [nodes[int(k) - 1] for k in r[2:]]
    if any(abs(n[2] + 4.65) > 1e-3 for n in ns): continue
    xs = [n[0] * 1000 for n in ns]; ys = [M.fy(n[1]) for n in ns]
    a = AS.get(i + 1)
    if a is None: continue
    cells.append(dict(id=i + 1, st=st, x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys), cx=sum(xs) / len(xs), cy=sum(ys) / len(ys), As=a))
print(len(cells), 'cells', collections.Counter(c['st'] for c in cells))
for k in range(4):
    v = sorted(c['As'][k] for c in cells)
    print('AS%d' % (k + 1), 'min', v[0], 'p50', v[len(v) // 2], 'p90', v[int(len(v) * .9)], 'p98', v[int(len(v) * .98)], 'max', v[-1])
json.dump(cells, open('arm/fm_cells.json', 'w'))
