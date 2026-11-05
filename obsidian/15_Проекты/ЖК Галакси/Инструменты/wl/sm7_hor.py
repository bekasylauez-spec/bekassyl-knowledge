# См-7 sheet 5.27 (analog 4.22 horizontal): per storey and piece two straight bars (bottom / top row of the step grid),
# Ск U-caps at the free ends (+ the A/1 corner, as in the analog; basement both ends), Ø per storey from LIRA (plane x = 0),
# positions after the vertical ones (wl/sm7_vert.json), analog notes cloned (pos: text left; Ск: text inward),
# step chains: right of the wall (as analog) and in each opening at the free end; basement/axes/foundation cleaned.
import sys, os, json, math; sys.path.insert(0, 'wl'); from common import *
from rowsplit import rows as ROWS
SX, SY = 2078100.0, 455939.0; AX1 = 15030.0
def W(x, y): return [SX + AX1 + x, SY + y]                 # x relative to axis A/1
L = [27970, 32520, 36570, 39720, 42870, 46020, 49170, 52320]
LEV = [-4.65, -0.1, 3.95, 7.1, 10.25, 13.4, 16.55, 19.7]
SLAB = 250.0
LAP = lambda d: {10: 610, 12: 730, 14: 860, 16: 980, 18: 1100, 20: 1220}.get(d, int(math.ceil(61 * d / 10.0) * 10))
A = lambda d: math.pi * d * d / 400
CELLS = [c for c in json.load(open('arm/wall_cells.json')) if c['pl'] == ['x', 0]]
PIECES = [(-125, 3175), (5750, 17100), (20375, 22875)]     # outline (piece 3 includes См-6 wall to 22875)
LIRA = [(0, 3175), (5750, 17100), (20375, 22750)]
def hd(s):
    rng = [(0, 22750)] if s == 0 else LIRA
    cs = [c for c in CELLS if LEV[s] - 1e-3 <= c['z0'] < LEV[s + 1] - 1e-3 and any(c['y1'] > a + 1 and c['y0'] < b - 1 for a, b in rng)]
    if s == 0: cs = [c for c in cs if c['z0'] >= -4.2] or cs          # foundation row closed by the Фм dowels (as for the verticals)
    req = max(max(c['As'][0], c['As'][1]) for c in cs)
    return next((d, st) for d, st in ((10, 200), (12, 200), (14, 200), (16, 200), (12, 100), (14, 100), (16, 100), (18, 100)) if A(d) * 1000 / st >= req - 1e-6)
HD = [hd(s) for s in range(7)]
vj = json.load(open('wl/sm7_vert.json', encoding='utf-8'))
P0 = max(vj['POS'].values()); CK0 = max(int(v) for v in vj['CAPS'].values())
POS = {}; CKS = {}
def pos_of(d):
    if d not in POS: POS[d] = P0 + len(POS) + 1
    return POS[d]
def ck_of(d):
    if d not in CKS: CKS[d] = CK0 + len(CKS) + 1
    return CKS[d]
R = json.load(open('w/r27.json')); N = json.load(open('w/n27.json'))
rel = lambda x: x - AX1
# ---- erase: horizontal bars, notes, dims of the elevation (except the axis dims / level / storey dims on the left)
er = [r['h'] for r in R if r['t'] in ('LINE', 'LWPOLYLINE') and r['lay'].lower().startswith('диам') and r['y0'] > L[0] - 100 and 14800 < r['x0'] and r['x1'] < 38000]
er += [r['h'] for r in R if r['t'] == 'DIMENSION' and r['y0'] > L[0] - 300 and r['x0'] > 14600 and r['h'] != '1FAF4F']
er += ['1F7C3D']
TPL = {'pos': '1F8142', 'ckL': '1F815D', 'ckR': '1F815C', 'ck0': '1F8153'}   # pos: text left; ckL: text right (left end); ckR: text left
er += [n['h'] for n in N if n['pts'][0][1] > L[0] - 600 and 14000 < n['pts'][0][0] < 39000]
ops = [dict(t='clone', h=v, base=[0, 0], to=[0, -300000], tag='H7' + k) for k, v in TPL.items()]
ops.append(dict(t='erase', h=sorted(set(er))))
BARS = []
def note(tpl, l1, l2, x, ym, y0, y1):
    tg = 'H7n%d' % len(ops)
    ops.append(dict(t='clone', h='H7' + tpl, base=[0, 0], to=[0, 0], tag=tg))
    ops.append(dict(t='spmove', h=tg, items=[[0] + W(x, ym), [1] + W(x, y0), [2] + W(x, y1)]))
    ops.append(dict(t='mcset', h=tg, set={'FirstLine': l1, 'SecondLine': l2}))
for s in range(7):
    d, st = HD[s]; pos, segs = ROWS(L[s], L[s + 1], st, SLAB); y0, y1 = pos[0], pos[-1]; rows = len(pos)
    lay = 'диам%d' % d; leg = LAP(d); ym = (y0 + y1) / 2
    if s == 0: pcs = [(-125, 22875, True, True, 2)]                                   # basement: one wall, Ск at both corners
    else: pcs = [(-125, 3175, True, True, 1), (5750, 17100, True, True, 1), (20375, 22875, True, False, 1)]
    p = pos_of(d); c = ck_of(d)
    for k, (a, b, ckl, ckr, _) in enumerate(pcs):
        fa = a + (20 if a in (-125,) else 50); fb = b - (20 if b == 22875 else 50)   # free end: cover 50; into a cross wall: 20 from its far face
        for y in (y0, y1): ops.append(dict(t='pl', p=[W(fa, y), W(fb, y)], layer=lay, lw=40))
        BARS.append(dict(pos=p, d=d, L=int(round(fb - fa, -1)), n=2 * rows, storey=s))
        for end, on in (('L', ckl), ('R', ckr)):
            if not on: continue
            xa, xb = (fa, fa + leg) if end == 'L' else (fb - leg, fb)
            ops.append(dict(t='pl', p=[W(xa, y0 + 20), W(xb, y0 + 20)], layer=lay, lw=40))
            ops.append(dict(t='pl', p=[W(xa, y1 - 20), W(xb, y1 - 20)], layer=lay, lw=40))
            BARS.append(dict(pos='Ск%d' % c, d=d, L=2 * leg + 170, n=rows, storey=s))
            xc = (xa + xb) / 2
            note('ckL' if end == 'L' else 'ckR', 'Ск%d' % c, '(%%%%C%d)' % d, xc, ym + 650, y0 + 20, y1 - 20)
        xp = {0: 1550, 1: 11000, 2: 22450}[k] if s else 11000
        note('pos', str(p), 'ш.%d' % st, xp, ym - 650 if s else ym, y0, y1)
    # chain right of the wall (analog): first storey from the foundation, slab crossings «350»
    ch = []
    if s == 0: ch.append((L[0], y0, ''))
    for a_, b_, v_, k_ in segs: ch.append((a_, b_, ('%dх%d' % (v_, k_)) if k_ > 1 else ''))
    ch.append((y1, (L[s + 1] + 50) if s < 6 else L[7], ''))
    for a, b, txt in ch:
        kw = dict(t='dim', h='WT_DV', p1=W(22875, a), p2=W(22875, b), dl=W(25176, (a + b) / 2), rot=math.pi / 2, txt=txt)
        if b - a < 450: kw['tx'] = W(25176 + 620, (a + b) / 2)
        ops.append(kw)
    if s:                                   # chains in the openings, at the free end (analog: 50 | steps | 50)
        for xf in (3175, 17100):
            ch = [(L[s], y0, '')] + [(a_, b_, ('%dх%d' % (v_, k_)) if k_ > 1 else '') for a_, b_, v_, k_ in segs] + [(y1, L[s + 1] - SLAB, '')]
            for a, b, txt in ch:
                kw = dict(t='dim', h='WT_DV', p1=W(xf, a), p2=W(xf, b), dl=W(xf + 1085, (a + b) / 2), rot=math.pi / 2, txt=txt)
                if b - a < 450: kw['tx'] = W(xf + 1085 + 620, (a + b) / 2)
                ops.append(kw)
ops.append(dict(t='erase', h=['H7' + k for k in TPL]))
# ---- foundation, hatches, foundation dim, axis dims, section mark 3 -> 2
ops.append(dict(t='spmove', h='1FAF2D', items=[[0] + W(23075, 27270), [1] + W(23075, 27970), [2] + W(-325, 27970), [3] + W(-325, 27270)]))
ops.append(dict(t='spmove', h='1FAF2F', items=[[0] + W(23175, 27170), [1] + W(23175, 27270), [2] + W(-425, 27270), [3] + W(-425, 27170)]))
PL = [r for r in R if r['t'] == 'LWPOLYLINE' and r['lay'] == 'Размеры' and r['x1'] - r['x0'] > 20000 and r['y1'] - r['y0'] < 300]
for h in [r for r in R if r['t'] == 'HATCH']:
    if h['y0'] < 27200: bx = (-425, 27170, 23175, 27270)
    elif h['y0'] < 27300: bx = (-325, 27270, 23075, 27970)
    else:
        b = next(p for p in PL if abs(p['y0'] - h['y0']) < 2 and abs(p['y1'] - h['y1']) < 2); bx = (rel(b['x0']), b['y0'], rel(b['x1']), b['y1'])
    ops.append(dict(t='hatchfit', h=h['h'], loops=[[W(bx[0], bx[1]), W(bx[2], bx[1]), W(bx[2], bx[3]), W(bx[0], bx[3])]]))
ops.append(dict(t='dimpts', h='1FAF4F', p1=W(-325, 27970), p2=W(-325, 27270), dl=[SX + 11651, SY + 27620]))
ops.append(dict(t='spmove', h='1FAF23', items=[[1] + W(22750, 25410)]))
for h, (a, b) in (('1FAF29', (0, 5000)), ('1FAF2B', (5000, 14750)), ('1FAF25', (14750, 22750))):
    ops.append(dict(t='dimpts', h=h, p1=W(a, 25410), p2=W(b, 25410), dl=W((a + b) / 2, 23410)))
    ops.append(dict(t='dimtx', h=h, at=W((a + b) / 2, 23410 + 220)))
ops.append(dict(t='erase', h=['1FAF24', '1FAF28']))
ops.append(dict(t='eprops', src='1FAB89', h=['1FAF23', '1FAF29', '1FAF2B', '1FAF25']))
ops.append(dict(t='secset', h='1F816E', word='2'))
ops.append(dict(t='save'))
json.dump(dict(HD=HD, POS={str(k): v for k, v in POS.items()}, CKS={str(k): v for k, v in CKS.items()}, BARS=BARS), open('wl/sm7_hor.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('HD', HD, 'POS', POS, 'CK', CKS, 'erase', len(er), 'ops', len(ops))
if '--run' in sys.argv:
    out = gx.run(ops, 'sm7h'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-8:])
