# fix «tick at a crossing»: the inner leader target of a shelf-note is moved along its own bar off the shelf (±300),
# so that its leader ENDS at the bar (tick) and the shelf only crosses the bar (no tick)
import sys, math; sys.path.insert(0, 'wl'); from common import *
from notes import notes
import tickgeom
def run(SX, H, geom, go=False, dy=300):
    SY = 455939.0
    bad = [b for b in tickgeom.run(SX, H, geom, show=False) if b[2].startswith('tick at a crossing')]
    R = listwin(SX, SY, 59400, H, None)
    V = [(r['sp'], r['lay']) for r in R if r['t'] in ('LINE', 'LWPOLYLINE') and r['lay'].lower().startswith('диам')]
    def covers(x, y):
        for sp, lay in V:
            for (x1, y1), (x2, y2) in zip(sp, sp[1:]):
                if abs(x1 - x2) < 1 and abs(x - x1) < 15 and min(y1, y2) + 50 <= y <= max(y1, y2) - 50: return True
        return False
    N = {n['h']: n for n in notes(SX, SY, 59400, H)}
    ops = []
    for h, l1, kind, c in bad:
        n = N[h]
        j = min(range(1, len(n['pts'])), key=lambda k: math.hypot(n['pts'][k][0] - c[0], n['pts'][k][1] - c[1]))
        x, y = n['pts'][j]
        ny = y - dy if covers(x, y - dy) else y + dy if covers(x, y + dy) else None
        if ny is None: print('no room', h, l1, (round(x), round(y))); continue
        ops.append(dict(t='spmove', h=h, items=[[j, SX + x, SY + ny]]))
    ops.append(dict(t='save'))
    print('fix', len(ops) - 1, 'of', len(bad))
    if go: out = gx.run(ops, 'tfix'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-3:])
if __name__ == '__main__':
    run(float(sys.argv[1]), float(sys.argv[2]), sys.argv[3], '--run' in sys.argv)
