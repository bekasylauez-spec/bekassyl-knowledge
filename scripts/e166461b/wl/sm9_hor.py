# См-8 horizontal sheet (analog См-9 4.34 hor, remapped by sm8_elev): per storey and piece two straight bars (bottom / top row),
# Ск at the free ends and at the A/1 corner, Ø per storey from LIRA (plane x = 6800); positions after the vertical ones by (Ø, L);
# analog notes cloned (pos: text left of its leader; Ск: text inward); step chains right of the wall and in each opening.
import sys, os, json, math; sys.path.insert(0, 'wl'); from common import *
from notes import notes
from rowsplit import rows as ROWS
SX, SY = 2543100.0, 455939.0; AX1 = float(os.environ.get('AX1', 12045.0))
def W(x, y): return [SX + AX1 + x, SY + y]
L = [10291, 14841, 18891, 22041, 25191, 28341, 31491, 34641, 37341]
LEV = [-4.65, -0.1, 3.95, 7.1, 10.25, 13.4, 16.55, 19.7, 22.4]
SLAB = 250.0; NS = len(L) - 1
LAP = lambda d: {10: 610, 12: 730, 14: 860, 16: 980, 18: 1100, 20: 1220}.get(d, int(math.ceil(61 * d / 10.0) * 10))
A = lambda d: math.pi * d * d / 400
CELLS = [c for c in json.load(open('arm/wall_cells.json')) if c['pl'] == ['x', 10400]]
# pieces per storey: (outline a, b, Ск left, Ск right); bars: free end cover 50, into a cross wall 20 from its far face
FL = [(15225, 18025, True, False), (20375, 22875, True, False)]
PCS = {}
FREE = {15225, 20375}
LIRA = {}
LIRAF = [(15225, 17600), (20375, 22750)]
def hd(s):
    rng = LIRA.get(s, LIRAF)
    cs = [c for c in CELLS if LEV[s] - 1e-3 <= c['z0'] < LEV[s + 1] - 1e-3 and any(c['y1'] > a + 1 and c['y0'] < b - 1 for a, b in rng)]
    if s == 0: cs = [c for c in cs if c['z0'] >= -4.2] or cs
    req = max(max(c['As'][0], c['As'][1]) for c in cs)
    return next((d, st) for d, st in ((10, 200), (12, 200), (14, 200), (16, 200), (12, 100), (14, 100), (16, 100), (18, 100)) if A(d) * 1000 / st >= req - 1e-6)
HD = [hd(s) for s in range(NS)]
vj = json.load(open('wl/sm9_vert.json', encoding='utf-8'))
P0 = max(vj['POS'].values()); CK0 = max(int(v) for v in vj['CAPS'].values())
POS = {}; CKS = {}
def pos_of(k):
    if k not in POS: POS[k] = P0 + len(POS) + 1
    return POS[k]
def ck_of(d):
    if d not in CKS: CKS[d] = CK0 + len(CKS) + 1
    return CKS[d]
R = listwin(SX, SY, 59400, 42000, None); N = notes(SX, SY, 59400, 42000)
inE = lambda x: AX1 + 13000 < x < AX1 + 25500
NE = [n for n in N if n['pts'][0][1] > L[0] - 600 and inE(n['pts'][0][0]) and len(n['pts']) == 3]
# templates: pos note with text left of its leader, Ск notes with text right / left of the leader
Rh = {r['h']: r for r in R}
def tside(n):
    r = Rh.get(n['h']); return 'L' if r and (r['x0'] + r['x1']) / 2 < n['pts'][0][0] else 'R'
TPL = {}
for n in NE:
    k = ('pos' if n['l2'].startswith('ш.') or not n['l1'].startswith('Ск') else 'ck') + tside(n)
    TPL.setdefault(k, n['h'])
print('templates', TPL)
TP = {k: v for k, v in {'pos': TPL.get('posL'), 'ckL': TPL.get('ckR'), 'ckR': TPL.get('ckL')}.items() if v}
er = [r['h'] for r in R if r['t'] in ('LINE', 'LWPOLYLINE') and r['lay'].lower().startswith('диам') and r['y0'] > L[0] - 100 and inE(r['x0']) and inE(r['x1'])]
er += [r['h'] for r in R if r['t'] == 'DIMENSION' and r['y0'] > L[0] - 300 and inE(r['x0']) and inE(r['x1'])]
er += [n['h'] for n in NE]
THIN = [((r['x0'] + r['x1']) / 2 - AX1, r['y0'], r['y1']) for r in R if r['t'] in ('LINE', 'LWPOLYLINE') and r['x1'] - r['x0'] < 2 and r['y1'] - r['y0'] > 1500
        and not r['lay'].lower().startswith('диам') and r['y0'] > L[0] - 50 and inE(r['x0'])]          # thin verticals of the analog background
THIN += [(x - AX1, r['y0'], r['y1']) for r in R if r['t'] == 'LWPOLYLINE' and 200 < r['x1'] - r['x0'] < 300 and r['y1'] - r['y0'] > 1500 and r['y0'] > L[0] - 50 and inE(r['x0']) for x in (r['x0'], r['x1'])]   # cross-wall strips
ops = [dict(t='clone', h=v, base=[0, 0], to=[0, -300000], tag='H9' + k) for k, v in TP.items()]
ops.append(dict(t='erase', h=sorted(set(er))))
BARS = []
def note(tpl, l1, l2, x, ym, y0, y1):
    if tpl not in TP:                                    # no analog template with the text on this side: new SPDS note (text right)
        ops.append(dict(t='note', l1=l1, l2=l2, origin=W(x, ym), targets=[W(x, y0), W(x, y1)], scale=100, ts=2.5, style='ГОСТ 2.304', arrow='oblique', layer='Размеры'))
        return
    tg = 'H9n%d' % len(ops)
    ops.append(dict(t='clone', h='H9' + tpl, base=[0, 0], to=[0, 0], tag=tg))
    ops.append(dict(t='spmove', h=tg, items=[[0] + W(x, ym), [1] + W(x, y0), [2] + W(x, y1)]))
    ops.append(dict(t='mcset', h=tg, set={'FirstLine': l1, 'SecondLine': l2}))
for s in range(NS):
    d, st = HD[s]; pos, segs = ROWS(L[s], L[s + 1], st, SLAB); y0, y1 = pos[0], pos[-1]; rows = len(pos)
    if len(segs) == 3 and segs[1][3] == 1:               # leftover space at the top (analog 4.31: «150» under the slab), not in the middle
        n_ = segs[0][3] + segs[2][3]; rem = segs[1][2]
        pos = [y0 + st * k for k in range(n_ + 1)] + [y1]; segs = [(y0, y0 + st * n_, st, n_), (y0 + st * n_, y1, rem, 1)]
    lay = 'диам%d' % d; leg = LAP(d); ym = (y0 + y1) / 2; c = ck_of(d)
    for k, (a, b, ckl, ckr) in enumerate(PCS.get(s, FL)):
        fa = a + (50 if a in FREE else 20); fb = b - (50 if b in FREE else 20)
        Lb = int(round(fb - fa, -1)); p = pos_of((d, Lb))
        for y in (y0, y1): ops.append(dict(t='pl', p=[W(fa, y), W(fb, y)], layer=lay, lw=40))
        BARS.append(dict(pos=p, d=d, L=Lb, n=2 * rows, storey=s))
        xs_ck = []
        for end, on in (('L', ckl), ('R', ckr)):
            if not on: continue
            xa, xb = (fa, fa + leg) if end == 'L' else (fb - leg, fb)
            ops.append(dict(t='pl', p=[W(xa, y0 + 20), W(xb, y0 + 20)], layer=lay, lw=40))
            ops.append(dict(t='pl', p=[W(xa, y1 - 20), W(xb, y1 - 20)], layer=lay, lw=40))
            BARS.append(dict(pos='Ск%d' % c, d=d, L=2 * leg + 170, n=rows, storey=s))
            xc = xa + 150 if end == 'L' else xb - 150; xs_ck.append(xc)      # leader near the free end, text inward (analog «Ск5»)
            note('ckL' if end == 'L' else 'ckR', 'Ск%d' % c, '', xc, ym + 550 if (y1 - y0) > 1500 else ym, y0 + 20, y1 - 20)
        xp = fb - 900 if ckr else fb - 50                    # pos note: leader near the right end, text to its left
        if fb - fa > 6000: xp = (fa + fb) / 2 + 600
        tl = [x for x, b0, b1 in THIN if b0 < ym < b1]
        for dx_ in [0] + [s_ * 10 * k_ for k_ in range(1, 150) for s_ in (-1, 1)]:      # text [xp-1000, xp] clear of the thin lines
            x_ = xp + dx_
            if fa + 190 < x_ - 950 and x_ < fb - 20 and not any(x_ - 990 < t < x_ + 40 for t in tl): xp = x_; break
        note('pos', str(p), 'ш.%d' % st, xp, ym - 550 if (y1 - y0) > 1500 else ym, y0, y1)
    # chain right of the wall
    ch = []
    if s == 0: ch.append((L[0], y0, ''))
    for a_, b_, v_, k_ in segs: ch.append((a_, b_, ('%dх%d' % (v_, k_)) if k_ > 1 else ''))
    ch.append((y1, (L[s + 1] + 50) if s < NS - 1 else L[NS], ''))
    xr = 22875
    for a, b, txt in ch:
        if s == NS - 1:
            pass
        kw = dict(t='dim', h='WT_DV', p1=W(xr, a), p2=W(xr, b), dl=W(xr + 1440, (a + b) / 2), rot=math.pi / 2, txt=txt)
        if b - a < 450:
            k_ = ch.index((a, b, txt)); prv = k_ > 0 and ch[k_ - 1][1] - ch[k_ - 1][0] < 450; nxt_ = k_ < len(ch) - 1 and ch[k_ + 1][1] - ch[k_ + 1][0] < 450
            yt_ = b + 300 if prv else (a - 300 if nxt_ else (a + b) / 2)      # two short spaces in a row: texts beyond their ends (analog «150 / 300»)
            kw['tx'] = W(xr + 1440 + 620, yt_)
        ops.append(kw)
    if True:                                                # chain left of piece 1 (analog: left of the wall, every storey)
        for xf, dx in ((15225, -1440),):
            ch = [(L[s], y0, '')] + [(a_, b_, ('%dх%d' % (v_, k_)) if k_ > 1 else '') for a_, b_, v_, k_ in segs] + [(y1, L[s + 1] - SLAB, '')]
            for a, b, txt in ch:
                kw = dict(t='dim', h='WT_DV', p1=W(xf, a), p2=W(xf, b), dl=W(xf + dx, (a + b) / 2), rot=math.pi / 2, txt=txt)
                if b - a < 450:
                    tight = len(segs) > 1                         # a leftover space in the middle: the step texts are long, «50» close to the slabs
                    k_ = ch.index((a, b, txt)); prv = k_ > 0 and ch[k_ - 1][1] - ch[k_ - 1][0] < 450; nxt_ = k_ < len(ch) - 1 and ch[k_ + 1][1] - ch[k_ + 1][0] < 450
                    yt_ = (b + (450 if s == NS - 1 else 100)) if prv else (((a + b) / 2 if s == NS - 1 else a - 400) if nxt_ else (a + 350 if a == L[s] else (b - 650 if b > L[s + 1] - SLAB - 5 else (a + b) / 2)))
                    kw['tx'] = W(xf + dx - 200, yt_)
                ops.append(kw)
ops.append(dict(t='erase', h=['H9' + k for k in TP]))
ops.append(dict(t='save'))
json.dump(dict(HD=HD, POS={'%d_%d' % k: v for k, v in POS.items()}, CKS={str(k): v for k, v in CKS.items()}, BARS=BARS), open('wl/sm9_hor.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('HD', HD, 'POS', POS, 'CK', CKS, 'erase', len(er), 'ops', len(ops))
if '--run' in sys.argv:
    out = gx.run(ops, 'sm9h'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-8:])
