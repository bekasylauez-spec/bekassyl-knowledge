# См-2 horizontal sheet 5.8: elevation (1:100, axis 1 at 8845) + plan «Разрез 1-1» (x2, axis 2 at 41104): stretch, drop 2/1
import sys, json; sys.path.insert(0, 'wl'); from common import *
X0, Y0 = 1219700.0, 455939.0
EL = [(14245, 14220), (14295, 14270), (15520, 15520), (15770, 15770), (16820, 17020), (16870, 17070),
      (20545, 20670), (20595, 20720), (21970, 21970), (22220, 22220), (23445, 23470), (23495, 23520)]
XP = lambda xs: 41104 + 2 * (xs - 6800)
PL = [(5400, 5375), (5450, 5425), (6675, 6675), (6925, 6925), (7975, 8175), (8025, 8225),
      (11700, 11825), (11750, 11875), (13125, 13125), (13375, 13375), (14600, 14625), (14650, 14675)]
R = listwin(X0, Y0, 59400, 42000, None)
for r in R:
    if r['t'] == 'INSERT' and r['x1'] - r['x0'] > 15000: gx.run([{'t': 'explode', 'h': r['h']}], 'ex')
R = listwin(X0, Y0, 59400, 42000, None)
DEAD = [19245, XP(9650)]
er = [r['h'] for r in R if r['t'] == 'SPDSCONSTRUCTIONLINE' and r['x1'] - r['x0'] < 1500 and min(abs((r['x0'] + r['x1']) / 2 - d) for d in DEAD) < 60]
er += [r['h'] for r in R if r['t'] == 'DIMENSION' and any(min(abs(a - d) for d in DEAD) < 5 for a, b in r['sp'][:2])]
ops = [dict(t='erase', h=er),
       dict(t='pmap', win=[X0 + 1000, Y0 + 1000, X0 + 33000, Y0 + 41000], pairs=[[X0 + a, X0 + b] for a, b in [(12000, 12000)] + EL + [(26000, 26000)]]),
       dict(t='pmap', win=[X0 + 33500, Y0 + 24000, X0 + 58500, Y0 + 41000], pairs=[[X0 + XP(a), X0 + XP(b)] for a, b in [(4000, 4000)] + PL + [(16000, 16000)]]),
       dict(t='save')]
print('erase', er)
out = gx.run(ops, 'sm2hg'); print([l for l in out.splitlines() if 'pmap' in l or 'ERR' in l][-3:])
