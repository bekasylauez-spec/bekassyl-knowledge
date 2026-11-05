# Wall См-1 — sheet 5.2 «Вертикальное армирование»: edge zones ш.100 at free ends, middle base Ø12@200 (or by calc).
import json, math, sys
import gx, colsheet as C
sys.path.insert(0, 'arm'); import wall_zones as WZ

SX, SY = 889400.0, 455939.0
def W(x, y): return [SX + x, SY + y]
AX1 = 9810.0                                         # axis 1 on the sheet; scheme x -> sheet x = AX1 + x
L = [15147, 19697, 23747, 26897, 30047, 33197, 36347, 39497]
SLAB = 250.0
PIECES = [(125, 1225), (5875, 7725), (12325, 14175), (18825, 19925)]
ENDS = [(False, True), (True, True), (True, True), (True, False)]
LIRA = [(0, 1225), (5875, 7725), (12325, 14175), (18825, 20050)]
D = WZ.design('y', 0, LIRA, ENDS)
EDGE = 450.0
LAP = lambda d: int(math.ceil(61 * d / 10.0) * 10)

ops = []
def add(**k): ops.append(k); return k
R = C.listwin(SX, SY, 59400, 42000)
er = [r['h'] for r in R if r['t'] == 'LINE' and 9000 < r['x0'] < 31500 and r['y0'] > 13000]
er += [r['h'] for r in R if r['t'] == 'SPDSNOTEPOSITION' and r['y0'] > 14800 and r['x0'] < 40000]
m_ = gx.tagmap(); TPLH = {m_['WT_DH'].upper(), m_['WT_DV'].upper()}
er += [r['h'] for r in R if r['t'] == 'DIMENSION' and r['x0'] > 7400 and r['y1'] > 12500 and r['h'].upper() not in TPLH]
TDIM, TLAP = 'WT_DH', 'WT_DV'
add(t='erase', h=er)

def zones(i, s):
    """[(kind, x_from, x_to, d, step)] in scheme x for piece i, storey s (bars from x_from to x_to)"""
    a, b = PIECES[i]; z = D[i]; el, er_ = ENDS[i]
    out = []
    lo, hi = a + 50, b - 50
    if el and z['L'][s]: out.append(('L', a + 50, a + EDGE, z['L'][s], 100)); lo = a + EDGE + 100
    if er_ and z['R'][s]: out.append(('R', b - EDGE, b - 50, z['R'][s], 100)); hi = b - EDGE - 100
    md, ms = z['M'][s] if z['M'][s] else (12, 200)
    n = max(1, int((hi - lo) // ms)); out.append(('M', lo, lo + n * ms, md, ms))
    return out

# ---- bars, positions ----
POS = {}; BARS = []
def pos_of(d, Lb):
    k = (d, Lb)
    if k not in POS: POS[k] = len(POS) + 1
    return POS[k]
NOTE = dict(scale=100, ts=2.5, style='ГОСТ 2.304', arrow='oblique', layer='Размеры')
for s in range(7):
    yb = L[s]; yt = L[s + 1]
    for i in range(4):
        zs = zones(i, s)
        for k, (kind, x0, x1, d, st) in enumerate(zs):
            nxt = [z for z in (zones(i, s + 1) if s < 6 else []) if z[0] == kind]
            if s == 6: top = yt - 30
            else:
                dn = nxt[0][3] if nxt else d
                top = yt + LAP(max(d, dn))
            Lb = int(round(top - yb, -1))
            p = pos_of(d, Lb)
            nb = int(round((x1 - x0) / st)) + 1
            BARS.append(dict(pos=p, d=d, L=Lb, n=2 * nb))
            lay = 'диам%d' % d
            for x in (x0, x1):
                add(t='pl', p=[W(AX1 + x, yb), W(AX1 + x, top)], layer=lay, lw=40)
            # callout on the right of the piece, staggered by zone
            off = {'L': 950, 'M': 0, 'R': -950} if len(zs) == 3 else {'L': 480, 'M': -480, 'R': 480} if len(zs) == 2 else {'L': 0, 'M': 0, 'R': 0}
            ymid = (yb + yt - SLAB) / 2 + off[kind]
            ox = AX1 + PIECES[i][1] + 700
            add(t='note', l1='%d(%%%%C%d)' % (p, d), l2='ш.%d' % st, origin=W(ox, ymid), targets=[W(AX1 + x0, ymid), W(AX1 + x1, ymid)], **NOTE)
        # lap dim for the piece (largest lap at the top of the storey)
        if s < 6:
            lapmax = max(LAP(z[3]) for z in zs)
            xa = AX1 + PIECES[i][0] - 150
            add(t='dim', h=TLAP, p1=W(AX1 + PIECES[i][0], yt), p2=W(AX1 + PIECES[i][0], yt + lapmax), dl=W(xa, yt + lapmax / 2), rot=math.pi / 2, txt='')
# ---- bottom chain of bar positions (basement) ----
for i in range(4):
    a, b = PIECES[i]
    pts = [a] + sorted({v for z in zones(i, 0) for v in (z[1], z[2])}) + [b]
    zz0 = zones(i, 0)
    for (kind, x0, x1, d, st) in zz0:
        n_ = round((x1 - x0) / st); txt = ('%dх%d' % (st, n_)) if n_ > 1 else ''
        tw = 110 * len(txt) / 2 + 150
        tx = {'L': AX1 + x0 - tw, 'R': AX1 + x1 + tw, 'M': AX1 + (x0 + x1) / 2}[kind]
        ty = 13334 if kind != 'M' else 12834
        add(t='dim', h=TDIM, p1=W(AX1 + x0, L[0]), p2=W(AX1 + x1, L[0]), dl=W(AX1 + (x0 + x1) / 2, ty), rot=0, txt=txt, tx=W(tx, ty + 60))
add(t='save')
json.dump(dict(POS={'%d_%d' % k: v for k, v in POS.items()}, BARS=BARS), open('w/sm1_vert.json', 'w'))
json.dump(ops, open('ops/w52.json', 'w'), ensure_ascii=False)
print(len(ops), 'positions', len(POS))
for (d, Lb), p in sorted(POS.items(), key=lambda kv: kv[1]): print(p, 'Ø%d' % d, 'L', Lb, 'n', sum(b['n'] for b in BARS if b['pos'] == p))
if '--run' in sys.argv: print(gx.run(ops, 'w52')[-400:])
