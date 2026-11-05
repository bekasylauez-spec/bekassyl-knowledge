# См-8 sheet 5.33 «Разрезы (Армирование) М1:50» stage 1: analog 4.35 plans remapped (x2), extension piece / axes А/2, Б/1 removed,
# our А/1 at sheet x 8000, axes А 5000, Б 14750, В 22750.
import sys, json; sys.path.insert(0, 'wl'); from common import *
X, Y = 2394600.0, 455939.0
A_ = [(-3125, -125), (-125, -125), (2775, 2775), (6175, 6175), (7875, 7425), (8125, 7675), (10225, 15225), (12475, 17775),
      (12725, 18025), (15875, 20575), (17625, 22625), (17875, 22875)]
AA, A0 = 16484.0, 8000.0
R = json.load(open('w/r8r.json')); N = json.load(open('w/n8r.json'))
er = [r['h'] for r in R if r['t'] not in ('SPDSFORMAT', 'MTEXT', 'SPDSCONSTRUCTIONLINE') and r['x0'] >= AA - 6400 and r['x1'] <= AA - 3000 and 8000 < r['y0']]
er += [n['h'] for n in N if all(AA - 6600 < p[0] < AA - 3000 for p in n['pts'])]
er += [r['h'] for r in R if r['t'] == 'SPDSCONSTRUCTIONLINE' and round(r['sp'][0][0]) in (34234, 41684) and abs(r['sp'][0][0] - r['sp'][1][0]) < 1]
ops = [dict(t='erase', h=er), dict(t='pmap', win=[X + 2000, Y + 9000, X + 58500, Y + 40500], pairs=[[X + AA + 2 * a, X + A0 + 2 * b] for a, b in A_])]
AX = {16484: ('А/1', 0), 32484: ('А', 5000), 35984: ('Б', 14750), 51984: ('В', 22750)}
for r in R:
    if r['t'] != 'SPDSCONSTRUCTIONLINE': continue
    (sx, sy), (ex, ey) = r['sp'][0], r['sp'][1]
    if abs(sx - ex) < 1 and round(sx) in AX:
        v, x = AX[round(sx)]; ops.append(dict(t='axis', h=r['h'], s=[X + A0 + 2 * x, Y + sy], e=[X + A0 + 2 * x, Y + ey], val=v))
    elif abs(sy - ey) < 1:
        ops.append(dict(t='axis', h=r['h'], s=[X + A0 + 45500, Y + sy], e=[X + A0 - 1000, Y + sy], val='2'))
ops.append(dict(t='save'))
print('erase', len(er))
out = gx.run(ops, 's81'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'pmap' in l][-4:])
