# См-10 sheet 5.43 «Разрез (Армирование) М1:50» stage 1: analog 4.29 plans (st2 idx4) remapped x2 (analog A at 14845 -> our А/1 at 9500,
# shifted left so that 22750 x2 fits): 1-1 basement <- analog 1-1 (MB), 2-2 floors <- analog 2-2 (MB), 3-3 top <- analog 3-3 (MF, only Б-В);
# extension piece, axes A/2, Б/1, analog dims except the axis chains away (reinforcement is rebuilt by wall_sec.py).
import sys, json; sys.path.insert(0, 'wl'); from common import *
from notes import notes
X, Y = 2817600.0, 455939.0; AA, A0 = 14845.0, 9500.0
COM = [(-3125, -125), (-125, -125), (2775, 2775), (6175, 6175), (7875, 7425), (8125, 7675)]
MB = COM + [(10225, 15225), (17625, 22625), (17875, 22875)]
MF = COM + [(11600, 15225), (17625, 22625), (17875, 22875)]
R = json.load(open('w/r43.json')); N = notes(X, Y, 59400, 42000)
PLANS = [(37544, MB, '1'), (25415, MB, '2'), (13301, MF, '3')]
AXV = {14845: ('А/1', 0), 30845: ('А', 5000), 34345: ('Б', 14750), 50345: ('В', 22750)}
ops = []; er = []
for wl, MP, nm in PLANS:
    band = lambda r: wl - 4300 < (r['y0'] + r['y1']) / 2 < wl + 2400
    er += [r['h'] for r in R if band(r) and r['t'] != 'MTEXT' and r['x0'] >= AA - 6900 and r['x1'] <= AA - 3000]          # extension piece + its dims
    er += [n['h'] for n in N if wl - 4300 < n['pts'][0][1] < wl + 2400 and all(AA - 7500 < p[0] < AA - 2900 for p in n['pts'])]
    for r in R:
        if not band(r) or r['t'] != 'SPDSCONSTRUCTIONLINE': continue
        (sx, sy), (ex, ey) = r['sp'][0], r['sp'][1]
        if abs(sx - ex) < 1:
            k = round(sx)
            if k in AXV and not (nm == '3' and AXV[k][1] < 14000):
                v, x = AXV[k]; ops.append(dict(t='axis', h=r['h'], s=[X + A0 + 2 * x, Y + sy], e=[X + A0 + 2 * x, Y + ey], val=v))
            else: er.append(r['h'])
        else:
            ops.append(dict(t='axis', h=r['h'], s=[X + A0 + 2 * 22750 + 300, Y + wl], e=[X + A0 + (2 * 14750 - 1300 if nm == '3' else -1300), Y + wl], val='3'))
    # analog dims: keep only the axis chain (ext at wl-1844 .. ) — everything else is rebuilt
    AD = [r for r in R if band(r) and r['t'] == 'DIMENSION' and len(r['sp']) > 2 and abs(r['sp'][0][1] - r['sp'][1][1]) < 1 and r['sp'][2][1] < wl - 2600]
    er += [r['h'] for r in R if band(r) and r['t'] == 'DIMENSION' and r not in AD]
    tot = max(AD, key=lambda r: abs(r['sp'][1][0] - r['sp'][0][0])); ch = [r for r in AD if r is not tot]
    yx = max(r['sp'][0][1] for r in AD); ych = ch[0]['sp'][2][1]; ytot = tot['sp'][2][1]
    segs = [(14750, 22750)] if nm == '3' else [(0, 5000), (5000, 14750), (14750, 22750)]
    for r, (a, b) in zip(ch, segs):
        ops.append(dict(t='dimpts', h=r['h'], p1=[X + A0 + 2 * a, Y + yx], p2=[X + A0 + 2 * b, Y + yx], dl=[X + A0 + a + b, Y + ych])); ops.append(dict(t='dimdef', h=[r['h']]))
    er += [r['h'] for r in ch[len(segs):]]
    if nm == '3': er.append(tot['h'])
    else: ops += [dict(t='dimpts', h=tot['h'], p1=[X + A0, Y + yx], p2=[X + A0 + 2 * 22750, Y + yx], dl=[X + A0 + 22750, Y + ytot]), dict(t='dimdef', h=[tot['h']])]
    ops.append(dict(t='pmap', win=[X + 1000, Y + wl - 2500, X + 58500, Y + wl + 2400], pairs=[[X + AA + 2 * a, X + A0 + 2 * b] for a, b in MP]))
    if nm == '3':                                                       # top storey: only the piece 15225..22875
        er += [r['h'] for r in R if band(r) and r['t'] not in ('MTEXT', 'SPDSCONSTRUCTIONLINE', 'DIMENSION') and r['x1'] < AA + 2 * 9000]
        er += [n['h'] for n in N if wl - 4300 < n['pts'][0][1] < wl + 2400 and n['pts'][0][0] < AA + 2 * 9000]
ops.insert(0, dict(t='erase', h=sorted(set(er))))
ops.append(dict(t='save'))
print('erase', len(set(er)), 'ops', len(ops))
if '--run' in sys.argv:
    out = gx.run(ops, 's101'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'pmap' in l][-6:])
