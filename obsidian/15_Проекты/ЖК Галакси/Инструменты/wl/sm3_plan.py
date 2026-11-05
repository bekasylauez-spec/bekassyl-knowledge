# См-3 sheet 5.12, plan «Разрез 1-1 (Армирования)» M1:50 (drawn x2, broken between the pieces): vertical bar dots, chain,
# dot notes in Bekassyl's style (one level, thin polyline dots -> shelf, text outward), Ск / straight bars of the basement storey.
import sys, os, json, math; sys.path.insert(0, 'wl'); from common import *
from notes import notes
SX, SY = 1427600.0, 455939.0
def W(x, y): return [SX + x, SY + y]
PIECES = [(125, 3225), (9975, 13075)]
BASE = [(9706, 0), (24156, 9975)]                                   # plan x of piece i = BASE[i][0] + 2 * (x - BASE[i][1])
XPi = lambda i, xs: BASE[i][0] + 2 * (xs - BASE[i][1])
YW, YD = 35478, 35584                                               # chain base (wall face), lower dot centre
YA, YB = 34084, 32971                                               # note levels
vj = json.load(open('wl/sm3_vert.json', encoding='utf-8')); hj = json.load(open('wl/sm3_hor.json', encoding='utf-8'))
D = vj['D']; LAB = vj['LABELS']
R = listwin(SX, SY, 59400, 42000, None)
N = notes(SX, SY, 59400, 42000)
PL = lambda r: 30000 < r['y0'] and r['x1'] < 34000
dots = [r for r in R if PL(r) and r['t'] == 'INSERT' and r['lay'].lower().startswith('диам') and r['x1'] - r['x0'] < 300]
tdot = dots[0]; tx0 = (tdot['x0'] + tdot['x1']) / 2
er = [r['h'] for r in dots]
chain = [r for r in R if PL(r) and r['t'] == 'DIMENSION' and abs(r['sp'][0][1] - YW) < 2 and abs(r['sp'][1][1] - YW) < 2]
tdim = chain[0]['h']; er += [r['h'] for r in chain[1:]]
barnotes = [n for n in N if 30000 < n['pts'][0][1] < 40000 and n['pts'][0][0] < 34000 and n['l2'].startswith('ш.') and not n['l1'].startswith(('Х', 'Шп'))]
er += [n['h'] for n in barnotes]
er += [r['h'] for r in R if PL(r) and r['t'] == 'LWPOLYLINE' and r['lay'] == 'Размеры' and len(r['sp']) == 4 and abs(r['sp'][0][1] - YD) < 3 and abs(r['sp'][3][1] - YD) < 3]
er += [r['h'] for r in R if PL(r) and r['t'] == 'LWPOLYLINE' and r['lay'] == 'Размеры' and len(r['sp']) == 2 and abs(r['sp'][0][1] - r['sp'][1][1]) < 1 and min(abs(r['sp'][0][1] - v) for v in (YA, YB)) < 2]
ops = [dict(t='clone', h=tdot['h'], base=[0, 0], to=[0, -300000], tag='S3D'), dict(t='erase', h=er)]
AX = [9706, 30606]; SEGS = []
for i in range(len(PIECES)):
    zs = D[i][0]; XP = lambda xs, i=i: XPi(i, xs)
    for j, z in enumerate(zs):
        kind, x0, x1, d, st = z[:5]
        for xb in z[5]: ops.append(dict(t='clone', h='S3D', base=[0, 0], to=[XP(xb) - tx0, 300000], layer='диам%d' % d))
        lab = LAB['%d|0|%s' % (i, kind)]; l1 = '%s(%%%%C%d)' % (lab, d); l2 = 'ш.%d' % st
        xa, xb = XP(z[5][0]), XP(z[5][-1]); cx = (xa + xb) / 2
        w = 200 * max(len(l1.replace('%%%%C', 'Ф')), len(l2))
        pc = (XP(PIECES[i][0]) + XP(PIECES[i][1])) / 2
        lev2 = len(zs) == 3 and kind == 'M'
        ys = YB if lev2 else YA
        lf, rf = xa + 100, max(xb - 100, xa + 200)
        left = cx <= pc if not lev2 else True
        if left: shelf = [lf - w, rf]; org = lf
        else: shelf = [lf, rf + w]; org = rf + w
        for ax_ in AX:                                          # the text never lies on an axis line
            if org - w - 60 < ax_ < org + 60:
                if left: org = ax_ - 120; shelf[0] = org - w
                else: org = ax_ + 120 + w; shelf[1] = org
        ops.append(dict(t='pl', p=[W(xa, YD), W(lf, ys), W(rf, ys), W(xb, YD)], layer='Размеры'))
        ops.append(dict(t='pl', p=[W(shelf[0], ys), W(shelf[1], ys)], layer='Размеры'))
        tag = 'S3N%d_%d' % (i, j)
        ops.append(dict(t='clone', h='TPA:5D2951', base=[0, 0], to=[0, 0], tag=tag))
        ops.append(dict(t='spmove', h=tag, items=[[0, SX + org, SY + ys]]))
        ops.append(dict(t='mcset', h=tag, set={'FirstLine': l1, 'SecondLine': l2}))
    a_, b_ = PIECES[i]
    for s0, s1, st, n in [(a_, a_ + 50, 50, 1)] + [sg for z in zs for sg in z[6]] + [(b_ - 50, b_, 50, 1)]: SEGS.append((i, s0, s1, st, n))
three = any(len(D[i][0]) == 3 for i in range(len(PIECES)))
RY = [YB - 900, YB - 1350] if three else [YB - 70, YB - 520]
CW = 140; TG = 120; rows = [[] for _ in RY]; items = []
for i, s0, s1, st, n in SEGS:
    XP = lambda xs, i=i: XPi(i, xs)
    a_, b_ = PIECES[i]; txt = ('%dх%d' % (st, n)) if n > 1 else ''
    w = CW * max(len(txt), len(str(int(s1 - s0)))) + 100
    if XP(s1) - XP(s0) >= w: cx, mv = (XP(s0) + XP(s1)) / 2, False
    else:
        cx = XP(s1) + w / 2 + 30 if (s0 + s1) / 2 > (a_ + b_) / 2 else XP(s0) - w / 2 - 30; mv = True
        for ax_ in AX:
            if abs(cx - ax_) < w / 2 + 40: cx = ax_ + (w / 2 + 60) * (1 if cx >= ax_ else -1)
    items.append((cx, w, XP(s0), XP(s1), txt, mv))
for cx0, w, p0, p1, txt, mv in sorted(items):
    cx = cx0
    r = next((j for j in range(len(RY)) if all(cx + w / 2 + TG < c - ww / 2 or cx - w / 2 - TG > c + ww / 2 for c, ww in rows[j])), None)
    if r is None:
        r = min(range(len(RY)), key=lambda j: max(c + ww / 2 for c, ww in rows[j])); cx = max(c + ww / 2 for c, ww in rows[r]) + TG + w / 2; mv = True
    rows[r].append((cx, w))
    kw = dict(t='dim', h=tdim, p1=W(p0, YW), p2=W(p1, YW), dl=W((p0 + p1) / 2, RY[r]), rot=0, txt=txt)
    if mv: kw['tx'] = W(cx, RY[r] + 60)
    ops.append(kw)
ops.append(dict(t='erase', h=[tdim, 'S3D']))
# basement storey: Ск notes and the plan's straight bars / caps -> Ø of the basement horizontal bars
d0 = hj['HD'][0][0]; ck = hj['CKS'][str(d0)] if str(d0) in hj['CKS'] else hj['CKS'][d0]
for n in N:
    if n['pts'][0][0] < 34000 and n['pts'][0][1] > 30000 and n['l1'].startswith('Ск'):
        ops.append(dict(t='mcset', h=n['h'], set={'FirstLine': 'Ск%d' % ck, 'SecondLine': '(%%%%C%d)' % d0}))
ub = [r for r in R if PL(r) and r['t'] in ('LINE', 'LWPOLYLINE') and r['lay'].lower() in ('диам10', 'диам12')]
for r in ub: ops.append(dict(t='clone', h=r['h'], base=[0, 0], to=[0, 0], layer='диам%d' % d0))
if ub: ops.append(dict(t='erase', h=[r['h'] for r in ub]))
ops.append(dict(t='save'))
print('dots', len(dots), 'chain', len(chain), 'notes', len(barnotes), 'Ск', ck, 'd0', d0, 'rows', RY)
if '--run' in sys.argv:
    out = gx.run(ops, 'sm3pl'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
