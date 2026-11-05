# -*- coding: utf-8 -*-
"""АБК завод (Маке) — ЛИРА схемасы: геометрия Заданиеден, жүктеме/сейсмика аналогтан
(«Станция очистки - Цех пред обработки.lir»).  Units: m, t.
usage: py gen_abk.py analog.txt out.txt report.txt plan.png"""
import io, re, sys, math, collections

AN, OUT, REP, PNG = sys.argv[1:5]
TASK = "ABK_zavod"

# ---------------- geometry (Задание) ----------------
AX_X = [6.0 * i for i in range(11)]          # оси 1..11
AX_Y = [0.0, 6.0, 12.0]                       # оси А, Б, В
Z0, Z1, Z2 = -0.80, 3.30, 6.60                # обрез фундамента, перекрытия
Z_STUB_EDGE, Z_STUB_MID = 7.23, 8.13          # оголовки колонн под фермы (разрез 1-1)
OPEN = (48.0, 50.75, 0.0, 4.05)               # лестничный проём на +3.300 (оси 9-10, А-Б)

# ---------------- partitions, 2nd floor (на плите +3.300), mm, local axes ----------------
H_PART = {   # y : [(x1,x2)]
    4050: [(1075, 2900), (3000, 3362), (4262, 6100), (6200, 6550), (7450, 9900), (10000, 10187),
           (11087, 15025), (15125, 15425), (16325, 20962), (21062, 21362), (22262, 24550),
           (25450, 26962), (27062, 27362), (28262, 35025), (35125, 35362), (36262, 38950),
           (39050, 39362), (40262, 42100), (42200, 42550), (43450, 45112), (45212, 45550),
           (46450, 48100), (50800, 51175), (52075, 56900), (57000, 57362), (58262, 59950)],
    5850: [(200, 425), (1325, 2900), (3000, 3362), (4262, 6425), (7325, 8962), (9062, 9362),
           (10262, 12550), (13450, 17212), (17312, 18425), (19325, 22400), (22500, 24425),
           (25325, 27462), (27562, 27925), (28825, 32150), (32250, 32550), (33450, 38187),
           (38287, 38550), (39450, 41800), (48200, 48550), (49450, 54425), (55325, 59800)],
    6950: [(41900, 42452), (43540, 43795), (44695, 45465), (45565, 46520), (47420, 48100)],
    8950: [(43565, 43715), (44615, 45465), (45565, 47037), (47937, 48100)],
    9625: [(41850, 43490)],
    10675: [(46490, 46807), (47790, 48100)],
}
V_PART = {   # x : [(y1,y2)]
    2950: [(50, 4000), (5900, 11950)], 6150: [(200, 4000)], 5850: [(6200, 11800)],
    9012: [(5900, 11950)], 9950: [(50, 4000)], 12150: [(6200, 11800)], 15075: [(50, 4000)],
    17262: [(5900, 11950)], 21012: [(50, 4000)], 22450: [(5900, 11950)],
    24150: [(200, 4000), (4100, 5750)], 27012: [(50, 4000)], 27512: [(5900, 11950)],
    32200: [(5900, 11950)], 35075: [(50, 4000)], 38237: [(5900, 11950)], 39000: [(50, 4000)],
    41850: [(6200, 9625)], 42150: [(200, 4000)],
    43490: [(7000, 9625), (9725, 10625), (10725, 11950)],   # 7000-8800 добавлено по зондированию 44515: [(10725, 11950)],
    45162: [(50, 4000)], 45515: [(7000, 8900), (9000, 10625), (10725, 11950)],
    46857: [(10725, 11950)], 48150: [(200, 4000), (6200, 11800)], 50750: [(50, 4000)],
    53850: [(6200, 11800)], 56950: [(50, 4000)],
}
CORR = [(0.0, 60.0, 4.05, 6.0), (42.0, 48.0, 6.0, 6.95)]   # коридоры 32, 33 (кат. C)

# ---------------- loads, t/m2 / t/m / t ----------------
G_SLAB = 0.2 * 2.5           # плита 200
RO_COL = 0.4 * 0.4 * 2.5     # колонна 400x400
RO_BEAM_DOWN = 0.4 * 0.3 * 2.5   # ригель 400x500: только часть ниже плиты (плита уже в весе пластин)
PIR_FLOOR = 0.243            # пирог пола +3.300 — как в аналоге
PIR_ATTIC = 0.025 + 0.002 + 0.010 + 0.015   # минвата 200 (125 кг/м3) + пароизол. + потолок Армстронг + сети
ROOF_STEEL = 0.036           # профлист Н60 + прогоны + фермы, т/м2 плана
SNOW, SNOW_X = 0.096, 0.192  # как в аналоге
LIVE_B, LIVE_C, LIVE_H = 0.20, 0.30, 0.07
W_EXT = 0.25                 # наружная стена: газоблок 250 + утепл. 100 + вентфасад + штукатурка, т/м2
W_PART = 0.12                # перегородка 100: газоблок D500 + штукатурка 2х15, т/м2
H_PART_SLAB, H_PART_BEAM = 3.1, 2.8
EXT_33 = 0.75                # стена 2 эт. на краевой ригель +3.300, т/м  (2.8 м кладки + фасад 3.3 м)
EXT_66_LONG = 0.30           # парапет до +7.515 по осям А, В
EXT_66_GABLE = 0.565         # фронтон по осям 1, 11 (равномерный эквивалент треугольника)
TRIB_EDGE, TRIB_MID = 3.1, 7.5   # грузовая ширина ферм на опоры А/В и Б (неразрезная, свесы 0.85)
STAIR_G1, STAIR_G2, STAIR_LIVE = 0.89, 0.14, 0.43   # реакция марша на край проёма, т/м
STAIR_X = (49.55, 50.75)

CASES = ["СОБСТВЕННЫЙ ВЕС", "ПОСТОЯННЫЕ ОТ ПИРОГА", "ПОСТОЯННОЕ ОТ СТЕН И ПЕРЕГОРОДОК",
         "ВРЕМЕННОЕ КАТ.B ОФИСЫ", "СНЕГОВАЯ НАГРУЗКА", "ЧРЕЗВЫЧАЙНАЯ СНЕГОВАЯ НАГРУЗКА",
         "ВРЕМЕННОЕ КАТ.Н ЧЕРДАК", "ВРЕМЕННОЕ КАТ.C КОРИДОРЫ, ЛЕСТНИЦА",
         "СЕЙСМИКА ПО Х", "СЕЙСМИКА ПО Y", "СЕЙСМИКА ПО Z"]
MASS = [(1, 1.0), (2, 1.0), (3, 1.0), (4, 0.3), (5, 0.2), (8, 0.6)]   # аналог: 1,1,1,ψ2,0.2
SEIS = [9, 10, 11]

# ---------------- mesh ----------------
ROW = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
def fill(a, b):
    g = round(b - a, 4); n = max(math.ceil(g / 0.6 - 1e-9), int(round(g / 0.5)))
    s = math.floor(g / n / 0.05 + 1e-9) * 0.05; rem = int(round((g - n * s) / 0.05))
    steps = [s] * n
    order = sorted(range(n), key=lambda i: abs(i - (n - 1) / 2))
    for i in order[:rem]: steps[i] += 0.05
    assert all(0.299 < t < 0.601 for t in steps), (a, b, steps)
    pts, c = [], a
    for t in steps[:-1]:
        c = round(c + t, 4); pts.append(c)
    return pts

def snap05(v): return round(round(v / 50.0) * 0.05, 3)
def snap_axis(v, axes):
    for a in axes:
        if abs(v - a) <= 0.30 + 1e-9: return a, True
    return v, False

hp, vp = [], []   # (coord, lo, hi, on_beam)
for y, segs in H_PART.items():
    c, ob = snap_axis(snap05(y), AX_Y)
    for a, b in segs: hp.append((c, a / 1000, b / 1000, ob))
for x, segs in V_PART.items():
    c, ob = snap_axis(snap05(x), AX_X)
    for a, b in segs: vp.append((c, a / 1000, b / 1000, ob))

kx = sorted(set(AX_X + [p[0] for p in vp] + list(STAIR_X) + [OPEN[0], OPEN[1]]))
ky = sorted(set(AX_Y + [p[0] for p in hp] + [OPEN[3]]))
def check_gaps(k):
    for a, b in zip(k, k[1:]): assert b - a >= 0.3 - 1e-9, (a, b)
check_gaps(kx); check_gaps(ky)
X = []; Y = []
for a, b in zip(kx, kx[1:]): X += [a] + fill(a, b)
X.append(kx[-1])
for a, b in zip(ky, ky[1:]): Y += [a] + fill(a, b)
Y.append(ky[-1])
ix = {round(v, 3): i for i, v in enumerate(X)}; iy = {round(v, 3): i for i, v in enumerate(Y)}

nodes = []; nid = {}
def node(x, y, z):
    k = (round(x, 3), round(y, 3), round(z, 3))
    if k not in nid: nodes.append(k); nid[k] = len(nodes)
    return nid[k]
els = []   # (type, stiff, nodes, tag)
def el(t, s, ns, tag): els.append((t, s, ns, tag)); return len(els)

slab = {}   # (z, i, j) -> elem
for z in (Z1, Z2):
    for i in range(len(X) - 1):
        for j in range(len(Y) - 1):
            cx, cy = (X[i] + X[i + 1]) / 2, (Y[j] + Y[j + 1]) / 2
            if z == Z1 and OPEN[0] < cx < OPEN[1] and OPEN[2] < cy < OPEN[3]: continue
            ns = [node(X[i], Y[j], z), node(X[i + 1], Y[j], z), node(X[i], Y[j + 1], z), node(X[i + 1], Y[j + 1], z)]
            slab[(z, i, j)] = el(41, 1, ns, 'slab')
beamx = {}; beamy = {}
for z in (Z1, Z2):
    for y in AX_Y:
        j = iy[y]
        for i in range(len(X) - 1):
            beamx[(z, y, i)] = el(10, 3, [node(X[i], y, z), node(X[i + 1], y, z)], 'beam')
    for x in AX_X:
        i = ix[x]
        for j in range(len(Y) - 1):
            beamy[(z, x, j)] = el(10, 3, [node(x, Y[j], z), node(x, Y[j + 1], z)], 'beam')
supports = []; stubs = {}
for x in AX_X:
    for y in AX_Y:
        n0 = node(x, y, Z0); supports.append(n0)
        el(10, 2, [n0, node(x, y, Z1)], 'col')
        el(10, 2, [node(x, y, Z1), node(x, y, Z2)], 'col')
        # колонна заканчивается на верхней плите +6.600 (замечание пользователя 05.11): оголовков нет
        j = iy[y]
        if j < len(Y) - 1: stubs[(x, y)] = (beamy[(Z2, x, j)], 0.0)            # ригель начинается в узле колонны
        else: stubs[(x, y)] = (beamy[(Z2, x, j - 1)], Y[j] - Y[j - 1])         # ригель заканчивается в узле колонны

# ---------------- loads ----------------
rows = []; rowid = {}
def row(vals):
    k = tuple(round(v, 6) for v in vals)
    if k not in rowid: rows.append(k); rowid[k] = len(rows)
    return rowid[k]
d6 = []
def L(e, kind, case, vals, dr=3): d6.append((e, kind, dr, row(vals), case))
summ = collections.defaultdict(float)
def area(e):
    ns = els[e - 1][2]; a = nodes[ns[0] - 1]; b = nodes[ns[3] - 1]
    return abs(b[0] - a[0]) * abs(b[1] - a[1])
def blen(e):
    a, b = (nodes[n - 1] for n in els[e - 1][2]); return math.dist(a, b)

for e, (t, s, ns, tag) in enumerate(els, 1):
    if tag == 'slab': L(e, 16, 1, (G_SLAB, 0, 0, 0)); summ[1] += G_SLAB * area(e)
    elif tag in ('col', 'stub'): L(e, 16, 1, (RO_COL, 0, 0, 0)); summ[1] += RO_COL * blen(e)
    elif tag == 'beam': L(e, 16, 1, (RO_BEAM_DOWN, 0, 0, 0)); summ[1] += RO_BEAM_DOWN * blen(e)

def in_corr(cx, cy): return any(a < cx < b and c < cy < d for a, b, c, d in CORR)
for (z, i, j), e in slab.items():
    A = area(e); cx, cy = (X[i] + X[i + 1]) / 2, (Y[j] + Y[j + 1]) / 2
    if z == Z1:
        L(e, 16, 2, (PIR_FLOOR, 0, 0, 0)); summ[2] += PIR_FLOOR * A
        if in_corr(cx, cy): L(e, 16, 8, (LIVE_C, 0, 0, 0)); summ[8] += LIVE_C * A
        else: L(e, 16, 4, (LIVE_B, 0, 0, 0)); summ[4] += LIVE_B * A
    else:
        L(e, 16, 2, (PIR_ATTIC, 0, 0, 0)); summ[2] += PIR_ATTIC * A
        L(e, 16, 7, (LIVE_H, 0, 0, 0)); summ[7] += LIVE_H * A

# roof trusses -> concentrated at column top node +6.600 (вид 15 на ригель, привязка a = 0 или L)
for (x, y), (e, ln) in stubs.items():
    s_along = 3.4 if x in (0.0, 60.0) else 6.0
    w = TRIB_MID if y == 6.0 else TRIB_EDGE
    for case, q in ((2, ROOF_STEEL), (5, SNOW), (6, SNOW_X)):
        P = q * s_along * w; L(e, 15, case, (P, ln, 0, 0)); summ[case] += P

# exterior walls on edge beams
for (z, y, i), e in beamx.items():
    if y in (0.0, 12.0):
        q = EXT_33 if z == Z1 else EXT_66_LONG
        L(e, 16, 3, (q, 0, 0, 0)); summ[3] += q * blen(e)
for (z, x, j), e in beamy.items():
    if x in (0.0, 60.0):
        q = EXT_33 if z == Z1 else EXT_66_GABLE
        L(e, 16, 3, (q, 0, 0, 0)); summ[3] += q * blen(e)

# partitions (+3.300)
part_len = collections.defaultdict(float); applied = []
def covered(lo, hi, segs):   # mesh edge [lo,hi] -> partition present at midpoint
    m = (lo + hi) / 2
    return any(a - 1e-6 <= m <= b + 1e-6 for a, b in segs)
hseg = collections.defaultdict(list); vseg = collections.defaultdict(list)
for c, a, b, ob in hp: hseg[(c, ob)].append((a, b))
for c, a, b, ob in vp: vseg[(c, ob)].append((a, b))
for (y, ob), segs in hseg.items():
    q = W_PART * (H_PART_BEAM if ob else H_PART_SLAB)
    j = iy[round(y, 3)]
    for i in range(len(X) - 1):
        if not covered(X[i], X[i + 1], segs): continue
        Lm = X[i + 1] - X[i]
        if ob: L(beamx[(Z1, y, i)], 16, 3, (q, 0, 0, 0))
        else:
            e = slab.get((Z1, i, j)); pr = (1, 2)
            if e is None: e = slab[(Z1, i, j - 1)]; pr = (3, 4)
            L(e, 19, 3, (pr[0], pr[1], q, q))
        summ[3] += q * Lm; part_len['beam' if ob else 'slab'] += Lm; applied.append(('H', y, X[i], X[i + 1], ob))
for (x, ob), segs in vseg.items():
    q = W_PART * (H_PART_BEAM if ob else H_PART_SLAB)
    i = ix[round(x, 3)]
    for j in range(len(Y) - 1):
        if not covered(Y[j], Y[j + 1], segs): continue
        Lm = Y[j + 1] - Y[j]
        if ob: L(beamy[(Z1, x, j)], 16, 3, (q, 0, 0, 0))
        else:
            e = slab.get((Z1, i, j)); pr = (1, 3)
            if e is None: e = slab[(Z1, i - 1, j)]; pr = (2, 4)
            L(e, 19, 3, (pr[0], pr[1], q, q))
        summ[3] += q * Lm; part_len['beam' if ob else 'slab'] += Lm; applied.append(('V', x, Y[j], Y[j + 1], ob))

# stair flight reaction on opening edge y=4.05 (элементы над проёмом -> край j)
jo = iy[OPEN[3]]
for i in range(len(X) - 1):
    if STAIR_X[0] - 1e-6 <= X[i] and X[i + 1] <= STAIR_X[1] + 1e-6:
        e = slab[(Z1, i, jo)]
        for case, q in ((1, STAIR_G1), (2, STAIR_G2), (8, STAIR_LIVE)):
            L(e, 19, case, (1, 2, q, q)); summ[case] += q * (X[i + 1] - X[i])

# mass conversion (вид 4): element field = static case
for sc in SEIS:
    for c, k in MASS: d6.append((c, 4, 1, row((k, 0, 0, 0)), sc))

# ---------------- seismic block from analog ----------------
an = io.open(AN, encoding='utf-8-sig').read()
m15 = re.search(r'\( 15/\n(.*?)\n\s*\)', an, re.S).group(1)
lines15 = [l for l in m15.split('\n') if l.strip()]
d15 = '\n'.join(lines15[:6])           # X, Y, Z (первые три записи, вариант C1*10 аналога)
hdr = re.search(r'\( 0/.*?\n\)', an, re.S).group(0)
tail = {k: re.search(r'\n%s;[^/]*/' % k, hdr).group(0).strip() for k in ('42', '50', '51', '52', '53', '54', '55')}

# ---------------- write ----------------
def recs(items, per=4):
    out = []
    for i in range(0, len(items), per): out.append(''.join(items[i:i + per]))
    return '\n'.join(out)
o = []
o.append('( 0/ 1; %s/ 2; 5/ ' % TASK)
o.append('28; 0 0 1  0 1 0  1 0 0; / ')
o.append('33;M 1 CM 100 T 1 C 1 / ')
o.append('35;\n' + '\n'.join(' %d :  %d;' % (i + 1, c) for i, c in enumerate(SEIS))[:-1] + '; /')
o.append('39;\n' + '\n'.join('%d: %s ;' % (i + 1, n) for i, n in enumerate(CASES)) + '\n /')
for k in ('42', '50', '51', '52', '53', '54', '55'): o.append(tail[k] + '\n')
o.append(')')
o.append('( 1/\n' + recs(['%d %d %s /' % (t, s, ' '.join(map(str, ns))) for t, s, ns, _ in els]) + '\n )')
o.append('''( 3/
1 GEI 3.06e+006 0.2 0.2 RO 2.5 /
2 S0 3.06e+006 40 40/
 0 RO 0.4/
 0 Mu 0.2/
3 S0 3.06e+006 40 50/
 0 RO 0.5/
 0 Mu 0.2/
 )''')
o.append('( 4/\n' + recs(['%.3f %.3f %.3f /' % n for n in nodes], 3) + '\n )')
o.append('( 5/\n' + recs(['%d 1 2 3 4 5 6 /' % n for n in supports]) + '\n )')
o.append('( 6/\n' + recs([' %d %d %d %d %d /' % r for r in d6]) + '\n )')
o.append('( 7/\n' + '\n'.join('%d %s /' % (i + 1, ' '.join(('%g' % v) for v in r)) for i, r in enumerate(rows)) + '\n )')
o.append('( 15/\n' + d15 + '\n\n )')
io.open(OUT, 'w', encoding='utf-8-sig', newline='\r\n').write('\n'.join(o) + '\n')

# ---------------- report ----------------
r = io.open(REP, 'w', encoding='utf-8')
r.write('nodes %d  elements %d (slab %d, beam %d, col %d, stub %d)  supports %d\n' % (
    len(nodes), len(els), sum(1 for e in els if e[3] == 'slab'), sum(1 for e in els if e[3] == 'beam'),
    sum(1 for e in els if e[3] == 'col'), sum(1 for e in els if e[3] == 'stub'), len(supports)))
r.write('mesh X steps %s\nmesh Y %s\n' % (sorted(set(round(b - a, 3) for a, b in zip(X, X[1:]))), Y))
for c in sorted(summ): r.write('case %2d %-40s total %8.2f t\n' % (c, CASES[c - 1], summ[c]))
r.write('partitions on slab %.2f m, on beams %.2f m\n' % (part_len['slab'], part_len['beam']))
r.write('doc15:\n' + d15 + '\n')

# ---------------- plot ----------------
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(30, 7))
for x in X: ax.plot([x, x], [0, 12], color='#eee', lw=0.3)
for y in Y: ax.plot([0, 60], [y, y], color='#eee', lw=0.3)
for x in AX_X: ax.plot([x, x], [0, 12], 'b-', lw=1.5)
for y in AX_Y: ax.plot([0, 60], [y, y], 'b-', lw=1.5)
ax.add_patch(plt.Rectangle((OPEN[0], OPEN[2]), OPEN[1] - OPEN[0], OPEN[3] - OPEN[2], color='#ccc'))
for o_, c, a, b, ob in applied:
    xs, ys = ([a, b], [c, c]) if o_ == 'H' else ([c, c], [a, b])
    ax.plot(xs, ys, color='m' if ob else 'r', lw=3)
for x in AX_X:
    for y in AX_Y: ax.add_patch(plt.Rectangle((x - .2, y - .2), .4, .4, color='k'))
for a, b, c, d in CORR: ax.add_patch(plt.Rectangle((a, c), b - a, d - c, color='y', alpha=.25))
ax.set_aspect('equal'); ax.set_xlim(-1, 61); ax.set_ylim(-1, 13)
ax.set_title('+3.300: перегородки на плите (красн.), на ригеле (фиол.), коридор кат.C (жёлт.), проём лестницы (сер.)')
fig.savefig(PNG, dpi=70, bbox_inches='tight')
print(io.open(REP, encoding='utf-8').read())
