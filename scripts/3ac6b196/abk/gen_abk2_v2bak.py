# -*- coding: utf-8 -*-
"""АБК завод (Маке) — ЛИРА схема v2.
Геометрия: Задание (оси, планы, разрез) + КЖ Чертеж АБК.dwg (Фм-1, См-1, Км-1, Пм-1, Рм-1/2).
Схема фундамента/стенки как в аналоге «алк от булаев.lir»; сейсмика и массы — «Станция очистки».
usage: py gen_abk2.py analog_stoch.txt p1part.json out.txt report.txt plan_prefix
Units: m, t."""
import io, re, sys, math, json, collections

AN, P1, OUT, REP, PNG = sys.argv[1:6]
TASK = "ABK_zavod"

# ---------------- geometry ----------------
AX_X = [6.0 * i for i in range(11)]          # оси 1..11
AX_Y = [0.0, 6.0, 12.0]                       # оси А, Б, В
ZF, Z0, Z1, Z2 = -2.00, 0.00, 3.30, 6.60      # верх Фм-1 / низ См-1, Пм-1, перекрытия
ZW = [-2.0, -1.5, -1.0, -0.5, 0.0]            # сетка стенки См-1 по высоте
OPEN = (48.0, 50.75, 0.0, 4.05)               # лестничный проём на +3.300 (оси 9-10, А-Б)
STAIR_X1, STAIR_X2 = (48.0, 49.45), (49.45, 50.75)   # нижний / верхний марш
PAD = 1.0                                     # Фм-1: подушка 2000x2000 (полуширина)
C1 = 168.0                                    # т/м3 — среднее по аналогу «алк от булаев» (105…305)

# ---------------- partitions ----------------
H2 = {4050: [(1075, 2900), (3000, 3362), (4262, 6100), (6200, 6550), (7450, 9900), (10000, 10187),
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
      9625: [(41850, 43490)], 10675: [(46490, 46807), (47790, 48100)]}
V2 = {2950: [(50, 4000), (5900, 11950)], 6150: [(200, 4000)], 5850: [(6200, 11800)],
      9012: [(5900, 11950)], 9950: [(50, 4000)], 12150: [(6200, 11800)], 15075: [(50, 4000)],
      17262: [(5900, 11950)], 21012: [(50, 4000)], 22450: [(5900, 11950)],
      24150: [(200, 4000), (4100, 5750)], 27012: [(50, 4000)], 27512: [(5900, 11950)],
      32200: [(5900, 11950)], 35075: [(50, 4000)], 38237: [(5900, 11950)], 39000: [(50, 4000)],
      41850: [(6200, 9625)], 42150: [(200, 4000)],
      43490: [(7000, 9625), (9725, 10625), (10725, 11950)], 44515: [(10725, 11950)],
      45162: [(50, 4000)], 45515: [(7000, 8900), (9000, 10625), (10725, 11950)],
      46857: [(10725, 11950)], 48150: [(200, 4000), (6200, 11800)], 50750: [(50, 4000)],
      53850: [(6200, 11800)], 56950: [(50, 4000)]}

def plan1():
    """1 этаж: пары линий 100 мм из плана Задания (part.py), без ложных пар с осями."""
    d = json.load(open(P1)); X0, Y0 = -167624, 7160
    H = collections.defaultdict(list); V = collections.defaultdict(list)
    for o, D, axes in (('H', H, [0, 6000, 12000]), ('V', V, list(range(0, 60001, 6000)))):
        for c, a, b, g in d[o]:
            if b - a < 250: continue
            c = c - (Y0 if o == 'H' else X0); a -= (X0 if o == 'H' else Y0); b -= (X0 if o == 'H' else Y0)
            if any(abs(c - ax) < 60 for ax in axes): continue      # пара «перегородка + ось»
            D[round(c)].append((round(a), round(b)))
    return H, V
H1, V1 = plan1()

# ---------------- loads, t/m2 / t/m / t ----------------
G_SLAB = 0.2 * 2.5; G_WALL = 0.2 * 2.5; G_PAD = 0.3 * 2.5
RO_COL = 0.4 * 0.4 * 2.5; RO_STRIP = 0.5 * 0.3 * 2.5
RO_BEAM_DOWN = 0.3 * 0.3 * 2.5                # Рм 300x500: часть ниже плиты
PIR_FLOOR = 0.243                             # пол 0.000 и +3.300 — как в аналоге
PIR_ATTIC = 0.025 + 0.002 + 0.010 + 0.015
SOIL_PAD = 1.8 * 1.8                          # грунт обратной засыпки на подушке (1.8 м x 1.8 т/м3)
SOIL_STRIP = (0.5 - 0.2) * 1.8 * 1.8          # грунт на обрезах ленты
ROOF_STEEL = 0.036
SNOW, SNOW_X = 0.096, 0.192
LIVE_B, LIVE_C, LIVE_H, LIVE_1 = 0.20, 0.30, 0.07, 0.40   # 1 эт.: столовая/пищеблок/кладовые
W_PART = 0.12
H_PART_SLAB, H_PART_BEAM = 3.1, 2.8
EXT_00 = EXT_33 = 0.75; EXT_66_LONG = 0.30; EXT_66_GABLE = 0.565
TRIB_EDGE, TRIB_MID = 3.1, 7.5
STAIR_G1, STAIR_G2, STAIR_LIVE = 0.89, 0.14, 0.43
W0, KZ, CW, CL = 0.039, 0.75, 0.8, 0.5        # ветер: w0 (Алматы), k(z), напор / отсос
HW = {Z1: 4.95, Z2: 2.6}; HW_GABLE = 3.6      # грузовые высоты фасада на ригель

CASES = ["СОБСТВЕННЫЙ ВЕС", "ПОСТОЯННЫЕ ОТ ПИРОГА И ГРУНТА", "ПОСТОЯННОЕ ОТ СТЕН И ПЕРЕГОРОДОК",
         "ВРЕМЕННОЕ КАТ.B ОФИСЫ", "СНЕГОВАЯ НАГРУЗКА", "ЧРЕЗВЫЧАЙНАЯ СНЕГОВАЯ НАГРУЗКА",
         "ВРЕМЕННОЕ КАТ.Н ЧЕРДАК", "ВРЕМЕННОЕ КАТ.C КОРИДОРЫ, ЛЕСТНИЦА",
         "ВЕТЕР ПО +X", "ВЕТЕР ПО -X", "ВЕТЕР ПО +Y", "ВЕТЕР ПО -Y",
         "СЕЙСМИКА ПО Х", "СЕЙСМИКА ПО Y", "СЕЙСМИКА ПО Z"]
MASS = [(1, 1.0), (2, 1.0), (3, 1.0), (4, 0.3), (5, 0.2), (8, 0.6)]
SEIS = [13, 14, 15]

# ---------------- mesh keys ----------------
def fill(a, b):
    g = round(b - a, 4); n = max(math.ceil(g / 0.6 - 1e-9), int(round(g / 0.5)))
    s = math.floor(g / n / 0.05 + 1e-9) * 0.05; rem = int(round((g - n * s) / 0.05))
    steps = [s] * n
    for i in sorted(range(n), key=lambda i: abs(i - (n - 1) / 2))[:rem]: steps[i] += 0.05
    assert all(0.299 < t < 0.601 for t in steps), (a, b, steps)
    pts, c = [], a
    for t in steps[:-1]: c = round(c + t, 4); pts.append(c)
    return pts
def snap05(v): return round(round(v / 50.0) * 0.05, 3)
def keyset(base, cands):
    k = sorted(set(base))
    for c in sorted(cands, key=lambda t: -t[1]):           # длинные перегородки — первыми
        if all(abs(c[0] - v) >= 0.3 - 1e-9 for v in k): k.append(c[0]); k.sort()
    return k
def nearest(v, k): return min(k, key=lambda t: abs(t - v))

parts = []   # (floor_z, orient, coord_raw, lo, hi)
for z, H, V in ((Z1, H2, V2),):   # плита по грунту в ЛИРА не моделируется (пользователь 05.11)
    for y, segs in H.items():
        for a, b in segs: parts.append((z, 'H', snap05(y), a / 1000, b / 1000))
    for x, segs in V.items():
        for a, b in segs: parts.append((z, 'V', snap05(x), a / 1000, b / 1000))
lenx = collections.Counter(); leny = collections.Counter()
for z, o, c, a, b in parts:
    if o == 'V' and all(abs(c - ax) > 0.3 for ax in AX_X): lenx[c] += b - a
    if o == 'H' and all(abs(c - ax) > 0.3 for ax in AX_Y): leny[c] += b - a
kx = keyset(AX_X + [OPEN[0], OPEN[1], STAIR_X1[1]], lenx.items())
ky = keyset(AX_Y + [OPEN[3]], leny.items())
X = []; Y = []
for a, b in zip(kx, kx[1:]): X += [a] + fill(a, b)
X.append(kx[-1])
for a, b in zip(ky, ky[1:]): Y += [a] + fill(a, b)
Y.append(ky[-1])
ix = {round(v, 3): i for i, v in enumerate(X)}; iy = {round(v, 3): i for i, v in enumerate(Y)}
# partitions snapped to keys; on an axis -> «на ригеле/по оси»
P = []
for z, o, c, a, b in parts:
    axes = AX_Y if o == 'H' else AX_X
    ax = [t for t in axes if abs(c - t) <= 0.3 + 1e-9]
    if ax: P.append((z, o, ax[0], a, b, True))
    else: P.append((z, o, nearest(c, ky if o == 'H' else kx), a, b, False))

# ---------------- elements ----------------
nodes = []; nid = {}
def node(x, y, z):
    k = (round(x, 3), round(y, 3), round(z, 3))
    if k not in nid: nodes.append(k); nid[k] = len(nodes)
    return nid[k]
els = []
def el(t, s, ns, tag): els.append((t, s, ns, tag)); return len(els)
# stiffness: 1 плита 200 (+3.3/+6.6), 2 колонна 40x40, 3 ригель 30x50, 4 стенка См-1 200,
#            5 подушка Фм-1 300, 6 лента Фм-1 50x30, 7 плита Пм-1 200 (0.000)
slab = {}
for z, st in ((Z1, 1), (Z2, 1)):
    for i in range(len(X) - 1):
        for j in range(len(Y) - 1):
            cx, cy = (X[i] + X[i + 1]) / 2, (Y[j] + Y[j + 1]) / 2
            if z == Z1 and OPEN[0] < cx < OPEN[1] and OPEN[2] < cy < OPEN[3]: continue
            ns = [node(X[i], Y[j], z), node(X[i + 1], Y[j], z), node(X[i], Y[j + 1], z), node(X[i + 1], Y[j + 1], z)]
            slab[(z, i, j)] = el(41, st, ns, 'slab%d' % st)
beamx = {}; beamy = {}
for z in (Z1, Z2):
    for y in AX_Y:
        for i in range(len(X) - 1): beamx[(z, y, i)] = el(10, 3, [node(X[i], y, z), node(X[i + 1], y, z)], 'beam')
    for x in AX_X:
        for j in range(len(Y) - 1): beamy[(z, x, j)] = el(10, 3, [node(x, Y[j], z), node(x, Y[j + 1], z)], 'beam')
for x in AX_X:
    for y in AX_Y:
        for za, zb in ((ZF, Z0), (Z0, Z1), (Z1, Z2)): el(10, 2, [node(x, y, za), node(x, y, zb)], 'col')
# стенка См-1 по периметру
wall = []
for y in (0.0, 12.0):
    for i in range(len(X) - 1):
        for k in range(len(ZW) - 1):
            wall.append(el(44, 4, [node(X[i], y, ZW[k + 1]), node(X[i], y, ZW[k]), node(X[i + 1], y, ZW[k + 1]), node(X[i + 1], y, ZW[k])], 'wall'))
for x in (0.0, 60.0):
    for j in range(len(Y) - 1):
        for k in range(len(ZW) - 1):
            wall.append(el(44, 4, [node(x, Y[j], ZW[k + 1]), node(x, Y[j], ZW[k]), node(x, Y[j + 1], ZW[k + 1]), node(x, Y[j + 1], ZW[k])], 'wall'))
# Фм-1: подушки 2000x2000 + ленты 500 под стенкой
def padcoords(c, mesh, lo, hi):
    """узлы подушки: точно c±1.0 (габарит 2000), внутри — узлы общей сетки (стыковка со стенкой), шаг >= 0.15"""
    pts = [round(c - PAD, 3), round(c + PAD, 3)]
    pts += [v for v in mesh if c - PAD + 0.25 <= v <= c + PAD - 0.25]
    for o in (-PAD / 2, PAD / 2):
        v = round(c + o, 3)
        if all(abs(v - p) > 0.25 for p in pts): pts.append(v)
    return sorted(set(pts))
pads = []; padbox = []
for x in AX_X:
    for y in AX_Y:
        px = padcoords(x, X, 0.0, 60.0); py = padcoords(y, Y, 0.0, 12.0)
        padbox.append((px[0], px[-1], py[0], py[-1]))
        for i in range(len(px) - 1):
            for j in range(len(py) - 1):
                pads.append(el(41, 5, [node(px[i], py[j], ZF), node(px[i + 1], py[j], ZF), node(px[i], py[j + 1], ZF), node(px[i + 1], py[j + 1], ZF)], 'pad'))
def inpad(x, y): return any(a - 1e-6 <= x <= b + 1e-6 and c - 1e-6 <= y <= d + 1e-6 for a, b, c, d in padbox)
strips = []
for y in (0.0, 12.0):
    for i in range(len(X) - 1):
        if not inpad((X[i] + X[i + 1]) / 2, y): strips.append(el(10, 6, [node(X[i], y, ZF), node(X[i + 1], y, ZF)], 'strip'))
for x in (0.0, 60.0):
    for j in range(len(Y) - 1):
        if not inpad(x, (Y[j] + Y[j + 1]) / 2): strips.append(el(10, 6, [node(x, Y[j], ZF), node(x, Y[j + 1], ZF)], 'strip'))
fnodes = sorted({n for e in pads + strips for n in els[e - 1][2]})

# ---------------- loads ----------------
rows = []; rowid = {}
def row(vals):
    k = tuple(round(v, 6) for v in vals)
    if k not in rowid: rows.append(k); rowid[k] = len(rows)
    return rowid[k]
d6 = []; summ = collections.defaultdict(float)
def L(e, kind, case, vals, dr=3): d6.append((e, kind, dr, row(vals), case))
def area(e):
    p = [nodes[n - 1] for n in els[e - 1][2]]
    return math.dist(p[0], p[1]) * math.dist(p[0], p[2])
def blen(e):
    a, b = (nodes[n - 1] for n in els[e - 1][2]); return math.dist(a, b)
for e, (t, s, ns, tag) in enumerate(els, 1):
    if t in (41, 44):
        q = {1: G_SLAB, 7: G_SLAB, 4: G_WALL, 5: G_PAD}[s]; L(e, 16, 1, (q, 0, 0, 0)); summ[1] += q * area(e)
    else:
        q = {'col': RO_COL, 'beam': RO_BEAM_DOWN, 'strip': RO_STRIP}[tag]; L(e, 16, 1, (q, 0, 0, 0)); summ[1] += q * blen(e)
def in_corr(cx, cy): return any(a < cx < b and c < cy < d for a, b, c, d in [(0.0, 60.0, 4.05, 6.0), (42.0, 48.0, 6.0, 6.95)])
for (z, i, j), e in slab.items():
    A = area(e); cx, cy = (X[i] + X[i + 1]) / 2, (Y[j] + Y[j + 1]) / 2
    if z == Z0:
        L(e, 16, 2, (PIR_FLOOR, 0, 0, 0)); summ[2] += PIR_FLOOR * A
        L(e, 16, 8, (LIVE_1, 0, 0, 0)); summ[8] += LIVE_1 * A
    elif z == Z1:
        L(e, 16, 2, (PIR_FLOOR, 0, 0, 0)); summ[2] += PIR_FLOOR * A
        if in_corr(cx, cy): L(e, 16, 8, (LIVE_C, 0, 0, 0)); summ[8] += LIVE_C * A
        else: L(e, 16, 4, (LIVE_B, 0, 0, 0)); summ[4] += LIVE_B * A
    else:
        L(e, 16, 2, (PIR_ATTIC, 0, 0, 0)); summ[2] += PIR_ATTIC * A
        L(e, 16, 7, (LIVE_H, 0, 0, 0)); summ[7] += LIVE_H * A
for e in pads: L(e, 16, 2, (SOIL_PAD, 0, 0, 0)); summ[2] += SOIL_PAD * area(e)
for e in strips: L(e, 16, 2, (SOIL_STRIP, 0, 0, 0)); summ[2] += SOIL_STRIP * blen(e)
# фермы -> узлы верха колонн +6.600 (вид 15 на ригель)
for x in AX_X:
    for y in AX_Y:
        j = iy[y]
        e, a = (beamy[(Z2, x, j)], 0.0) if j < len(Y) - 1 else (beamy[(Z2, x, j - 1)], Y[j] - Y[j - 1])
        s_al = 3.4 if x in (0.0, 60.0) else 6.0; w = TRIB_MID if y == 6.0 else TRIB_EDGE
        for case, q in ((2, ROOF_STEEL), (5, SNOW), (6, SNOW_X)):
            Pq = q * s_al * w; L(e, 15, case, (Pq, a, 0, 0)); summ[case] += Pq
# наружные стены
def slab_edge(z, o, c, lo, hi):
    """элементы плиты z с ребром на линии o=c между lo..hi -> [(e, pair, len)]"""
    out = []
    if o == 'H':
        j = iy[round(c, 3)]
        for i in range(len(X) - 1):
            m = (X[i] + X[i + 1]) / 2
            if lo - 1e-6 <= m <= hi + 1e-6:
                e = slab.get((z, i, j)); pr = (1, 2)
                if e is None: e = slab.get((z, i, j - 1)); pr = (3, 4)
                if e: out.append((e, pr, X[i + 1] - X[i]))
    else:
        i = ix[round(c, 3)]
        for j in range(len(Y) - 1):
            m = (Y[j] + Y[j + 1]) / 2
            if lo - 1e-6 <= m <= hi + 1e-6:
                e = slab.get((z, i, j)); pr = (1, 3)
                if e is None: e = slab.get((z, i - 1, j)); pr = (2, 4)
                if e: out.append((e, pr, Y[j + 1] - Y[j]))
    return out
for o, c, lo, hi in (('H', 0.0, 0, 60), ('H', 12.0, 0, 60), ('V', 0.0, 0, 12), ('V', 60.0, 0, 12)):
    pass
# наружная стена 1 этажа -> верх стенки См-1 (0.000), ребро 1-3 КЭ 44
for e in wall:
    p = [nodes[n - 1] for n in els[e - 1][2]]
    if abs(p[0][2] - Z0) < 1e-6:
        ln = math.dist(p[0], p[2]); L(e, 19, 3, (1, 3, EXT_00, EXT_00)); summ[3] += EXT_00 * ln
for (z, y, i), e in beamx.items():
    if y in (0.0, 12.0):
        q = EXT_33 if z == Z1 else EXT_66_LONG; L(e, 16, 3, (q, 0, 0, 0)); summ[3] += q * blen(e)
for (z, x, j), e in beamy.items():
    if x in (0.0, 60.0):
        q = EXT_33 if z == Z1 else EXT_66_GABLE; L(e, 16, 3, (q, 0, 0, 0)); summ[3] += q * blen(e)
# перегородки
plen = collections.defaultdict(float); applied = []
grp = collections.defaultdict(list)
for z, o, c, a, b, ob in P: grp[(z, o, c, ob)].append((a, b))
for (z, o, c, ob), segs in grp.items():
    q = W_PART * (H_PART_BEAM if ob else H_PART_SLAB)
    mesh = X if o == 'H' else Y
    for k in range(len(mesh) - 1):
        m = (mesh[k] + mesh[k + 1]) / 2
        if not any(a - 1e-6 <= m <= b + 1e-6 for a, b in segs): continue
        ln = mesh[k + 1] - mesh[k]
        if ob and z == Z1:
            L((beamx[(z, c, k)] if o == 'H' else beamy[(z, c, k)]), 16, 3, (q, 0, 0, 0))
        else:
            se = slab_edge(z, o, c, mesh[k], mesh[k + 1])
            if not se: continue
            e, pr, _ = se[0]; L(e, 19, 3, (pr[0], pr[1], q, q))
        summ[3] += q * ln; plen[(z, 'beam' if ob else 'slab')] += ln; applied.append((z, o, c, mesh[k], mesh[k + 1], ob))
# лестница: верхний марш -> край проёма +3.300, нижний марш -> плита 0.000 по той же линии
for z, sx in ((Z1, STAIR_X2),):
    for e, pr, ln in slab_edge(z, 'H', OPEN[3], *sx):
        for case, q in ((1, STAIR_G1), (2, STAIR_G2), (8, STAIR_LIVE)):
            L(e, 19, case, (pr[0], pr[1], q, q)); summ[case] += q * ln
# ветер (нормативный): напор на наветренный, отсос на подветренный — оба в направлении ветра
for (z, x, j), e in beamy.items():
    if x in (0.0, 60.0):
        h = HW[z] if z == Z1 else HW_GABLE
        for case, sgn, windward in ((9, -1, 0.0), (10, 1, 60.0)):
            q = W0 * KZ * (CW if x == windward else CL) * h; L(e, 16, case, (sgn * q, 0, 0, 0), dr=1); summ[case] += q * blen(e)
for (z, y, i), e in beamx.items():
    if y in (0.0, 12.0):
        h = HW[z]
        for case, sgn, windward in ((11, -1, 0.0), (12, 1, 12.0)):
            q = W0 * KZ * (CW if y == windward else CL) * h; L(e, 16, case, (sgn * q, 0, 0, 0), dr=2); summ[case] += q * blen(e)
for sc in SEIS:
    for c, k in MASS: d6.append((c, 4, 1, row((k, 0, 0, 0)), sc))

# ---------------- seismic from analog ----------------
an = io.open(AN, encoding='utf-8-sig').read()
m15 = re.search(r'\( 15/\n(.*?)\n\s*\)', an, re.S).group(1)
d15 = '\n'.join([l for l in m15.split('\n') if l.strip()][:6])
AG = 4.709   # 9 баллов: ag = 0.480g (как Байтурсынова 50, участок II-А-1), грунт II
assert d15.count(' 5.300 ') == 3
d15 = d15.replace(' 5.300 ', ' %.3f ' % AG)
hdr = re.search(r'\( 0/.*?\n\)', an, re.S).group(0)
tail = {k: re.search(r'\n%s;[^/]*/' % k, hdr).group(0).strip() for k in ('42', '50', '51', '52', '53', '54', '55')}

# ---------------- write ----------------
def recs(items, per=4): return '\n'.join(''.join(items[i:i + per]) for i in range(0, len(items), per))
for n in CASES: assert '(' not in n and ')' not in n
o = ['( 0/ 1; %s/ 2; 5/ ' % TASK, '28; 0 0 1  0 1 0  1 0 0; / ', '33;M 1 CM 100 T 1 C 1 / ',
     '35;\n' + '\n'.join(' %d :  %d;' % (i + 1, c) for i, c in enumerate(SEIS))[:-1] + '; /',
     '39;\n' + '\n'.join('%d: %s ;' % (i + 1, n) for i, n in enumerate(CASES)) + '\n /']
for k in ('42', '50', '51', '52', '53', '54', '55'): o.append(tail[k] + '\n')
o.append(')')
o.append('( 1/\n' + recs(['%d %d %s /' % (t, s, ' '.join(map(str, ns))) for t, s, ns, _ in els]) + '\n )')
o.append('''( 3/
1 GEI 3.06e+006 0.2 0.2 RO 2.5 /
2 S0 3.06e+006 40 40/
 0 RO 0.4/
 0 Mu 0.2/
3 S0 3.06e+006 30 50/
 0 RO 0.375/
 0 Mu 0.2/
4 GEI 3.06e+006 0.2 0.2 RO 2.5 /
5 GEI 3.06e+006 0.2 0.3 RO 2.5 /
6 S0 3.06e+006 50 30/
 0 RO 0.375/
 0 Mu 0.2/
7 GEI 3.06e+006 0.2 0.2 RO 2.5 /
 )''')
o.append('( 4/\n' + recs(['%.3f %.3f %.3f /' % n for n in nodes], 3) + '\n )')
o.append('( 5/\n' + recs(['%d 1 2 6 /' % n for n in fnodes]) + '\n )')
o.append('( 6/\n' + recs([' %d %d %d %d %d /' % r for r in d6]) + '\n )')
o.append('( 7/\n' + '\n'.join('%d %s /' % (i + 1, ' '.join(('%g' % v) for v in r)) for i, r in enumerate(rows)) + '\n )')
o.append('( 15/\n' + d15 + '\n\n )')
o.append('( 19/\n' + '\n'.join(['%d %g 0 0 0 0/' % (e, C1) for e in pads] + ['%d 0.5 %g 0 0 0 0 0 0/' % (e, C1) for e in strips]) + '\n )')
io.open(OUT, 'w', encoding='utf-8-sig', newline='\r\n').write('\n'.join(o) + '\n')

# ---------------- report + plots ----------------
r = io.open(REP, 'w', encoding='utf-8')
cnt = collections.Counter(e[3] for e in els)
r.write('nodes %d elements %d %s; supports %d; pads %d strips %d\n' % (len(nodes), len(els), dict(cnt), len(fnodes), len(pads), len(strips)))
r.write('X keys %s\nY keys %s\n' % (kx, ky))
r.write('mesh steps X %s Y %s\n' % (sorted(set(round(b - a, 3) for a, b in zip(X, X[1:]))), sorted(set(round(b - a, 3) for a, b in zip(Y, Y[1:])))))
for c in sorted(summ): r.write('case %2d %-45s %9.2f t\n' % (c, CASES[c - 1], summ[c]))
for k, v in sorted(plen.items()): r.write('partitions z=%s %s: %.2f m\n' % (k[0], k[1], v))
r.close()
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
for z, nm in ((Z0, '0.000'), (Z1, '+3.300')):
    fig, ax = plt.subplots(figsize=(30, 7))
    for x in AX_X: ax.plot([x, x], [0, 12], 'b-', lw=1.2)
    for y in AX_Y: ax.plot([0, 60], [y, y], 'b-', lw=1.2)
    if z == Z1: ax.add_patch(plt.Rectangle((OPEN[0], OPEN[2]), OPEN[1] - OPEN[0], OPEN[3] - OPEN[2], color='#ccc'))
    for zz, o_, c, a, b, ob in applied:
        if zz != z: continue
        xs, ys = ([a, b], [c, c]) if o_ == 'H' else ([c, c], [a, b])
        ax.plot(xs, ys, color='m' if ob else 'r', lw=3)
    for a, b, c, d in padbox: ax.add_patch(plt.Rectangle((a, c), b - a, d - c, fill=False, ec='g', lw=0.8))
    ax.set_aspect('equal'); ax.set_xlim(-1.5, 61.5); ax.set_ylim(-1.5, 13.5)
    ax.set_title('%s: перегородки на плите (красн.), по оси (фиол.); Фм-1 подушки (зел.)' % nm)
    fig.savefig('%s_%s.png' % (PNG, nm.replace('+', 'p')), dpi=70, bbox_inches='tight'); plt.close(fig)
print(io.open(REP, encoding='utf-8').read())
