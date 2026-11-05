# 5.26 cleanup: "0" dim, basement opening lines, foundation rectangle, slab hatches refit, axis dims 5000|9750|8000 + 22750
import sys, json; sys.path.insert(0, 'wl'); from common import *
X, Y = 2036100.0, 455939.0; A = 15030.0
R = json.load(open('w/r26.json'))
W = lambda x, y: [X + x, Y + y]
lines = [r['h'] for r in R if r['t'] == 'LINE' and r['lay'] == 'Размеры' and abs(r['y0'] - 27970) < 2 and r['y1'] < 31000 and abs(r['x0'] - r['x1']) < 1]
ops = [dict(t='erase', h=['1F6C85'] + lines)]
ops.append(dict(t='spmove', h='1FAB6E', items=[[0] + W(A + 23075, 27270), [1] + W(A + 23075, 27970), [2] + W(A - 325, 27970), [3] + W(A - 325, 27270)]))
ops.append(dict(t='spmove', h='1FAB70', items=[[0] + W(A + 23175, 27170), [1] + W(A + 23175, 27270), [2] + W(A - 425, 27270), [3] + W(A - 425, 27170)]))
pairs = {'1FAB6D': (A - 325, 27270, A + 23075, 27970), '1FAB6F': (A - 425, 27170, A + 23175, 27270)}
B = {r['h']: r for r in R}
for hh, bb in (('1FAB77', '1FAB78'), ('1FAB79', '1FAB7A'), ('1FAB7B', '1FAB7C'), ('1FAB7D', '1FAB7E'), ('1FAB7F', '1FAB80'), ('1FAB81', '1FAB82'), ('1FAB83', '1FAB84')):
    r = B[bb]; pairs[hh] = (r['x0'], r['y0'], r['x1'], r['y1'])
for hh, (x0, y0, x1, y1) in pairs.items():
    ops.append(dict(t='hatchfit', h=hh, loops=[[W(x0, y0), W(x1, y0), W(x1, y1), W(x0, y1)]]))
# axis dims: total (existing 17750 dim reused) + chain above it
ops.append(dict(t='spmove', h='1FAB64', items=[[1] + W(A + 22750, 25410)]))
for a, b in ((0, 5000), (5000, 14750), (14750, 22750)):
    ops.append(dict(t='dim', h='1FAB64', p1=W(A + a, 25410), p2=W(A + b, 25410), dl=W(A + (a + b) / 2, 23510), rot=0, txt=''))
ops.append(dict(t='save'))
out = gx.run(ops, 'f26'); print(len(lines), [l for l in out.splitlines() if 'ERR' in l or 'hatchfit' in l or 'done' in l or 'spmove' in l][-14:])
