# Фм-1 sheet 3.8: specification (analog tables: header F110D, body F0D7A, steel summary F0D09, details F1125)
import json, math, sys
sys.path.insert(0, '.')
import model as M

ops = []
def add(**k): ops.append(k); return k
KG = {8: 0.395, 10: 0.617, 12: 0.888, 14: 1.208, 16: 1.578, 18: 1.998, 20: 2.466, 22: 2.984, 25: 3.853, 28: 4.834, 32: 6.313}
GOST = {10: '214-210-0501-0005', 12: '214-210-0502-0001', 14: '214-210-0502-0002', 16: '214-210-0502-0003', 18: '214-210-0502-0004',
        20: '214-210-0502-0005', 22: '214-210-0502-0006', 25: '214-210-0502-0007', 28: '214-210-0502-0008', 32: '214-210-0502-0009'}
HDR, BODY, STEEL, DET = 'F110D', 'F0D7A', 'F0D09', 'F1125'
FX0, FY0, FX1, FY1 = M.FM
W, H = FX1 - FX0, FY1 - FY0
LAP16 = 71 * 16
def total_len(L):
    n = 1
    while (L + (n - 1) * LAP16) / n > 11700: n += 1
    return L + (n - 1) * LAP16
nx = int((H - 100) / 200) + 1; ny = int((W - 100) / 200) + 1
L1 = 2 * (nx * total_len(W - 100) + ny * total_len(H - 100)) / 1000.0     # m, two meshes
rows = [('Ск1*', 16, 2580, 2 * nx + 2 * ny), ('Ф1*', 12, 2140, int(round(W * H / 1e6 / 0.32)))]
dop = json.load(open('arm/fm_rows.json'))
items = []
for p, d, L, n in rows: items.append((p, d, str(L), n, KG[d] * L / 1000.0))
items.append(('1', 16, 'пог.м.', round(L1, 1), KG[16]))
for p, d, L, n, _ in dop: items.append((p, d, str(L), n, KG[d] * L / 1000.0))
vol = W * H * 700 / 1e9; volp = (W + 200) * (H + 200) * 100 / 1e9
tot = sum(n * m for _, _, _, n, m in items)
# ---- frame portrait, stamp to the portrait corner ----
fx8 = 528579.0 + 14850.0; fy = 455938.9
m = json.load(open(__import__('os').environ['TEMP'] + '/gx_map.json', encoding='utf-8-sig'))
add(t='mcset', h=m['FM3.8_DC477'], set={'Horizontal': False})
add(t='move', h=[m['FM3.8_DC478'], m['FM3.8_DC479'], m['FM3.8_DC4E5']], d=[-17400, 0])
add(t='move', h=[m['FM3.8_DC4E3']], d=[-8700, 17400])
# ---- tables ----
nrow = 1 + len(items) + 3 + 1
add(t='trows', h=BODY, mode='ins', at=5, **{'from': 4}, n=nrow - 37)
cells = [[0, 12, '%.2f' % tot]]
for i, (p, d, L, n, mu) in enumerate(items):
    r = 1 + i
    cells += [[r, 0, p], [r, 1, 'ГОСТ 34028-2016(%s)' % GOST[d]], [r, 2, '%%C'], [r, 3, str(d)], [r, 4, 'A'], [r, 5, '500С'],
              [r, 8, 'L='], [r, 9, L], [r, 10, ('%.1f' % n) if isinstance(n, float) else str(n)], [r, 11, '%.2f' % mu], [r, 12, '%.2f' % (n * mu)]]
r0 = 1 + len(items)
cells += [[r0 + 1, 1, '(212-101-0901)'], [r0 + 1, 12, '%.2f' % vol], [r0 + 2, 1, '(212-101-0401)'], [r0 + 2, 12, '%.2f' % volp]]
add(t='tset', h=BODY, cells=cells)
# steel summary: A500С only, Ø10…Ø32
by = {}
for p, d, L, n, mu in items: by[d] = by.get(d, 0) + n * mu
for r in ((3, 1, 3, 3), (3, 4, 3, 11), (4, 1, 4, 3), (4, 4, 4, 11)):
    add(t='tmerge', h=STEEL, r=list(r), mode='unmerge')
add(t='tmerge', h=STEEL, r=[3, 1, 3, 11], mode='merge'); add(t='tmerge', h=STEEL, r=[4, 1, 4, 11], mode='merge')
DS = [10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
sc = [[3, 1, 'А500С'], [4, 1, 'ГОСТ 34028-2016'], [5, 11, 'Итого'], [6, 11, '%.2f' % tot], [6, 12, '%.2f' % tot]]
for j, d in enumerate(DS):
    sc += [[5, 1 + j, '%%C' + str(d)], [6, 1 + j, '%.2f' % by.get(d, 0)]]
add(t='tset', h=STEEL, cells=sc)
# placement: header/body on the left, steel summary + details on the right above the stamp
T = fy + 59400 - 500
add(t='move', h=[HDR], d=[fx8 + 2300 - (-1908358), T - (-1264674)])
add(t='move', h=[BODY], d=[fx8 + 2300 - (-1908358), T - 2300 - (-1264674)])
add(t='move', h=[STEEL], d=[fx8 + 23500 - (-1898724), fy + 22000 - (-1303650)])
add(t='move', h=[DET], d=[fx8 + 23500 - (-1899642), fy + 14000 - (-1314011)])
json.dump(ops, open('ops/fm3.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(len(items), 'items', round(tot), 'kg', 'L1', round(L1), 'vol', round(vol, 2), round(volp, 2))
