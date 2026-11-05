# См-1 sheet 5.3 (analog 4.3 reworked): the analog's own horizontal bars / notes kept; Ø per storey from LIRA, positions renumbered,
# step chain on the right recomputed. U-bars wrap the free end: long leg + 170 + return leg (61d).
import sys, os, json, math; sys.path.insert(0, 'wl'); from common import *
from notes import notes
from rowsplit import rows as ROWS
SX, SY = 948800.0, 455939.0
def W(x, y): return [SX + x, SY + y]
L = [v - 347 for v in (15147, 19697, 23747, 26897, 30047, 33197, 36347, 39497)]
SLAB = 250.0
HD = [(14, 200), (16, 200), (16, 200), (12, 200), (12, 200), (12, 200), (14, 100)]   # per storey, max As of the pieces (LIRA AS1/AS2)
LAP = lambda d: {10: 610, 12: 730, 14: 860, 16: 980, 18: 1100, 20: 1220}.get(d, int(math.ceil(61 * d / 10.0) * 10))   # 61d as in the analog lap table (B25)
LONG = {'end': 1310, 'mid': 1810}            # analog 1085 / 1760 for pieces 875 / 1800 -> ours 1100 / 1850
vj = json.load(open('wl/sm1_vert.json', encoding='utf-8'))
P0 = max(vj['POS'].values())
POS = {}
def pos_of(kind, d):
    if (kind, d) not in POS: POS[(kind, d)] = P0 + len(POS) + 1
    return POS[(kind, d)]
def storey(y):
    for s in range(7):
        if L[s] - 10 <= y <= L[s + 1] - 10: return s
def grid(s):
    yb, yt = L[s], L[s + 1]; d, st = HD[s]; y0 = yb + 50
    pos, segs = ROWS(yb, yt, st, SLAB); return pos[0], pos[-1], len(pos) - 1
R = listwin(SX, SY, 59400, 42000, None)
N = notes(SX, SY, 59400, 42000)
ops = []; BARS = []
for r in R:
    if r['t'] in ('LINE', 'LWPOLYLINE') and r['lay'].lower().startswith('диам') and r['y0'] > 14000 and abs(r['y1'] - r['y0']) < 1:
        y = r['y0']; s = storey(y); d = HD[s][0]
        y0, y1, n_ = grid(s); y = y0 if abs(y - y0) < abs(y - y1) and y < (L[s] + L[s + 1]) / 2 else y1
        ops.append(dict(t='erase', h=[r['h']]))
        ops.append(dict(t='pl', p=[W(r['x0'], y), W(r['x1'], y)], layer='диам%d' % d, lw=40))
for n in N:
    if n['l2'].startswith('(') and n['pts'][0][1] > 14000:
        s = storey(n['pts'][0][1]); d, st = HD[s]
        kind = 'end' if n['pts'][0][0] < 12000 or n['pts'][0][0] > 28000 else 'mid'
        p = pos_of(kind, d)
        ops.append(dict(t='mcset', h=n['h'], set={'FirstLine': str(p), 'SecondLine': '(%%%%C%d)' % d}))
        y0, y1, n_ = grid(s)
        ops.append(dict(t='spmove', h=n['h'], items=[[0, SX + n['pts'][0][0], SY + (y0 + y1) / 2], [1, SX + n['pts'][1][0], SY + y0], [2, SX + n['pts'][2][0], SY + y1]]))
# rows and step chain per storey (the whole wall, analog: one chain on the right)
er = [r['h'] for r in R if r['t'] == 'DIMENSION' and r['x0'] > 29000 and r['y0'] > 14000 and r['x1'] < 33500]
ops.insert(0, dict(t='erase', h=er))
XE, XD = 29965.0, 31130.0
for s in range(7):
    yb, yt = L[s], L[s + 1]; d, st = HD[s]
    pos_, segs_ = ROWS(yb, yt, st, SLAB); y0, ytop, n = pos_[0], pos_[-1], len(pos_) - 1
    rows = len(pos_)
    for kind, cnt in (('end', 2), ('mid', 2)):
        BARS.append(dict(pos=pos_of(kind, d), d=d, L=LONG[kind] + 170 + LAP(d), n=2 * rows * cnt, storey=s))
    ch = []
    if s == 0: ch.append((yb, y0, ''))
    for a_, b_, v_, k_ in segs_: ch.append((a_, b_, ('%dх%d' % (v_, k_)) if k_ > 1 else ''))
    ch.append((ytop, (L[s + 1] + 50) if s < 6 else L[7], ''))
    for a, b, txt in ch:
        kw = dict(t='dim', h='WT_DV', p1=W(XE, a), p2=W(XE, b), dl=W(XD, (a + b) / 2), rot=math.pi / 2, txt=txt)
        if b - a < 450: kw['tx'] = W(XD + 620, (a + b) / 2)
        ops.append(kw)
# ops.append(dict(t='dimtx', h='140B97', at=W(5461, 28700)))
ops.append(dict(t='save'))
json.dump(dict(POS={'%s_%d' % k: v for k, v in POS.items()}, BARS=BARS, LONG=LONG), open('wl/sm1_hor.json', 'w'), ensure_ascii=False)
print('ops', len(ops), 'erase dims', len(er), POS)
if '--run' in sys.argv:
    out = gx.run(ops, 'sm1h'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-5:])
# notes inside the piece so that the shelf crosses neither the faces nor the axis
NX = {10324: 9935 + 150, 16610: 16735 + 100, 23060: 23185 + 100, 29347: 29735 - 100}
def move_notes():
    N = notes(SX, SY, 59400, 42000); ops = []
    for n in N:
        if not n['l2'].startswith('(') or n['pts'][0][1] < 14000: continue
        ox = round(n['pts'][0][0]); nx = next((v for k, v in NX.items() if abs(k - ox) < 5), None)
        if nx is None: continue
        ops.append(dict(t='spmove', h=n['h'], items=[[j, SX + nx, SY + p[1]] for j, p in enumerate(n['pts'])]))
    ops.append(dict(t='save'))
    out = gx.run(ops, 'sm1hn'); print('moved', len(ops) - 1, [l for l in out.splitlines() if 'ERR' in l or 'done' in l][-3:])
if '--notes' in sys.argv: move_notes()
