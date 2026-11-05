# См-4 sheet 5.15, plan «Разрез 1-1 (Армирование)» M1:50 (x2): piece A = analog (kept), piece B (11750..13250, axis 3) added right of A.
# B: dots, chain, dot notes in Bekassyl's style, Ск label of the basement horizontal bars; axes 2 (wall face) and 3, dim 2-3.
import sys, os, json, math; sys.path.insert(0, 'wl'); from common import *
from notes import notes
SX, SY = 1637700.0, 455939.0
def W(x, y): return [SX + x, SY + y]
PB = (7050, 10400)
XP = lambda x: 43322 + 2 * (x - 7050)
YW, YD = 25390, 25496
YA, YB = 23996, 22883
AX = [42822]
vj = json.load(open('wl/sm5_vert.json', encoding='utf-8')); hj = json.load(open('wl/sm5_hor.json', encoding='utf-8'))
D = vj['D'][0][0]; LAB = vj['LABELS']
R = listwin(SX, SY, 59400, 42000, None)
N = notes(SX, SY, 59400, 42000)
inB = lambda r: 41000 < r['x0'] and r['x1'] < 56000 and 15000 < r['y0'] < 30000
tdot = next(r for r in R if r['t'] == 'INSERT' and r['lay'].startswith('диам') and r['x1'] - r['x0'] < 300 and 40000 < r['x0'] < 56000 and 24000 < r['y0'] < 27000)
tx0 = (tdot['x0'] + tdot['x1']) / 2
er = [r['h'] for r in R if inB(r) and r['t'] == 'INSERT' and r['lay'].startswith('диам') and r['x1'] - r['x0'] < 300]
chain = [r for r in R if inB(r) and r['t'] == 'DIMENSION' and abs(r['sp'][0][1] - YW) < 2]
tdim = chain[0]['h']; er += [r['h'] for r in chain[1:]]
er += [n['h'] for n in N if 41000 < n['pts'][0][0] < 56000 and 15000 < n['pts'][0][1] < 30000 and len(n['pts']) == 1 and n['l2'].startswith('ш.') and not n['l1'].startswith(('Х', 'Шп'))]
er += [r['h'] for r in R if inB(r) and r['t'] == 'LWPOLYLINE' and r['lay'] == 'Размеры' and len(r['sp']) == 4 and (abs(r['sp'][0][1] - YD) < 3 or abs(r['sp'][0][1] - 25784) < 3)]
er += [r['h'] for r in R if inB(r) and r['t'] == 'LWPOLYLINE' and r['lay'] == 'Размеры' and len(r['sp']) == 2 and abs(r['sp'][0][1] - r['sp'][1][1]) < 1 and min(abs(r['sp'][0][1] - v) for v in (YA, YB)) < 2]
ops = [dict(t='clone', h=tdot['h'], base=[0, 0], to=[0, -300000], tag='S5D'), dict(t='erase', h=er)]
pc = (XP(PB[0]) + XP(PB[1])) / 2; SEGS = []
for j, z in enumerate(D):
    kind, x0, x1, d, st = z[:5]
    for xb in z[5]: ops.append(dict(t='clone', h='S5D', base=[0, 0], to=[XP(xb) - tx0, 300000], layer='диам%d' % d))
    lab = LAB['0|0|%s' % kind]; l1 = '%s(%%%%C%d)' % (lab, d); l2 = 'ш.%d' % st
    xa, xb = XP(z[5][0]), XP(z[5][-1]); cx = (xa + xb) / 2
    w = 200 * max(len(l1.replace('%%%%C', 'Ф')), len(l2))
    lf, rf = xa + 100, max(xb - 100, xa + 200)
    left = False; ys = YA
    if left: shelf = [lf - w, rf]; org = lf
    else: shelf = [lf, rf + w]; org = rf + w
    for ax_ in AX:
        if org - w - 60 < ax_ < org + 60:
            if left: org = ax_ - 120; shelf[0] = org - w
            else: org = ax_ + 120 + w; shelf[1] = org
    if not left and org > 58700: ys = YB; shelf = [lf - w, rf]; org = lf      # no room at the frame: lower level, text inward
    ops.append(dict(t='pl', p=[W(xa, YD), W(lf, ys), W(rf, ys), W(xb, YD)], layer='Размеры'))
    ops.append(dict(t='pl', p=[W(shelf[0], ys), W(shelf[1], ys)], layer='Размеры'))
    tag = 'S5N_%d' % j
    ops.append(dict(t='clone', h='TPA:5D2951', base=[0, 0], to=[0, 0], tag=tag))
    ops.append(dict(t='spmove', h=tag, items=[[0, SX + org, SY + ys]]))
    ops.append(dict(t='mcset', h=tag, set={'FirstLine': l1, 'SecondLine': l2}))
    SEGS += z[6]
a_, b_ = PB
SEGS = [(a_, a_ + 50, 50, 1)] + SEGS + [(b_ - 50, b_, 50, 1)]
RY = [YB - 650, YB - 1100]; CW = 140; TG = 120; rows = [[] for _ in RY]; items = []
for s0, s1, st, n in SEGS:
    txt = ('%dх%d' % (st, n)) if n > 1 else ''
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
ops.append(dict(t='erase', h=[tdim, 'S5D']))
# horizontal bars of the basement storey (Bekassyl 05.11: «горизонтальная арматура қайда»): both faces + Ск at both ends, notes
d0, st0 = hj['HD'][0]; ck = hj['CKS'][str(d0)]; pS = hj['POS']['S_%d' % d0]
xl, xr = 42862, 50482; leg = 2 * (int(math.ceil(61 * d0 / 10.0) * 10))
ops += [dict(t='pl', p=[W(xl, 25470), W(xr, 25470)], layer='диам%d' % d0, lw=40), dict(t='pl', p=[W(xl, 25810), W(xr, 25810)], layer='диам%d' % d0, lw=40),
        dict(t='pl', p=[W(xl + leg, 25430), W(xl + 100, 25430), W(xl, 25530), W(xl, 25750), W(xl + 100, 25850), W(xl + leg, 25850)], layer='диам%d' % d0, lw=40),
        dict(t='pl', p=[W(xr - leg, 25430), W(xr - 100, 25430), W(xr, 25530), W(xr, 25750), W(xr - 100, 25850), W(xr - leg, 25850)], layer='диам%d' % d0, lw=40)]
for tag, src, org, tgt in (('S5CKL', '1BD110', (42600, 27100), (xl, 25640)), ('S5CKR', '1BD167', (50200, 27700), (xr, 25640))):
    ops += [dict(t='clone', h=src, base=[0, 0], to=[0, 0], tag=tag), dict(t='spmove', h=tag, items=[[0] + W(*org), [1] + W(*tgt)]),
            dict(t='mcset', h=tag, set={'FirstLine': 'Ск%d' % ck, 'SecondLine': '(%%%%C%d)' % d0})]
ops += [dict(t='clone', h='A4S9', base=[0, 0], to=[0, 0], tag='S5S'), dict(t='spmove', h='S5S', items=[[0] + W(47000, 28300), [1] + W(47250, 25810), [2] + W(47500, 25470)]),
        dict(t='mcset', h='S5S', set={'FirstLine': str(pS), 'SecondLine': 'ш.%d' % st0})]
ax2 = next(r for r in R if r['t'] == 'SPDSCONSTRUCTIONLINE' and 41000 < r['x0'] < 44000 and r['y1'] - r['y0'] > 5000)
ops.append(dict(t='move', h=[ax2['h']], d=[-125, 0]))                     # axis 2 at the wall face: -250 drawn (x2), -125 already done
ops.append(dict(t='save'))
print('dots tpl', tdot['h'], 'erase', len(er), 'zones', [(z[0], z[3], z[4], len(z[5])) for z in D], 'Ск', ck, d0)
if '--notes-only' in sys.argv:
    ops = [o for o in ops if (o.get('h', '') or '').startswith(('S4N_', 'TPA:')) or (o.get('tag', '') or '').startswith('S4N_')] + [dict(t='save')]
    out = gx.run(ops, 'sm4pln'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
elif '--run' in sys.argv:
    out = gx.run(ops, 'sm5pl'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
