# Horizontal sheet, analog style «straight bar through the piece + Ск U-caps at the free ends» (analog См-2 4.8):
# the analog's bars and notes are kept: layer/Ø per storey, top bar on the step grid, texts; step chain on the right recomputed.
# usage: python wl/wall_hor2.py cfg_sm2 [--run]
import sys, os, json, math, importlib; sys.path.insert(0, 'wl'); from common import *
from notes import notes
from rowsplit import rows as ROWS
CFG = importlib.import_module(sys.argv[1]).HOR
SX, SY = CFG['SX'], 455939.0
def W(x, y): return [SX + x, SY + y]
L = CFG['L']; SLAB = 250.0
LAP = lambda d: int(math.ceil(61 * d / 10.0) * 10)
A = lambda d: math.pi * d * d / 400
LEV = [-4.65, -0.1, 3.95, 7.1, 10.25, 13.4, 16.55, 19.7]
CELLS = [c for c in json.load(open('arm/wall_cells.json')) if c['pl'] == CFG['PLANE']]
KX = ('x0', 'x1') if CFG['PLANE'][0] == 'y' else ('y0', 'y1')
def hd(s):
    cs = [c for c in CELLS if LEV[s] - 1e-3 <= c['z0'] < LEV[s + 1] - 1e-3 and any(c[KX[1]] > a + 1 and c[KX[0]] < b - 1 for a, b in CFG['LIRA'])]
    req = max(max(c['As'][0], c['As'][1]) for c in cs)
    return next((d, st) for d, st in ((10, 200), (12, 200), (14, 200), (16, 200), (12, 100), (14, 100), (16, 100), (18, 100)) if A(d) * 1000 / st >= req - 1e-6)
HD = [hd(s) for s in range(7)]
def grid(s):
    d, st = HD[s]; y0 = L[s] + 50
    pos, segs = ROWS(L[s], L[s + 1], st, SLAB); return pos[0], pos[-1], len(pos) - 1
def storey(y):
    for s in range(7):
        if L[s] - 10 <= y <= L[s + 1] - 10: return s
P0 = len(json.load(open(CFG['VJSON'], encoding='utf-8'))['POS']) if CFG.get('VJSON') else CFG['P0']; POS = {}
def pos_of(k):
    if k not in POS: POS[k] = P0 + len(POS) + 1
    return POS[k]
CK0 = CFG['CK0']; CKS = {int(k): v for k, v in json.load(open(CFG['VJSON'], encoding='utf-8'))['CAPS'].items()} if CFG.get('VJSON') else {}
CK0 = max(CKS.values()) if CKS else CK0
def ck_of(d):
    if d not in CKS: CKS[d] = max(list(CKS.values()) + [CK0]) + 1
    return CKS[d]
R = listwin(SX, SY, 59400, 42000, None)
N = notes(SX, SY, 59400, 42000)
ops = []; BARS = []
X1E = CFG['AXES'][0] - 300; X4E = CFG['AXES'][-1] + 300
HL = [r for r in R if r['t'] in ('LINE', 'LWPOLYLINE') and r['lay'].lower().startswith('диам') and abs(r['y1'] - r['y0']) < 1 and X1E < r['x0'] and r['x1'] < X4E and r['y0'] > L[0] - 100]
LONG = [r for r in HL if r['x1'] - r['x0'] >= 1500]
CK_X = []                                                              # (old centre, new centre) of the Ск lines, for the notes
for r in HL:
    s = storey(r['y0'])
    if s is None: continue
    d = HD[s][0]; y0, y1, n = grid(s); bottom = r['y0'] < (L[s] + L[s + 1]) / 2
    ops.append(dict(t='erase', h=[r['h']]))
    if r['x1'] - r['x0'] >= 1500:                                      # straight bar through the piece, on the step grid
        ops.append(dict(t='pl', p=[W(r['x0'], y0 if bottom else y1), W(r['x1'], y0 if bottom else y1)], layer='диам%d' % d, lw=40))
    else:                                                              # analog: Ск leg drawn BESIDE the main bar (20 inward), length = leg
        leg = LAP(d); left = any(abs(q['x0'] - r['x0']) < 5 for q in LONG)
        xa, xb = (r['x0'], r['x0'] + leg) if left else (r['x1'] - leg, r['x1'])
        y = y0 + 20 if bottom else y1 - 20
        ops.append(dict(t='pl', p=[W(xa, y), W(xb, y)], layer='диам%d' % d, lw=40))
        CK_X.append((s, (r['x0'] + r['x1']) / 2, (xa + xb) / 2))
for nn in N:
    if nn['pts'][0][1] < L[0] - 100 or len(nn['pts']) != 3 or not (CFG['AXES'][0] - 3000 < nn['pts'][0][0] < CFG['AXES'][-1] + 3000): continue
    s = storey(nn['pts'][0][1])
    if s is None: continue
    d, st = HD[s]; y0, y1, n = grid(s)
    if nn['l1'].startswith('Ск'): l1, l2 = 'Ск%d' % ck_of(d), '(%%%%%%%%C%d)' % d
    else: l1, l2 = str(pos_of(('S', d))), 'ш.%d' % st
    ops.append(dict(t='mcset', h=nn['h'], set={'FirstLine': l1.replace('%%%%', '%%'), 'SecondLine': ('(%%%%C%d)' % d) if l2.startswith('(') else l2}))
    if nn['l1'].startswith('Ск'):                                       # leaders to the Ск legs (20 inside the main bars)
        cs = [q for q in CK_X if q[0] == s] or CK_X
        xc = min(cs, key=lambda q: abs(q[1] - nn['pts'][1][0]))[2] if cs else nn['pts'][1][0]
        ops.append(dict(t='spmove', h=nn['h'], items=[[0, SX + xc, SY + (y0 + y1) / 2], [1, SX + xc, SY + y0 + 20], [2, SX + xc, SY + y1 - 20]]))
    else:
        ops.append(dict(t='spmove', h=nn['h'], items=[[0, SX + nn['pts'][0][0], SY + (y0 + y1) / 2], [1, SX + nn['pts'][1][0], SY + y0], [2, SX + nn['pts'][2][0], SY + y1]]))
# straight bars and caps per storey
for s in range(7):
    d, st = HD[s]; y0, y1, n = grid(s); rows = n + 1                  # n spaces -> n + 1 rows
    BARS.append(dict(pos=pos_of(('S', d)), d=d, L=CFG['STRAIGHT'], n=2 * rows * CFG['NPAIR']))
    BARS.append(dict(pos='Ск%d' % ck_of(d), d=d, L=2 * LAP(d) + 170, n=rows * 2 * CFG['NPAIR']))
# step chain on the right (analog): template = one of the analog chain dims, the rest erased
chain = [r for r in R if r['t'] == 'DIMENSION' and r['x0'] > CFG['AXES'][-1] - 200 and r['y0'] > L[0] - 800 and r['x1'] < CFG['AXES'][-1] + 3500]
tdim = 'WT_DV'; XE, XD = CFG['XE'], CFG['XD']
ops.insert(0, dict(t='erase', h=[r['h'] for r in chain]))
for s in range(7):
    yb = L[s]; d, st = HD[s]; y0, ytop, n = grid(s)
    ch = []
    if s == 0: ch.append((yb, y0, ''))
    for a_, b_, v_, k_ in ROWS(L[s], L[s + 1], st, SLAB)[1]: ch.append((a_, b_, ('%dх%d' % (v_, k_)) if k_ > 1 else ''))
    ch.append((ytop, (L[s + 1] + 50) if s < 6 else L[7], ''))
    for a, b, txt in ch:
        kw = dict(t='dim', h=tdim, p1=W(XE, a), p2=W(XE, b), dl=W(XD, (a + b) / 2), rot=math.pi / 2, txt=txt)
        if b - a < 450: kw['tx'] = W(XD + 620, (a + b) / 2)
        ops.append(kw)
ops.append(dict(t='save'))
json.dump(dict(HD=HD, POS={'%s_%d' % k: v for k, v in POS.items()}, CKS=CKS, BARS=BARS), open(CFG['OUT'], 'w'), ensure_ascii=False)
print('HD', HD, 'POS', POS, 'CK', CKS, 'chain erased', len(chain))
if '--run' in sys.argv:
    out = gx.run(ops, 'wh2'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
