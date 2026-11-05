# См-11 geometry from the cloned См-7 sheets: piece ends 3175 -> 2775, 17100 -> 15675 (axis 4, x = 20050); См-3 band 13725..13975 kept
import sys; sys.path.insert(0, 'wl'); from common import *
Y = 455939.0
P = [(-125, -125), (3175, 2775), (5750, 5750), (13725, 13725), (13975, 13975), (17100, 15675), (20375, 20375), (22875, 22875)]
# applied once (05.11); the axes А 5000 / Б 14750 moved with it -> correction (current -> wanted) with the axes as fixed points:
f1 = lambda x: -125 + (x + 125) * 2900 / 3300                  # first map inside piece 1 (compressed linearly)
if '--fix2' in sys.argv: P = [(-125, -125), (f1(0), 0), (f1(125), 125), (2775, 2775), (22875, 22875)]   # second correction: only the piece's right end moves
elif '--fix' in sys.argv: P = [(-125, -125), (2775, 2775), (2775 + (5000 - 3175) / (5750 - 3175) * 2975, 5000), (5750, 5750), (13975, 13975), (13975 + (14750 - 13975) / 3125 * 1700, 14750), (15675, 15675), (22875, 22875)]
SH = [(2906700, 11503, 1, 0, 42000), (2966100, 6615, 1, 0, 29700), (3008100, 15030, 1, 0, 59400), (3050100, 15030, 1, 0, 59400), (3092100, 8000, 2, 0, 42000)]
ops = []
for X, A, k, y0, y1 in SH:
    ops.append(dict(t='pmap', win=[X + 200, Y + y0 + 200, X + A + k * 23500, Y + y1 - 200], pairs=[[X + A + k * a, X + A + k * b] for a, b in P]))
ops.append(dict(t='save'))
out = gx.run(ops, 'm11'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'pmap' in l])
