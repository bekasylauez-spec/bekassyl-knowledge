# Sheet 4.1 "Схема расположения колонн" (A2, 1:100) — built from analog sheet 2.1 objects (clone/move), plan from
# "СХЕМА КОЛОНН МАССПОДГОТОВКА.dwg" (Block 2: axes 9-13 / А-К) + LIRA-only columns.
import json, math, sys
import mb

F0 = (-1612203.1, -1749172.3)          # A2 frame 37EA1B (59400 x 42000)
PX0, PY0 = F0[0] + 8500, F0[1] + 9300  # axis 9 / axis А on the sheet
AXX = {'9': 55050, '10': 64150, '11': 73650, '12': 79650, '13': 86250}
AXY = {'А': 0, 'Б': 7000, 'Д': 16500, 'Ж': 22000, 'К': 29000}
def P(x, y): return [PX0 + x - 55050, PY0 + y]

# columns (scheme coords: centre x, centre y, size X, size Y, mark, level note)
COLS = json.load(open(mb.S + r'\colplan.json', encoding='utf-8'))

ops = []
def add(**k): ops.append(k); return k

# ---- axes (reuse 2.1 SPDS axes) ----
dig = ['3444AD', '3444AE', '3444AF', '3444B0', '3444B1']
for h, (v, x) in zip(dig, AXX.items()):
    add(t='axis', h=h, s=P(x, 29000 + 1900), e=P(x, -5200), val=v)
add(t='erase', h=['3444B2', '3444B3', '3444B4'])
let = ['34467D', '344687', '3446D3']
for i, (v, y) in enumerate(AXY.items()):
    if i < 3: h = let[i]
    else:
        h = 'AXL_' + v; add(t='clone', h='34467D', tag=h)
    add(t='axis', h=h, s=P(86250 + 1400, y), e=P(55050 - 4700, y), val=v)

# ---- columns: rect + hatch (reuse 24 pairs of 2.1, clone the rest) ----
pairs = [l.split() for l in open(mb.S + r'\w\colpairs21.txt', encoding='utf-8') if l.strip()]
for i, c in enumerate(COLS):
    x0, y0, x1, y1 = c['x'] - c['bx'] / 2, c['y'] - c['by'] / 2, c['x'] + c['bx'] / 2, c['y'] + c['by'] / 2
    pts = [P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)]
    if i < len(pairs): hr, hh = pairs[i]
    else:
        hr, hh = 'COLR_%d' % i, 'COLH_%d' % i
        add(t='clone', h=pairs[0][0], tag=hr); add(t='clone', h=pairs[0][1], tag=hh)
    add(t='plset', h=hr, p=pts, closed=True)
    add(t='hatchset', h=hh, loops=[[p + [0] for p in pts]])
for hr, hh in pairs[len(COLS):]:
    add(t='erase', h=[hr, hh])

json.dump(ops, open(mb.S + r'\ops\sch_ops.json', 'w', encoding='utf-8'), ensure_ascii=False)
if __name__ == '__main__' and 'run' in sys.argv:
    print(mb.run(ops, 'sch1', 1200))
