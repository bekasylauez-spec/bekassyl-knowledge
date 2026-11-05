# См-8 plans «Разрез (Опалубка) М1:100» on a separate A3 landscape sheet (x 2268600, frame cloned from 5.25):
# analog 4.33 plans moved there and remapped like the elevation: 1-1 (basement) <- analog 1-1, 2-2 (floors) <- analog 3-3,
# 3-3 (top storey +19.700...+21.450, only the piece 15225...18025, cropped at axes Б-В) <- analog 2-2.
import sys, json; sys.path.insert(0, 'wl'); from common import *
OX, Y = 2209200.0, 455939.0; NX = 2268600.0
A_ = [(-3125, -125), (-125, -125), (2775, 2775), (6175, 6175), (7875, 7425), (8125, 7675), (10225, 15225), (12475, 17775),
      (12725, 18025), (15875, 20575), (17625, 22625), (17875, 22875)]
R = json.load(open('w/r8op.json'))
AA = 39105.0                                         # analog axis A on the op sheet (all plans)
# (analog plan wall-line y, target wall-line y on the A3 sheet, target x of our А/1, name)
PL = [(36850, 25300, 6600, '1'), (17605, 16500, 6600, '2'), (27656, 7400, 6600 - 13700, '3')]
AX = {39105: ('А/1', 0), 47105: ('А', 5000), 48855: ('Б', 14750), 56855: ('В', 22750)}
EXTRA_AX = (47980, 51705)
ops = []
for ya, yt, xt, nm in PL:
    G = [r for r in R if r['x0'] > 32000 and ya - 5200 < (r['y0'] + r['y1']) / 2 < ya + 4200 and r['t'] != 'SPDSFORMAT']
    dx, dy = (NX + xt) - (OX + AA), yt - ya
    hs = [r['h'] for r in G]
    ops.append(dict(t='move', h=hs, d=[dx, dy]))
    A0 = NX + xt                                     # analog A after the move = our А/1
    ops.append(dict(t='erase', h=[r['h'] for r in G if r['t'] != 'MTEXT' and r['x0'] >= AA - 3300 and r['x1'] <= AA - 1500]))   # extension piece
    ops.append(dict(t='erase', h=[r['h'] for r in G if r['t'] == 'SPDSCONSTRUCTIONLINE' and round(r['sp'][0][0]) in EXTRA_AX]))
    ops.append(dict(t='pmap', win=[A0 - 3400, Y + yt - 5300, A0 + 18800, Y + yt + 1300], pairs=[[A0 + a, A0 + b] for a, b in A_]))
    for r in G:
        if r['t'] == 'SPDSCONSTRUCTIONLINE' and round(r['sp'][0][0]) in AX:
            v, x = AX[round(r['sp'][0][0])]
            (sx, sy), (ex, ey) = r['sp'][0], r['sp'][1]
            ops.append(dict(t='axis', h=r['h'], s=[A0 + x, Y + sy + dy], e=[A0 + x, Y + ey + dy], val=v))
    print(nm, len(G))
ops.append(dict(t='save'))
if '--run' in sys.argv:
    out = gx.run(ops, 'p8'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'pmap' in l][-6:])
