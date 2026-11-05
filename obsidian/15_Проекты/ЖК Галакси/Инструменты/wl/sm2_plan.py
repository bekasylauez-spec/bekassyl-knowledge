# См-2 sheet 5.8, plan «Разрез 1-1» (x2, axis 2 at 41054): vertical bar dots / chain / notes for our basement zones (analog objects reused)
import sys, os, json; sys.path.insert(0, 'wl'); from common import *
from notes import notes
SX, SY = 1219700.0, 455939.0
def W(x, y): return [SX + x, SY + y]
XP = lambda xs: 41054 + 2 * (xs - 6800)
PIECES = [(5375, 6675), (6925, 8225), (11825, 13125), (13375, 14675)]
vj = json.load(open('wl/sm2_vert.json', encoding='utf-8')); hj = json.load(open('wl/sm2_hor.json', encoding='utf-8'))
D = vj['D']; LAB = vj['LABELS']
R = listwin(SX, SY, 59400, 42000, None); N = notes(SX, SY, 59400, 42000)
PLN = lambda r: r['x0'] > 33500 and r['y0'] > 24000
dots = [r for r in R if PLN(r) and r['t'] == 'INSERT' and r['lay'].lower().startswith('диам') and r['x1'] - r['x0'] < 300]
tdot = dots[0]; tx0 = (tdot['x0'] + tdot['x1']) / 2
chain = [r for r in R if PLN(r) and r['t'] == 'DIMENSION' and abs(r['sp'][0][1] - 35200) < 3]
dead = [r['h'] for r in R if PLN(r) and r['t'] == 'DIMENSION' and any(abs(a - 47089) < 5 for a, b in r['sp'][:2])]
dead += [r['h'] for r in R if PLN(r) and r['t'] == 'SPDSCONSTRUCTIONLINE' and abs((r['x0'] + r['x1']) / 2 - 47089) < 80]
barn = [n for n in N if n['pts'][0][0] > 33500 and len(n['pts']) == 1 and n['l2'].startswith('ш.')]
tdim = chain[0]['h']
ops = [dict(t='clone', h=tdot['h'], base=[0, 0], to=[0, -300000], tag='S2D'), dict(t='clone', h=barn[0]['h'], base=[0, 0], to=[0, -300000], tag='S2N'),
       dict(t='erase', h=[r['h'] for r in dots] + [r['h'] for r in chain[1:]] + [n['h'] for n in barn] + dead)]
k = 0
for i, (a, b) in enumerate(PIECES):
    zs = D[i][0]
    for j, z in enumerate(zs):
        kind, x0, x1, d, st, bars = z[:6]
        for xb in bars: ops.append(dict(t='clone', h='S2D', base=[0, 0], to=[XP(xb) - tx0, 300000], layer='диам%d' % d))
        lab = LAB['%d|0|%s' % (i, kind)]
        cx = (XP(x0) + XP(x1)) / 2; tag = 'S2n%d' % k; k += 1        # analog: a shelf note under the zone, no leader
        ops.append(dict(t='clone', h='S2N', base=[0, 0], to=[0, 0], tag=tag))
        ops.append(dict(t='spmove', h=tag, items=[[0, SX + cx - 300, SY + 33806 - 700 * (j % 2)]]))
        ops.append(dict(t='mcset', h=tag, set={'FirstLine': '%s(%%%%C%d)' % (lab, d), 'SecondLine': 'ш.%d' % st}))
    segs = [(a, a + 50, 50, 1)] + [sg for z in zs for sg in z[6]] + [(b - 50, b, 50, 1)]
    for k_, (s0, s1, st, n) in enumerate(segs):
        txt = ('%dх%d' % (st, n)) if n > 1 else ''
        ty = 32273 - 450 * (k_ % 2)
        kw = dict(t='dim', h=tdim, p1=W(XP(s0), 35200), p2=W(XP(s1), 35200), dl=W((XP(s0) + XP(s1)) / 2, ty), rot=0, txt=txt)
        tw = 110 * max(len(txt), len(str(int(s1 - s0)))) / 2 + 150
        if XP(s1) - XP(s0) < 2 * tw:
            kw['tx'] = W(XP(s1) + tw if (s0 + s1) / 2 > (a + b) / 2 else XP(s0) - tw, ty + 60)
        ops.append(kw)
ops.append(dict(t='erase', h=[tdim, 'S2D', 'S2N']))
# straight bars / caps notes of the basement storey
d0 = hj['HD'][0][0]; sp0 = 'ш.%d' % hj['HD'][0][1]
pS = hj['POS']['S_%d' % d0]; ck = hj['CKS'][str(d0)] if str(d0) in hj['CKS'] else hj['CKS'][d0]
for n in N:
    if n['pts'][0][0] < 33500: continue
    if n['l1'].startswith('Ск'): ops.append(dict(t='mcset', h=n['h'], set={'FirstLine': 'Ск%d' % ck, 'SecondLine': '(%%%%C%d)' % d0}))
    elif n['l1'].strip().isdigit() and n['l2'].startswith('ш.') and len(n['pts']) == 3: ops.append(dict(t='mcset', h=n['h'], set={'FirstLine': str(pS), 'SecondLine': sp0}))
ops.append(dict(t='save'))
print('dots', len(dots), 'chain', len(chain), 'notes', len(barn), 'dead', dead)
if '--run' in sys.argv:
    out = gx.run(ops, 'sm2pl'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
