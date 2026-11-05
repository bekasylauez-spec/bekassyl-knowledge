# geometric tick check of SPDS notes (rule Bekassyl 05.11): a tick only where the leader ENDS on a bar; a leader end on a bar must have a tick;
# where the leader only crosses a bar of another position - no tick. Bars = lines on layers «диам*».
import sys, math, collections, re; sys.path.insert(0, 'wl'); from common import *
from notes import notes
def run(SX, H, geom, show=True):
    SY = 455939.0
    R = listwin(SX, SY, 59400, H, None)
    B = []
    for r in R:
        if r['t'] in ('LINE', 'LWPOLYLINE') and r['lay'].lower().startswith('диам'):
            for (x1, y1), (x2, y2) in zip(r['sp'], r['sp'][1:]): B.append((x1, y1, x2, y2, int(re.sub(r'\D', '', r['lay']) or 0)))
    def bar_at(x, y, tol=20):
        out = []
        for x1, y1, x2, y2, d in B:
            if abs(x1 - x2) < 1 and abs(x - x1) < tol and min(y1, y2) - tol <= y <= max(y1, y2) + tol: out.append(d)
            elif abs(y1 - y2) < 1 and abs(y - y1) < tol and min(x1, x2) - tol <= x <= max(x1, x2) + tol: out.append(d)
        return out
    S = collections.defaultdict(list)
    for l in open(geom, encoding='utf-8-sig').read().splitlines():
        p = l.split('|')
        if p[0] == 'S' and p[2] == 'SPDSNOTEPOSITION': S[p[1]].append([float(v) for v in p[3:7]])
    bad = []
    for n in notes(SX, SY, 59400, H):
        segs = [(a - SX, b - SY, c - SX, d - SY) for a, b, c, d in S.get(n['h'], [])]
        if not segs: continue
        m = re.search(r'C(\d+)', n['l1'] + n['l2']); dn = int(m.group(1)) if m else None
        TG = n['pts'][1:]
        ticks = [s for s in segs if 150 < math.hypot(s[2] - s[0], s[3] - s[1]) < 260 and any(math.hypot((s[0] + s[2]) / 2 - q[0], (s[1] + s[3]) / 2 - q[1]) < 25 for q in TG)]
        lines = [s for s in segs if s not in ticks and math.hypot(s[2] - s[0], s[3] - s[1]) > 1]
        tc = [((s[0] + s[2]) / 2, (s[1] + s[3]) / 2) for s in ticks]
        # 1) every tick must be at a leader END lying on a bar of the note's Ø
        ends = collections.Counter()
        for s in lines:
            for p in ((s[0], s[1]), (s[2], s[3])): ends[(round(p[0]), round(p[1]))] += 1
        endpts = [p for p, c in ends.items() if c == 1]
        for c in tc:
            ds = bar_at(*c)
            def inside(sg, q, tol=8):
                x1, y1, x2, y2 = sg; L = math.hypot(x2 - x1, y2 - y1)
                if L < 1: return False
                t = ((q[0] - x1) * (x2 - x1) + (q[1] - y1) * (y2 - y1)) / L / L
                dd = abs((q[0] - x1) * (y2 - y1) - (q[1] - y1) * (x2 - x1)) / L
                return dd < tol and 80 / L < t < 1 - 80 / L
            isend = not any(inside(sg, c) for sg in lines)
            if not ds: bad.append((n['h'], n['l1'], 'tick not on a bar', c))
            elif dn and dn not in ds: bad.append((n['h'], n['l1'], 'tick on a bar of other Ø %s' % ds, c))
            elif not isend: bad.append((n['h'], n['l1'], 'tick at a crossing (line goes on)', c))
        for sg in ticks:
            a = abs(math.degrees(math.atan2(sg[3] - sg[1], sg[2] - sg[0]))) % 180
            if min(a, 180 - a) > 70 and bar_at((sg[0] + sg[2]) / 2, (sg[1] + sg[3]) / 2): bad.append((n['h'], n['l1'], 'tick ~parallel to a vertical bar (invisible)', ((sg[0] + sg[2]) / 2, (sg[1] + sg[3]) / 2)))
        # 2) a leader end on a bar must carry a tick
        endpts = [e for e in endpts if not any(inside(sg, e) for sg in lines)] if tc else endpts
        for e in endpts:
            if bar_at(*e) and not any(math.hypot(e[0] - c[0], e[1] - c[1]) < 25 for c in tc): bad.append((n['h'], n['l1'], 'end on a bar without tick', e))
    if show:
        for b in bad: print(b[0], b[1], b[2], (round(b[3][0]), round(b[3][1])))
    return bad
if __name__ == '__main__':
    b = run(float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]); print('BAD', len(b))
