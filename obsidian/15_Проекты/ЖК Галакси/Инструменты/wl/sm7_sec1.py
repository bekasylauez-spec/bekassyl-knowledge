# См-7 sheet 5.29 «Разрез 1-1; 2-2 (Армирование) М1:50» stage 1, from the analog 4.22 sections import (x 2149800):
# analog 2-2 (storey with the extension) dropped, analog 3-3 (floors) moved up as our 2-2, extension piece / axes А/2, Б/1 removed,
# x remapped x2 with the См-7 piece map (sm7_map), our А/1 at sheet x 8000.
import sys, json; sys.path.insert(0, 'wl'); from common import *
from sm7_map import A_
X, Y = 2149800.0, 455939.0; AA, A0 = 16346.0, 8000.0
R = json.load(open('w/r7r.json')); N = json.load(open('w/n7r.json'))
cy = lambda r: (r['y0'] + r['y1']) / 2
G2 = [r['h'] for r in R if 20500 < cy(r) < 32000 and r['t'] != 'SPDSFORMAT'] + [n['h'] for n in N if 21000 < n['pts'][0][1] < 31500]
G3 = [r['h'] for r in R if 8000 < cy(r) < 20000 and r['t'] != 'SPDSFORMAT'] + [n['h'] for n in N if 9000 < n['pts'][0][1] < 19500]
DY = 26696 - 14234
er = list(G2)
er += [r['h'] for r in R if 32000 < cy(r) < 41500 and r['t'] not in ('SPDSFORMAT', 'MTEXT', 'SPDSCONSTRUCTIONLINE') and r['x0'] >= AA - 6400 and r['x1'] <= AA - 3000]
er += [n['h'] for n in N if n['pts'][0][1] > 32000 and all(AA - 6600 < p[0] < AA - 3000 for p in n['pts'])]
er += [r['h'] for r in R if r['t'] == 'SPDSCONSTRUCTIONLINE' and round(r['sp'][0][0]) in (34096, 41546) and abs(r['sp'][0][0] - r['sp'][1][0]) < 1 and r['h'] not in G2]
ops = [dict(t='erase', h=sorted(set(er))), dict(t='move', h=[h for h in G3 if h not in er], d=[0, DY]),
       dict(t='pmap', win=[X + 2000, Y + 20000, X + 58500, Y + 41500], pairs=[[X + AA + 2 * a, X + A0 + 2 * b] for a, b in A_])]
AX = {16346: ('А/1', 0), 32346: ('А', 5000), 35846: ('Б', 14750), 51846: ('В', 22750)}
for r in R:
    if r['t'] != 'SPDSCONSTRUCTIONLINE' or r['h'] in er: continue
    dy = DY if r['h'] in G3 else 0
    (sx, sy), (ex, ey) = r['sp'][0], r['sp'][1]
    if abs(sx - ex) < 1 and round(sx) in AX:
        v, x = AX[round(sx)]; ops.append(dict(t='axis', h=r['h'], s=[X + A0 + 2 * x, Y + sy + dy], e=[X + A0 + 2 * x, Y + ey + dy], val=v))
    elif abs(sy - ey) < 1:
        ops.append(dict(t='axis', h=r['h'], s=[X + A0 + 45500, Y + sy + dy], e=[X + A0 - 1000, Y + sy + dy], val='1'))
ops.append(dict(t='save'))
print('erase', len(set(er)), 'move', len(G3))
out = gx.run(ops, 's71'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'pmap' in l][-4:])
