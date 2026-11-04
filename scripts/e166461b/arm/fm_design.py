# Фм-1 design by bar lines: base Ø16 @200 (analog), dop bars @200 between base bars (offset 100, same level),
# for every dop line the required As along it (cell As averaged with the neighbour perpendicular to the bar),
# segments where As > base, Ø by the deficit, extended by the anchorage, then neighbouring lines with the same
# Ø and similar extents merged into zones (first/last bar + «200хN» as in the analog 3.3–3.6).
import json, math, sys, bisect
sys.path.insert(0, '.')
import model as M

C = json.load(open('arm/fm_cells.json'))
BARS = [(10, 3.93), (12, 5.65), (14, 7.70), (16, 10.05), (18, 12.72), (20, 15.71), (22, 19.01), (25, 24.54), (28, 30.79), (32, 40.21)]
BASE_D, BASE_A = 16, 10.05
COVER = 50                     # bar end / first bar from the slab edge (analog section 1-1: 50)
LAN = 40                       # anchorage of dop bars beyond the zone, ×d (assumption, rounded up to 50 mm)
FX0, FY0, FX1, FY1 = M.FM
KEYS = [('bot_x', 0, 'x'), ('top_x', 1, 'x'), ('bot_y', 2, 'y'), ('top_y', 3, 'y')]
STEP = 50
MINB, PEN = 6, 100
BRIDGE = 2000
KG = {10: .617, 12: .888, 14: 1.21, 16: 1.58, 18: 2.0, 20: 2.47, 22: 2.98, 25: 3.85, 28: 4.83, 32: 6.31}


def cell_at(x, y):
    for c in C:
        if c['x0'] - 1 <= x <= c['x1'] + 1 and c['y0'] - 1 <= y <= c['y1'] + 1: return c
    return None


def build_grid():
    xs = sorted(set([round(c['x0']) for c in C] + [round(c['x1']) for c in C]))
    ys = sorted(set([round(c['y0']) for c in C] + [round(c['y1']) for c in C]))
    return xs, ys


def eff_line(k, axis, pos):
    """As_eff along a bar line: bars along x at y=pos (axis 'x') or along y at x=pos (axis 'y'). Returns [(s, As)] every STEP."""
    out = []
    lo, hi = (FX0, FX1) if axis == 'x' else (FY0, FY1)
    s = lo + COVER
    while s <= hi - COVER:
        x, y = (s, pos) if axis == 'x' else (pos, s)
        c = cell_at(x, y)
        v = 0.0
        if c is not None:
            # neighbour perpendicular to the bar: the cell on the other side of the nearer edge
            if axis == 'x':
                d0, d1 = y - c['y0'], c['y1'] - y
                o = cell_at(x, c['y0'] - 1) if d0 < d1 else cell_at(x, c['y1'] + 1)
            else:
                d0, d1 = x - c['x0'], c['x1'] - x
                o = cell_at(c['x0'] - 1, y) if d0 < d1 else cell_at(c['x1'] + 1, y)
            v = (c['As'][k] + (o['As'][k] if o else c['As'][k])) / 2
        out.append((s, v))
        s += STEP
    return out


def bar_for(need):
    for d, a in BARS:
        if a >= need - 1e-6: return d, a
    return None


def rnd(v, m=50, up=True):
    return (math.ceil(v / m) if up else math.floor(v / m)) * m


def segments(prof):
    segs = []; cur = None
    for s, v in prof:
        need = v - BASE_A
        if need > 0.01:
            if cur is None: cur = [s, s, need]
            else: cur[1] = s; cur[2] = max(cur[2], need)
        else:
            if cur is not None: segs.append(cur); cur = None
    if cur is not None: segs.append(cur)
    return segs


def design():
    res = {}
    for key, k, axis in KEYS:
        lo, hi = (FY0, FY1) if axis == 'x' else (FX0, FX1)        # positions of bar lines across
        a0, a1 = (FX0, FX1) if axis == 'x' else (FY0, FY1)        # along the bar
        base0 = lo + COVER
        lines = []
        p = base0 + 100
        while p <= hi - COVER:
            segs = segments(eff_line(k, axis, p))
            out = []
            for s0, s1, need in segs:
                bf = bar_for(need)
                d = bf[0] if bf else 32
                la = rnd(LAN * d)
                x0 = max(a0 + COVER, rnd(s0 - la, 50, up=False)); x1 = min(a1 - COVER, rnd(s1 + la, 50))
                if x0 - (a0 + COVER) < la: x0 = a0 + COVER            # close to the edge: run to the edge (bracket Ск)
                if (a1 - COVER) - x1 < la: x1 = a1 - COVER
                out.append([x0, x1, d, round(need + BASE_A, 2), None if bf else 'need>Ø32'])
            # merge overlapping pieces on one line (the stronger Ø wins over the whole run)
            out.sort()
            mg = []
            for o in out:
                if mg and o[0] <= mg[-1][1] + BRIDGE: mg[-1][1] = max(mg[-1][1], o[1]); mg[-1][2] = max(mg[-1][2], o[2]); mg[-1][3] = max(mg[-1][3], o[3])
                else: mg.append(o)
            lines.append((p, mg))
            p += 200
        # groups: consecutive lines whose pieces overlap (any Ø); then bands by Ø with a DP (mass + penalty per zone)
        groups = []; open_g = []
        for p, mg in lines:
            nxt = []; used = set()
            for g in open_g:
                hit = None
                for i, o in enumerate(mg):
                    if i in used: continue
                    s0, s1 = g['pieces'][-1][1], g['pieces'][-1][2]
                    if min(o[1], s1) - max(o[0], s0) > 0.5 * min(o[1] - o[0], s1 - s0): hit = i; break
                if hit is None: groups.append(g)
                else:
                    used.add(hit); o = mg[hit]; g['pieces'].append((p, o[0], o[1], o[2], o[3], o[4])); nxt.append(g)
            for i, o in enumerate(mg):
                if i not in used: nxt.append(dict(pieces=[(p, o[0], o[1], o[2], o[3], o[4])]))
            open_g = nxt
        groups += open_g
        zones = []
        for g in groups:
            P = g['pieces']; n = len(P)
            def cost(i, j):          # band P[i..j]
                d = max(q[3] for q in P[i:j + 1]); s0 = min(q[1] for q in P[i:j + 1]); s1 = max(q[2] for q in P[i:j + 1])
                return (j - i + 1) * (s1 - s0) / 1000 * KG[d] + PEN, d, s0, s1
            best = [0.0] + [1e18] * n; cut = [0] * (n + 1)
            for j in range(1, n + 1):
                for i in range(max(0, j - 60), j):
                    if j - i < min(MINB, n) and not (i == 0 and j == n): continue
                    c = best[i] + cost(i, j - 1)[0]
                    if c < best[j]: best[j] = c; cut[j] = i
            j = n; bands = []
            while j > 0:
                i = cut[j]; bands.append((i, j - 1)); j = i
            for i, j in reversed(bands):
                _, d, s0, s1 = cost(i, j)
                zones.append(dict(d=d, s0=s0, s1=s1, p0=P[i][0], p1=P[j][0], n=j - i + 1, req=max(q[4] for q in P[i:j + 1]),
                                  flag=next((q[5] for q in P[i:j + 1] if q[5]), None)))
        zones = [z for z in zones if z['n'] >= 2 or z['s1'] - z['s0'] >= 1500]
        res[key] = zones
    return res


if __name__ == '__main__':
    R = design()
    tot = 0
    for key, zs in R.items():
        print('==', key, len(zs))
        for z in sorted(zs, key=lambda z: (z['p0'], z['s0'])):
            L = z['s1'] - z['s0']; tot += z['n'] * L / 1000 * {10: .617, 12: .888, 14: 1.21, 16: 1.58, 18: 2.0, 20: 2.47, 22: 2.98, 25: 3.85, 28: 4.83, 32: 6.31}[z['d']]
            print('   Ø%d L=%d x%d  p %d..%d  s %d..%d  req %.1f %s' % (z['d'], L, z['n'], z['p0'], z['p1'], z['s0'], z['s1'], z['req'], z['flag'] or ''))
    print('dop mass kg %.0f' % tot)
    json.dump(R, open('arm/fm_design.json', 'w'), indent=1)
