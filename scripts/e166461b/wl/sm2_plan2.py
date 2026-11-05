# См-2 sheet 5.8, plan «Разрез 1-1» (x2, axis 2 at 41054): dots, chain and dot notes in Bekassyl's style
# (thin polyline dots -> shelf, text outward; a note that would cross an axis / another note goes to the lower level or the other side).
import sys, os, json, math; sys.path.insert(0, 'wl'); from common import *
from notes import notes
SX, SY = 1219700.0, 455939.0
def W(x, y): return [SX + x, SY + y]
PIECES = [(5375, 6675), (6925, 8225), (11825, 13125), (13375, 14675)]
XP = lambda xs: 41054 + 2 * (xs - 6800)
YW, YD = 35200, 35306                                               # chain base, lower dot centre
LEV = [33806, 32693]                                                # note levels A, B
AX = [41054, 53954]
vj = json.load(open('wl/sm2_vert.json', encoding='utf-8')); hj = json.load(open('wl/sm2_hor.json', encoding='utf-8'))
D = vj['D']; LAB = vj['LABELS']
R = listwin(SX, SY, 59400, 42000, None)
N = notes(SX, SY, 59400, 42000)
PL = lambda r: r['x0'] > 33500 and r['y0'] > 24000
dots = [r for r in R if PL(r) and r['t'] == 'INSERT' and r['lay'].lower().startswith('диам') and r['x1'] - r['x0'] < 300]
tdot = dots[0]; tx0 = (tdot['x0'] + tdot['x1']) / 2
er = [r['h'] for r in dots]
chain = [r for r in R if PL(r) and r['t'] == 'DIMENSION' and abs(r['sp'][0][1] - YW) < 2 and abs(r['sp'][1][1] - YW) < 2]
tdim = chain[0]['h']; er += [r['h'] for r in chain[1:]]
barnotes = [n for n in N if n['pts'][0][0] > 33500 and n['pts'][0][1] > 24000 and n['l2'].startswith('ш.') and not n['l1'].startswith(('Х', 'Шп')) and len(n['pts']) == 1]
er += [n['h'] for n in barnotes]
er += [r['h'] for r in R if PL(r) and r['t'] == 'LWPOLYLINE' and r['lay'] == 'Размеры' and len(r['sp']) == 4 and abs(r['sp'][0][1] - YD) < 3 and abs(r['sp'][3][1] - YD) < 3]
er += [r['h'] for r in R if PL(r) and r['t'] == 'LWPOLYLINE' and r['lay'] == 'Размеры' and len(r['sp']) == 2 and abs(r['sp'][0][1] - r['sp'][1][1]) < 1 and min(abs(r['sp'][0][1] - v) for v in LEV) < 2]
ops = [dict(t='clone', h=tdot['h'], base=[0, 0], to=[0, -300000], tag='S2D'), dict(t='erase', h=er)]
placed = {0: [], 1: []}; legsB = []; SEGS = []; k = 0
for i, (a, b) in enumerate(PIECES):
    zs = D[i][0]; pc = (XP(a) + XP(b)) / 2
    for j, z in sorted(enumerate(zs), key=lambda q: q[1][0] == 'M'):   # edge zones first, the middle one fits around them
        kind, x0, x1, d, st = z[:5]
        for xb in z[5]: ops.append(dict(t='clone', h='S2D', base=[0, 0], to=[XP(xb) - tx0, 300000], layer='диам%d' % d))
        lab = LAB['%d|0|%s' % (i, kind)]; l1 = '%s(%%%%C%d)' % (lab, d); l2 = 'ш.%d' % st
        xa, xb = XP(z[5][0]), XP(z[5][-1]); cx = (xa + xb) / 2
        w = 200 * max(len(l1.replace('%%%%C', 'Ф')), len(l2))
        lf, rf = xa + 100, max(xb - 100, xa + 200)
        out = cx <= pc
        best = None
        for lev, left in ((0, out), (1, out), (0, not out), (1, not out)):
            t0, t1 = (lf - w, lf) if left else (rf, rf + w)
            if any(t0 - 80 < ax_ < t1 + 80 for ax_ in AX): continue
            if any(not (t1 + 150 < p0 or t0 - 150 > p1) for p0, p1 in placed[lev]): continue
            if lev == 0 and any(t0 - 60 < xl < t1 + 60 for xl in legsB): continue
            best = (lev, left, t0, t1); break
        if best is None: best = (1, out, (lf - w, lf) if out else (rf, rf + w))[:2] + ((lf - w, lf) if out else (rf, rf + w))
        lev, left, t0, t1 = best; ys = LEV[lev]
        placed[lev].append((t0, t1))
        if lev == 1: legsB += [xa, lf, rf, xb]
        if lev == 0: legsA = [(t0, t1)]
        shelf = [t0, rf] if left else [lf, t1]; org = t1 if left else t1
        org = lf if left else rf + w
        ops.append(dict(t='pl', p=[W(xa, YD), W(lf, ys), W(rf, ys), W(xb, YD)], layer='Размеры'))
        ops.append(dict(t='pl', p=[W(shelf[0], ys), W(shelf[1], ys)], layer='Размеры'))
        tag = 'S2N2_%d' % k; k += 1
        ops.append(dict(t='clone', h='TPA:5D2951', base=[0, 0], to=[0, 0], tag=tag))
        ops.append(dict(t='spmove', h=tag, items=[[0, SX + org, SY + ys]]))
        ops.append(dict(t='mcset', h=tag, set={'FirstLine': l1, 'SecondLine': l2}))
    for s0, s1, st, n in [(a, a + 50, 50, 1)] + [sg for z in zs for sg in z[6]] + [(b - 50, b, 50, 1)]: SEGS.append((i, s0, s1, st, n))
RY = [31800, 31350]; CW = 140; TG = 120; rows = [[] for _ in RY]; items = []
for i, s0, s1, st, n in SEGS:
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
ops.append(dict(t='erase', h=[tdim, 'S2D']))
# basement: Ск notes / straight-bar notes / plan bars -> Ø of the basement horizontal bars; vertical-pair note: far target off the line
d0 = hj['HD'][0][0]; ck = hj['CKS'][str(d0)]; pS = hj['POS']['S_%d' % d0]
for n in N:
    if n['pts'][0][0] < 33500 or n['pts'][0][1] < 24000: continue
    if n['l1'].startswith('Ск'): ops.append(dict(t='mcset', h=n['h'], set={'FirstLine': 'Ск%d' % ck, 'SecondLine': '(%%%%C%d)' % d0}))
    elif n['l1'].strip().isdigit() and len(n['pts']) == 3 and abs(n['pts'][1][0] - n['pts'][2][0]) < 5:
        o = n['pts'][0]; jf = max((1, 2), key=lambda j: abs(n['pts'][j][1] - o[1]))
        ops.append(dict(t='mcset', h=n['h'], set={'FirstLine': str(pS), 'SecondLine': 'ш.%d' % hj['HD'][0][1]}))
        ops.append(dict(t='spmove', h=n['h'], items=[[jf, SX + n['pts'][jf][0] + 250, SY + n['pts'][jf][1]]]))
ub = [r for r in R if PL(r) and r['t'] in ('LINE', 'LWPOLYLINE') and r['lay'].lower() in ('диам10', 'диам12')]
for r in ub: ops.append(dict(t='clone', h=r['h'], base=[0, 0], to=[0, 0], layer='диам%d' % d0))
if ub: ops.append(dict(t='erase', h=[r['h'] for r in ub]))
ops.append(dict(t='save'))
print('dots', len(dots), 'chain', len(chain), 'notes', len(barnotes), 'Ск', ck, 'd0', d0, 'placed', placed)
if '--run' in sys.argv:
    out = gx.run(ops, 'sm2pl2'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
