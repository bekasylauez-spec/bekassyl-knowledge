# См-6 sheet 5.22: corner piers' horizontal bars in the grammar of the См-1 sheet 5.3 (analog 4.3): U-bars around the free end
# (long leg + 170 + return leg 61d), Ø per storey from LIRA (plane y = 22750), positions after the vertical ones, step chain on the right.
import sys, os, json, math; sys.path.insert(0, 'wl'); from common import *
from notes import notes
from rowsplit import rows as ROWS
SX, SY = 1845600.0, 455939.0
def W(x, y): return [SX + x, SY + y]
L = [15206, 19756, 23806, 26956, 30106, 33256, 36406, 39556]
LEV = [-4.65, -0.1, 3.95, 7.1, 10.25, 13.4, 16.55, 19.7]
SLAB = 250.0
LAP = lambda d: int(math.ceil(61 * d / 10.0) * 10)
A = lambda d: math.pi * d * d / 400
CELLS = [c for c in json.load(open('arm/wall_cells.json')) if c['pl'] == ['y', 22750]]
LIRA = [(0, 1225), (18825, 20050)]
def hd(s):
    cs = [c for c in CELLS if LEV[s] - 1e-3 <= c['z0'] < LEV[s + 1] - 1e-3 and any(c['x1'] > a + 1 and c['x0'] < b - 1 for a, b in LIRA)]
    req = max(max(c['As'][0], c['As'][1]) for c in cs)
    return next((d, st) for d, st in ((10, 200), (12, 200), (14, 200), (16, 200), (12, 100), (14, 100), (16, 100), (18, 100)) if A(d) * 1000 / st >= req - 1e-6)
HD = [hd(s) for s in range(7)]
LONG = {'end': 1310}                         # См-1 piers 1100: long leg 1310 (analog 1085 for 875)
vj = json.load(open('wl/sm6_vert.json', encoding='utf-8'))
P0 = max(vj['POS'].values())
POS = {}
def pos_of(kind, d):
    if (kind, d) not in POS: POS[(kind, d)] = P0 + len(POS) + 1
    return POS[(kind, d)]
def storey(y):
    for s in range(7):
        if L[s] - 10 <= y <= L[s + 1] - 10: return s
def grid(s):
    d, st = HD[s]; pos, segs = ROWS(L[s], L[s + 1], st, SLAB); return pos[0], pos[-1], len(pos) - 1
R = listwin(SX, SY, 59400, 42000, None)
N = notes(SX, SY, 59400, 42000)
ops = []; BARS = []
for r in R:
    if r['t'] in ('LINE', 'LWPOLYLINE') and r['lay'].lower().startswith('диам') and r['y0'] > 14000 and abs(r['y1'] - r['y0']) < 1 and r['x1'] < 33000:
        y = r['y0']; s = storey(y); d = HD[s][0]
        y0, y1, n_ = grid(s); y = y0 if y < (L[s] + L[s + 1]) / 2 else y1
        ops.append(dict(t='erase', h=[r['h']]))
        ops.append(dict(t='pl', p=[W(r['x0'], y), W(r['x1'], y)], layer='диам%d' % d, lw=40))
for n in N:
    if n['l2'].startswith('(') and n['pts'][0][1] > 14000:
        s = storey(n['pts'][0][1]); d, st = HD[s]
        p = pos_of('end', d)
        ops.append(dict(t='mcset', h=n['h'], set={'FirstLine': str(p), 'SecondLine': '(%%%%C%d)' % d}))
        y0, y1, n_ = grid(s)
        ops.append(dict(t='spmove', h=n['h'], items=[[0, SX + n['pts'][0][0], SY + (y0 + y1) / 2], [1, SX + n['pts'][1][0], SY + y0], [2, SX + n['pts'][2][0], SY + y1]]))
er = [r['h'] for r in R if r['t'] == 'DIMENSION' and r['x0'] > 28800 and r['y0'] > 14000 and r['x1'] < 33500]
ops.insert(0, dict(t='erase', h=er))
XE, XD = 29856.0, 31021.0
for s in range(7):
    yb, yt = L[s], L[s + 1]; d, st = HD[s]
    pos_, segs_ = ROWS(yb, yt, st, SLAB); y0, ytop = pos_[0], pos_[-1]
    rows = len(pos_)
    BARS.append(dict(pos=pos_of('end', d), d=d, L=LONG['end'] + 170 + LAP(d), n=2 * rows * 2, storey=s))
    ch = []
    if s == 0: ch.append((yb, y0, ''))
    for a_, b_, v_, k_ in segs_: ch.append((a_, b_, ('%dх%d' % (v_, k_)) if k_ > 1 else ''))
    ch.append((ytop, (L[s + 1] + 50) if s < 6 else L[7], ''))
    for a, b, txt in ch:
        kw = dict(t='dim', h='WT_DV', p1=W(XE, a), p2=W(XE, b), dl=W(XD, (a + b) / 2), rot=math.pi / 2, txt=txt)
        if b - a < 450: kw['tx'] = W(XD + 620, (a + b) / 2)
        ops.append(kw)
ops.append(dict(t='save'))
json.dump(dict(POS={'%s_%d' % k: v for k, v in POS.items()}, BARS=BARS, LONG=LONG, HD=HD), open('wl/sm6_hor.json', 'w'), ensure_ascii=False)
print('ops', len(ops), 'erase dims', len(er), POS, HD)
if '--run' in sys.argv:
    out = gx.run(ops, 'sm6h'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-5:])
