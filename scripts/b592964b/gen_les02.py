# Новая лестница по аналогу «БЦ Лестница 01»: всё, кроме геометрии, из выгрузки аналога.
# Геометрия по эскизу: колонны 6.6 x 2.0, этажи +0.980/+4.780/+8.180/+11.680,
# промежуточные площадки посередине, нижний марш 7 x 140 от +0.980 к земле.
import re, sys

AN, OUT, NAME = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(AN, encoding='utf-8-sig').read()

XL, XR = 0.0, 6.6            # колонны (ось X — вдоль марша)
YC = (0.0, 2.0)              # колонны (Y=2.0 — сторона здания)
YA = (0.10, 0.95)            # косоуры марша «от этажа вверх» (наружная половина)
YB = (1.05, 1.90)            # косоуры марша «к этажу» (у здания)
XJL, XJR = 1.2, 4.8          # границы маршей (1200 / 3600 / 1800)
DLINK = 0.2                  # балка площадки ниже косоура (КЭ55), как в аналоге
YBLD = 2.3                   # опора кронштейна [12П на здании (+0.3, как в аналоге)
FLOORS = [0.98, 4.78, 8.18, 11.68]
TREAD = 0.30
GROUND_RISERS = 7            # 0.980 / 7 = 140 мм

nodes, nid = [], {}
def N(x, y, z):
    k = (round(x, 5), round(y, 5), round(z, 5))
    if k not in nid:
        nodes.append(k); nid[k] = len(nodes)
    return nid[k]

els = []                     # (тип, жесткость, n1, n2, тег)
def E(st, a, b, tag='', typ=10): els.append((typ, st, a, b, tag))

def chain(st, pts, tag):
    ids = [N(*p) for p in pts]
    for a, b in zip(ids, ids[1:]): E(st, a, b, tag)
    return ids

YS = (YA[0], YA[1], YB[0], YB[1])
def ycuts(): return sorted(set((YC[0],) + YS + (YC[1],)))

# --- уровни площадок: (x колонны, уровень верха косоура)
land = []                    # (xcol, z, тип)
for i in range(len(FLOORS) - 1):
    f0, f1 = FLOORS[i], FLOORS[i + 1]
    land.append((XR, f0, 'floor'))
    land.append((XL, (f0 + f1) / 2, 'mid'))
land.append((XR, FLOORS[-1], 'floor'))

risers_info = []
flights = []                 # точки косоуров (st 2)
for i in range(len(FLOORS) - 1):
    f0, f1 = FLOORS[i], FLOORS[i + 1]
    zm = (f0 + f1) / 2
    n = 13                   # 12 проступей x 300 = 3600
    risers_info.append((f1 - f0) / 2 / n)
    for y in YA:             # вверх от этажа (справа) к промежуточной (слева)
        flights.append([(XJR - (XJR - XJL) * k / n, y, f0 + (zm - f0) * k / n) for k in range(n + 1)])
    for y in YB:             # от промежуточной (слева) к этажу (справа)
        flights.append([(XJL + (XJR - XJL) * k / n, y, zm + (f1 - zm) * k / n) for k in range(n + 1)])

# нижний марш: от площадки +0.980 у колонны XR наружу к земле
ng = GROUND_RISERS
xg = XR + TREAD * (ng - 1)
gflights = [[(XR + (xg - XR) * k / ng, y, FLOORS[0] * (1 - k / ng)) for k in range(ng + 1)] for y in YA]

# ===== элементы, сгруппированные по жесткостям =====
# 1 — колонны: разрезаем в уровнях балок и кронштейнов
bracket_z = [f - DLINK for f in FLOORS[:-1]]
for xc in (XL, XR):
    zl = sorted(set([0.0] + [z - DLINK for x, z, t in land if x == xc] + bracket_z))
    ztop = max(z - DLINK for x, z, t in land if x == xc)
    zl = [z for z in zl if z <= ztop + 1e-9]
    for yc in YC:
        chain(1, [(xc, yc, z) for z in zl], 'col')

# 2 — косоуры маршей, горизонтальные косоуры площадок, кромочные балки площадок
for pts in flights + gflights:
    chain(2, pts, 'fl')
for xc, z, t in land:
    xj = XJR if xc == XR else XJL
    for y in YS:
        chain(2, [(xc, y, z), (xj, y, z)], 'ld')
    chain(2, [(xj, y, z) for y in YS], 'edge')   # кромка площадки по границе марша

# 3 — балки площадок по осям колонн
for xc, z, t in land:
    chain(3, [(xc, y, z - DLINK) for y in ycuts()], 'beam')

# 4 — кронштейны к зданию [12П
for xc in (XL, XR):
    for z in bracket_z:
        E(4, N(xc, YC[1], z), N(xc, YBLD, z), 'br')

# 5 — ступени 2L50x4 во внутренних узлах маршей
for pts in flights + gflights:
    pass
def steps(fa, fb):
    for pa, pb in zip(fa[1:-1], fb[1:-1]):
        E(5, N(*pa), N(*pb), 'st')
for i in range(0, len(flights), 2):
    steps(flights[i], flights[i + 1])
steps(gflights[0], gflights[1])

# 6 — КЭ55 балка -> косоур
for xc, z, t in land:
    for y in YS:
        E(6, N(xc, y, z - DLINK), N(xc, y, z), 'lnk', typ=55)

els.sort(key=lambda e: e[1])

# ===== связи =====
sup = []
for xc in (XL, XR):
    for yc in YC: sup.append((N(xc, yc, 0.0), '1 2 3 4 5 6'))
for y in YA: sup.append((N(xg, y, 0.0), '1 2 3'))
for xc in (XL, XR):
    for z in bracket_z: sup.append((N(xc, YBLD, z), '1 2 3'))

# ===== нагрузки (строки документа 7 аналога сохраняем) =====
L = []
sw = {1: 5, 2: 9, 3: 9, 4: 11, 5: 10}
for i, (typ, st, a, b, tag) in enumerate(els, 1):
    if st in sw: L.append(f' {i} 16 3 {sw[st]} 1')
for i, (typ, st, a, b, tag) in enumerate(els, 1):
    if st == 2:
        L += [f' {i} 16 3 6 2', f' {i} 16 3 7 3', f' {i} 16 3 8 4']
for i, (typ, st, a, b, tag) in enumerate(els, 1):
    pa, pb = nodes[a - 1], nodes[b - 1]
    sloped = abs(pa[0] - pb[0]) > 1e-6 and abs(pa[2] - pb[2]) > 1e-6
    if st == 1 or (st == 2 and sloped):
        L += [f' {i} 16 1 1 5', f' {i} 16 1 2 6']
    if st in (1, 2):
        L += [f' {i} 16 2 3 7', f' {i} 16 2 4 8']
d6_an = re.search(r'\(\s*6/(.*?)\n\s*\)', src, re.S).group(1)
mass = [r.strip() for r in d6_an.replace('\n', ' ').split('/') if r.split()[1:2] == ['4']]

def blk(recs, per=4):
    out = []
    for i in range(0, len(recs), per): out.append(' /'.join(recs[i:i + per]) + ' /')
    return '\n'.join(out)

doc1 = '( 1/\n' + blk([f'{t} {s} {a} {b}' for t, s, a, b, _ in els]) + '\n )\n'
doc4 = '( 4/\n' + blk(['%.5f %.5f %.5f' % n for n in nodes]) + '\n )\n'
doc5 = '( 5/\n' + '\n'.join(f'{n} {d} /' for n, d in sup) + '\n\n )\n'
doc6 = '( 6/\n' + blk([l.strip() for l in L] + mass) + '\n\n )\n'

def repl(text, num, new):
    m = re.search(r'\(\s*%d\s*/.*?\n\s*\)\s*\n' % num, text, re.S)
    return text[:m.start()] + new + text[m.end():]
out = src
for num, new in ((1, doc1), (4, doc4), (5, doc5), (6, doc6)):
    out = repl(out, num, new)
out = re.sub(r'\( 0/ 1; [^/]*/', '( 0/ 1; %s/' % NAME, out, count=1)
open(OUT, 'w', encoding='utf-8-sig', newline='\r\n').write(out)

import collections
c = collections.Counter(e[1] for e in els)
print('nodes', len(nodes), 'elems', len(els), dict(sorted(c.items())))
rng = {}
for i, e in enumerate(els, 1): rng.setdefault(e[1], [i, i])[1] = i
print('ranges', rng)
print('risers mm', [round(r * 1000, 1) for r in risers_info], 'ground', round(FLOORS[0] / ng * 1000, 1), 'xg', xg)
print('landings', [(x, round(z, 3), t) for x, z, t in land])
