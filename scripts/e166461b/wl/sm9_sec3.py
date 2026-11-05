# См-9 5.37 section 1-1: zone-note fans re-laid (edge zone shelf to the right of its zone, middle zone shelf after it), so no
# text sits between axis Б and the wall face (dimension extension lines).
import sys, json; sys.path.insert(0, 'wl'); from common import *; from notes import notes
X, Y = 2543100.0, 455939.0; BX = 41455.0
PX = lambda x: X + BX + 2 * (x - 14750)
V = json.load(open('wl/sm9_vert.json', encoding='utf-8')); D = V['D']; LAB = V['LABELS']
YT = 32308.0; YS = 31291.0
R = listwin(X, Y, 59400, 42000, None)
fans = [r for r in R if r['t'] == 'LWPOLYLINE' and r['lay'] == 'Размеры' and any(abs(p[1] - YS) < 2 for p in r['sp']) and r['x0'] > 38000]
N = [n for n in notes(X, Y, 59400, 42000) if abs(n['pts'][0][1] - YS) < 2 and n['pts'][0][0] > 38000]
ops = [dict(t='erase', h=[r['h'] for r in fans])]
for i in range(2):
    zL, zM = D[i][0]
    nL = next(n for n in N if n['l1'] == LAB['%d|0|L' % i] and abs(n['pts'][0][0] - (PX(zL[1]) - X)) < 4000 and (i == 0) == (n['pts'][0][0] < 50000))
    nM = next(n for n in N if n['l1'] == LAB['%d|0|M' % i] and (i == 0) == (n['pts'][0][0] < 50000))
    A = PX(zL[2]) + 300; B = A + 1800; E = PX(zM[2]) - 300
    ops += [dict(t='pl', p=[[PX(zL[1]), Y + YT], [A, Y + YS], [A + 1400, Y + YS]], layer='Размеры'),
            dict(t='pl', p=[[PX(zL[2]), Y + YT], [A, Y + YS]], layer='Размеры'),
            dict(t='spmove', h=nL['h'], items=[[0, A, Y + YS]]),
            dict(t='pl', p=[[PX(zM[1]), Y + YT], [B, Y + YS], [E, Y + YS], [PX(zM[2]), Y + YT]], layer='Размеры'),
            dict(t='spmove', h=nM['h'], items=[[0, B, Y + YS]])]
ops.append(dict(t='save'))
print(len(fans), [n['l1'] for n in N])
out = gx.run(ops, 's93'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-8:])
