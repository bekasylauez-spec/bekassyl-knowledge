# См-1 sheet 5.4, plan «Разрез 1-1 (Армирования)» (drawn x2, axis 1 at 7075): vertical bar dots and their notes / chain
# redrawn for our zones (basement group G0); the analog's U-bars, hoops X1-X3 and their notes are kept (pmapped), texts updated.
import sys, os, json, math; sys.path.insert(0, 'wl'); from common import *
from notes import notes
SX, SY = 1008200.0, 455939.0
def W(x, y): return [SX + x, SY + y]
XP = lambda xs: 7075 + 2 * xs
PIECES = [(125, 1225), (5875, 7725), (12325, 14175), (18825, 19925)]                       # scheme x (axis 1 = 0) -> plan x
vj = json.load(open('wl/sm1_vert.json', encoding='utf-8')); hj = json.load(open('wl/sm1_hor.json', encoding='utf-8'))
D = vj['D']; LAB = vj['LABELS']
R = json.load(open('wl/f54b.json', encoding='utf-8')) if '--cached' in sys.argv else listwin(SX, SY, 59400, 84100, None)
N = notes(SX, SY, 59400, 84100)
PL = lambda r: 8000 < r['y0'] and r['y1'] < 22500
dots = [r for r in R if PL(r) and r['t'] == 'INSERT' and r['lay'].lower().startswith('диам') and r['x1'] - r['x0'] < 300]
tdot = dots[0]; tx0 = (tdot['x0'] + tdot['x1']) / 2
er = [r['h'] for r in dots]
AXD = {'14235B', '14235C', '14235D', '14235E', '14236A', '14236B', '14236C'}
chain = [r for r in R if PL(r) and r['t'] == 'DIMENSION' and r['h'] not in AXD and abs(r['sp'][0][1] - 16807) < 2]
tdim = chain[0]['h']
er += [r['h'] for r in chain[1:]]
barnotes = [n for n in N if PL({'y0': n['pts'][0][1], 'y1': n['pts'][0][1]}) and n['l2'].startswith('ш.') and not n['l1'].startswith('Х')]
er += [n['h'] for n in barnotes]
ops = [dict(t='clone', h=tdot['h'], base=[0, 0], to=[0, -300000], tag='S1D'), dict(t='erase', h=er)]
NOTE = dict(scale=100, ts=2.5, style='ГОСТ 2.304', arrow='oblique', layer='Размеры')
AX = [XP(0), XP(6800), XP(13250), XP(20050)]
for i in range(4):
    zs = D[i][0]
    for j, z in enumerate(zs):
        kind, x0, x1, d, st = z[:5]
        for xb in z[5]:
            xp = XP(xb)
            ops.append(dict(t='clone', h='S1D', base=[0, 0], to=[xp - tx0, 300000], layer='диам%d' % d))
        # note below the wall, leaders to the extreme dots (analog: «1(ф16) ш.100» under the piece)
        lab = LAB['%d|0|%s' % (i, kind)]
        ym = 13750 if kind == 'M' else 12950             # below the chain (the gap wall-chain is full of extension lines)
        ox = {'L': XP(x0) - 1000, 'R': XP(x1) + 1000, 'M': (XP(x0) + XP(x1)) / 2}[kind]
        for a in AX:
            if abs(ox - a) < 1300: ox = a + 1300 if ox >= a else a - 1300
        ops.append(dict(t='note', l1='%s(%%%%C%d)' % (lab, d), l2='ш.%d' % st, origin=W(ox, ym), targets=[W(XP(x0), 16887), W(XP(x1), 16887)], **NOTE))
    # chain of bar positions (one dim per zone, text «step x n»), the analog's dim as template (x2 drawing, real values)
    a_, b_ = PIECES[i]
    segs = [(a_, a_ + 50, 50, 1)] + [sg for z in zs for sg in z[6]] + [(b_ - 50, b_, 50, 1)]
    for k_, (s0, s1, st, n) in enumerate(segs):
        txt = ('%dх%d' % (st, n)) if n > 1 else ''
        ty = 14475 - 450 * (k_ % 2)
        kw = dict(t='dim', h=tdim, p1=W(XP(s0), 16807), p2=W(XP(s1), 16807), dl=W((XP(s0) + XP(s1)) / 2, ty), rot=0, txt=txt)
        tw = 110 * max(len(txt), len(str(int(s1 - s0)))) / 2 + 150
        if XP(s1) - XP(s0) < 2 * tw:
            cx = XP(s1) + tw if (s0 + s1) / 2 > (a_ + b_) / 2 else XP(s0) - tw
            for ax_ in AX:
                if abs(cx - ax_) < tw: cx = ax_ + (tw + 50) * (1 if cx >= ax_ else -1)
            kw['tx'] = W(cx, ty + 60)
        ops.append(kw)
ops.append(dict(t='erase', h=[tdim, 'S1D']))
# U-bar notes (analog 23 / 24 / 25): basement storey Ø and position
HD0 = json.load(open('wl/sm1_hor.json', encoding='utf-8'))['BARS'][0]['d']
pe = hj['POS']['end_%d' % HD0]; pm = hj['POS']['mid_%d' % HD0]
for n in N:
    if n['l2'].startswith('(') and PL({'y0': n['pts'][0][1], 'y1': n['pts'][0][1]}):
        x = n['pts'][0][0]
        ops.append(dict(t='mcset', h=n['h'], set={'FirstLine': str(pe if (x < 12000 or x > 42000) else pm), 'SecondLine': '(%%%%C%d)' % HD0}))
ops.append(dict(t='save'))
print('dots erased', len(dots), 'chain erased', len(chain) - 1, 'notes erased', len(barnotes), 'ops', len(ops))
if '--run' in sys.argv:
    out = gx.run(ops, 'sm154r'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
