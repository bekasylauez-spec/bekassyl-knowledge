# См-9 (x = 10400, [15225..18025] + [20375..22875], -4.650...+22.400) from the analog См-8 (st2 4.30 / 4.31): only the right end of
# piece 1 moves +300 (См-5 face 18025 instead of the analog's 2975 from Б); axis Б/1 removed. Slab hatches refitted.
import sys; sys.path.insert(0, 'wl'); from common import *
Y = 455939.0
P1 = [(475, 475), (2725, 3025), (2975, 3275), (5625, 5625)]
def ops_for(X, B, sc, win, axb1):
    return [dict(t='pmap', win=[X + win[0], Y + win[1], X + win[2], Y + win[3]], pairs=[[X + B + sc * a, X + B + sc * b] for a, b in P1])], axb1
OPS = []; ER = []
for X, B, sc, win, axb1 in ((2483700, 10440, 1, (3000, 6000, 20500, 40500), ['27942C']), (2483700, 34435, 1, (31000, 26000, 45000, 30500), ['276DB1']),
                           (2543100, 9348, 1, (2000, 3500, 19400, 38500), ['279514']), (2543100, 26795, 1, (19800, 3500, 36950, 38500), ['2795FC']),
                           (2543100, 41455, 2, (38000, 29500, 59000, 36500), ['278170'])):
    o, e = ops_for(X, B, sc, win, axb1); OPS += o; ER += e
OPS.insert(0, dict(t='erase', h=ER))
OPS.append(dict(t='save'))
out = gx.run(OPS, 's9e'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'pmap' in l])
# hatches
ops = []
for X in (2483700.0, 2543100.0):
    R = listwin(X, Y, 59400, 42000, None)
    PL = [r for r in R if r['t'] == 'LWPOLYLINE' and r['y1'] - r['y0'] < 800 and r['x1'] - r['x0'] > 1500]
    for h in [r for r in R if r['t'] == 'HATCH']:
        b = [p for p in PL if abs(p['y0'] - h['y0']) < 3 and abs(p['y1'] - h['y1']) < 3 and p['x0'] < (h['x0'] + h['x1']) / 2 + 3000 and p['x1'] > (h['x0'] + h['x1']) / 2 - 3000]
        if not b: print('no band', h['h']); continue
        b = min(b, key=lambda p: abs((p['x0'] + p['x1']) / 2 - (h['x0'] + h['x1']) / 2))
        ops.append(dict(t='hatchfit', h=h['h'], loops=[[[X + b['x0'], Y + b['y0']], [X + b['x1'], Y + b['y0']], [X + b['x1'], Y + b['y1']], [X + b['x0'], Y + b['y1']]]]))
ops.append(dict(t='save'))
out = gx.run(ops, 's9e2'); print('hatchfit', len(ops) - 1, [l for l in out.splitlines() if 'ERR' in l or 'done' in l])
