# two-target shelf notes: inner target (nearest to the text) ON the shelf -> the shelf ends at it (tick at the end);
# far target slightly below the shelf (shallow leader, angle <= ~20 deg) -> its leader crosses the inner bar without a tick
# and ends at the far bar with a tick that is clearly not parallel to the bar.
import sys, math; sys.path.insert(0, 'wl'); from common import *
from notes import notes
def run(SX, H, go=False, ylo=0):
    SY = 455939.0
    R = listwin(SX, SY, 59400, H, None)
    V = [r['sp'] for r in R if r['t'] in ('LINE', 'LWPOLYLINE') and r['lay'].lower().startswith('диам')]
    def covers(x, y):
        return any(abs(x1 - x2) < 1 and abs(x - x1) < 15 and min(y1, y2) + 30 <= y <= max(y1, y2) - 30 for sp in V for (x1, y1), (x2, y2) in zip(sp, sp[1:]))
    ops = []
    for n in notes(SX, SY, 59400, H):
        if len(n['pts']) != 3 or n['pts'][0][1] < ylo: continue
        o = n['pts'][0]; t = n['pts'][1:]
        if abs(t[0][0] - t[1][0]) < 20: continue                     # vertical pair (other style): leave
        ys = o[1]
        ji = min((1, 2), key=lambda j: abs(n['pts'][j][0] - o[0])); jf = 3 - ji
        xi, xf = n['pts'][ji][0], n['pts'][jf][0]
        dy = max(80, min(300, 0.36 * (abs(xf - xi) + 100)))
        yf = ys - dy if covers(xf, ys - dy) else ys + dy
        if not covers(xi, ys): print('inner not on a bar', n['h'], n['l1'], (round(xi), round(ys)))
        ops.append(dict(t='spmove', h=n['h'], items=[[ji, SX + xi, SY + ys], [jf, SX + xf, SY + yf]]))
    ops.append(dict(t='save'))
    print('notes', len(ops) - 1)
    if go: out = gx.run(ops, 'tfx2'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-3:])
if __name__ == '__main__':
    run(float(sys.argv[1]), float(sys.argv[2]), '--run' in sys.argv, float(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] != '--run' else 14000)
