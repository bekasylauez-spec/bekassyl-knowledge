# См-10 plans «Разрез (Опалубка) М1:100» on a separate A3 landscape sheet 5.40 (x 2691600, frame + stamp cloned from 5.31):
# analog 4.26 plans moved there and remapped like the elevation: 1-1 (basement) <- analog 1-1, 2-2 (floors) <- analog 3-3,
# 3-3 (top storey +19.700...+22.400, only the piece 15225...22875) <- analog 2-2 (cropped later).
import sys, json; sys.path.insert(0, 'wl'); from common import *
OX, Y = 2632200.0, 455939.0; NX = 2691600.0
COM = [(-3125, -125), (-125, -125), (2775, 2775), (6175, 6175), (7875, 7425), (8125, 7675)]
MB = COM + [(10225, 15225), (17625, 22625), (17875, 22875)]
MF = COM + [(11600, 15225), (17625, 22625), (17875, 22875)]
R = json.load(open('w/r10o2.json'))
AA = 40182.0
PL = [(36399, 25300, 6600, MB), (17154, 16500, 6600, MF), (27205, 7400, 6600 - 13700, MB)]
AX = {40182: ('А/1', 0), 48182: ('А', 5000), 49932: ('Б', 14750), 57932: ('В', 22750)}
EXTRA_AX = (49057, 52782)
ops = [dict(t='clone', h=h, base=[OX - 59400 + 0, 0], to=[OX - 59400 + 423000, 0]) for h in ('234803', '234804', '234807')]
ops = [dict(t='clone', h=h, base=[0, 0], to=[NX - 2268600, 0], tag='P10F_' + h) for h in ('234803', '234804', '234807')]
if len(sys.argv) > 2: PL = [PL[int(sys.argv[2])]]; ops = []
for ya, yt, xt, MP in PL:
    G = [r for r in R if r['x0'] > 32000 and ya - 5200 < (r['y0'] + r['y1']) / 2 < ya + 4200 and r['t'] != 'SPDSFORMAT']
    dx, dy = (NX + xt) - (OX + AA), yt - ya
    ops.append(dict(t='move', h=[r['h'] for r in G], d=[dx, dy]))
    A0 = NX + xt
    ops.append(dict(t='erase', h=[r['h'] for r in G if r['t'] != 'MTEXT' and r['x0'] >= AA - 3300 and r['x1'] <= AA - 1500]))
    ops.append(dict(t='erase', h=[r['h'] for r in G if r['t'] == 'SPDSCONSTRUCTIONLINE' and round(r['sp'][0][0]) in EXTRA_AX]))
    ops.append(dict(t='pmap', win=[A0 - 3400, Y + yt - 5300, A0 + 18800, Y + yt + 1300], pairs=[[A0 + a, A0 + b] for a, b in MP]))
    for r in G:
        if r['t'] == 'SPDSCONSTRUCTIONLINE' and round(r['sp'][0][0]) in AX:
            v, x = AX[round(r['sp'][0][0])]
            (sx, sy), (ex, ey) = r['sp'][0], r['sp'][1]
            ops.append(dict(t='axis', h=r['h'], s=[A0 + x, Y + sy + dy], e=[A0 + x, Y + ey + dy], val=v))
    print(ya, len(G))
ops.append(dict(t='save'))
if sys.argv[1:2] == ['--run']:
    out = gx.run(ops, 'p10'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'pmap' in l][-6:])
