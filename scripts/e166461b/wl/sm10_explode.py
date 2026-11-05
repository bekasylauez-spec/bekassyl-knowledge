# См-10: explode the large drawing blocks of the imported analog См-7 sheets (st2 idx 3, 13, 14, 4)
import sys; sys.path.insert(0, 'wl'); from common import *
SH = [(2632200, 59400, 42000), (2691600, 42000, 59400), (2733600, 42000, 59400), (2775600, 59400, 42000)]
for it in range(2):
    ops = []
    for X, W, H in SH:
        R = listwin(X, 455939, W, H, None)
        big = [r for r in R if r['t'] == 'INSERT' and (r['x1'] - r['x0'] > 3000 or r['y1'] - r['y0'] > 3000) and r['x0'] > -5 and r['x1'] < W + 5]
        ops += [dict(t='explode', h=r['h']) for r in big]
        print(it, X, len(R), 'big', len(big))
    if not ops: break
    ops.append(dict(t='save')); out = gx.run(ops, 'ex10'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
