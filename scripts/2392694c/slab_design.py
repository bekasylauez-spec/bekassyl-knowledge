# Slab dop reinforcement from LIRA «Арматура в пластинах» (as_pl6.csv), method of Фм-1 (Obsidian 02_Фундамент):
# base Ø12 @200 (analog 5.1), dop bars between base bars (same level), As_eff of a line = mean of the cell and its
# neighbour across the bar, segments where As_eff > base, Ø by the deficit, + anchorage 40d, clipped to the slab
# (no bar over an opening, Obsidian 05_Плиты), neighbouring lines grouped into zones (first/last bar + 200хN).
# Bekassyl 05.11: bars parallel to a rigel never inside the rigel strip; bay layout starts 50 from the rigel face.
import csv, pickle, json, math, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model as M

BARS = [(10, 3.93), (12, 5.65), (14, 7.70), (16, 10.05), (18, 12.72), (20, 15.71), (22, 19.01), (25, 24.54)]
KG = {8: .395, 10: .617, 12: .888, 14: 1.21, 16: 1.58, 18: 2.0, 20: 2.47, 22: 2.98, 25: 3.85}
BASE_D, BASE_A = 12, 5.65
LAN = 40
STEP = 50
MINB, PEN, BRIDGE = 5, 150, 1500
KEYS = [('bot_x', 0, 'x'), ('top_x', 1, 'x'), ('bot_y', 2, 'y'), ('top_y', 3, 'y')]


def cells(Z):
    els, nodes = pickle.load(open(os.path.join(HERE, 'lira6', 'm.pkl'), 'rb'))
    AS = {}
    for r in csv.reader(open(os.path.join(HERE, 'arm', 'as_pl6.csv'), encoding='utf-8', errors='replace'), delimiter=';'):
        if len(r) < 12 or not r[4].strip().isdigit(): continue
        try: v = [float(x) for x in r[8:12]]
        except ValueError: continue
        e = int(r[4]); AS[e] = [max(a, b) for a, b in zip(AS.get(e, [0, 0, 0, 0]), v)]
    env = {}
    for i, r in enumerate(els):
        if int(r[0]) not in (41, 42, 44): continue
        ns = [nodes[int(k) - 1] for k in r[2:]]
        zs = [n[2] for n in ns]
        Zs = Z if isinstance(Z, (list, tuple)) else [Z]
        if max(zs) - min(zs) > 1e-3 or not any(abs(zs[0] - z) < 1e-3 for z in Zs): continue
        xs = [n[0] * 1000 for n in ns]; ys = [M.fy(n[1]) for n in ns]
        key = (round(min(xs)), round(min(ys)), round(max(xs)), round(max(ys)))
        a = AS.get(i + 1, [0, 0, 0, 0])
        if key in env: env[key]['As'] = [max(p, q) for p, q in zip(env[key]['As'], a)]      # envelope over the levels
        else: env[key] = dict(x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys), As=list(a))
    return list(env.values())


class Slab:
    def __init__(self, Z, rect, openings, rx, ry):
        self.C = cells(Z); self.rect = rect; self.open = openings; self.rx = rx; self.ry = ry
        # bucket index
        self.idx = {}
        for c in self.C:
            for i in range(int(c['x0'] // 1000), int(c['x1'] // 1000) + 1):
                for j in range(int(c['y0'] // 1000), int(c['y1'] // 1000) + 1):
                    self.idx.setdefault((i, j), []).append(c)

    def cell_at(self, x, y):
        for c in self.idx.get((int(x // 1000), int(y // 1000)), []):
            if c['x0'] - 1 <= x <= c['x1'] + 1 and c['y0'] - 1 <= y <= c['y1'] + 1: return c
        return None

    def in_open(self, x, y, m=0):
        return any(a - m <= x <= c + m and b - m <= y <= d + m for a, b, c, d in self.open)

    def base_lines(self, axis):
        """positions of base bars across: bars along x lie at y (rigels ry), bars along y at x (rigels rx)"""
        x0, y0, x1, y1 = self.rect
        lo, hi, strips = (y0, y1, self.ry) if axis == 'x' else (x0, x1, self.rx)
        bounds, cur = [], lo
        for a, b in sorted(strips):
            if b <= lo or a >= hi: continue
            if a > cur: bounds.append((cur, a))
            cur = max(cur, b)
        if cur < hi: bounds.append((cur, hi))
        return bounds

    def dop_positions(self, axis):
        out = []
        for a, b in self.base_lines(axis):
            p = a + 50 + 100
            while p <= b - 50: out.append(p); p += 200
        return out

    def eff_line(self, k, axis, pos):
        x0, y0, x1, y1 = self.rect
        lo, hi = (x0, x1) if axis == 'x' else (y0, y1)
        res = []; s = lo + 50
        while s <= hi - 50:
            x, y = (s, pos) if axis == 'x' else (pos, s)
            v = None
            if not self.in_open(x, y):
                c = self.cell_at(x, y)
                v = 0.0
                if c is not None:
                    if axis == 'x':
                        o = self.cell_at(x, c['y0'] - 1) if y - c['y0'] < c['y1'] - y else self.cell_at(x, c['y1'] + 1)
                    else:
                        o = self.cell_at(c['x0'] - 1, y) if x - c['x0'] < c['x1'] - x else self.cell_at(c['x1'] + 1, y)
                    v = (c['As'][k] + (o['As'][k] if o else c['As'][k])) / 2
            res.append((s, v))
            s += STEP
        return res

    def free_runs(self, axis, pos):
        """parts of a bar line lying on the slab (between openings), minus cover 50 at the edges"""
        x0, y0, x1, y1 = self.rect
        lo, hi = (x0 + 50, x1 - 50) if axis == 'x' else (y0 + 50, y1 - 50)
        cuts = []
        for a, b, c, d in self.open:
            if axis == 'x' and b <= pos <= d: cuts.append((a - 50, c + 50))
            if axis == 'y' and a <= pos <= c: cuts.append((b - 50, d + 50))
        runs, cur = [], lo
        for a, b in sorted(cuts):
            if a > cur: runs.append((cur, a))
            cur = max(cur, b)
        if cur < hi: runs.append((cur, hi))
        return runs


def bar_for(need):
    for d, a in BARS:
        if a >= need - 1e-6: return d
    return None


def rnd(v, m=50, up=True):
    return (math.ceil(v / m) if up else math.floor(v / m)) * m


def design(S, maxd=20):
    res = {}
    for key, k, axis in KEYS:
        lines = []
        for p in S.dop_positions(axis):
            prof = S.eff_line(k, axis, p)
            segs, cur = [], None
            for s, v in prof:
                need = (v or 0) - BASE_A
                if v is not None and need > 0.01:
                    if cur is None: cur = [s, s, need]
                    else: cur[1] = s; cur[2] = max(cur[2], need)
                elif cur is not None: segs.append(cur); cur = None
            if cur: segs.append(cur)
            runs = S.free_runs(axis, p)
            out = []
            for s0, s1, need in segs:
                d = bar_for(need) or 25
                flag = None
                if d > maxd: flag = 'need Ø%d' % d; d = maxd
                la = rnd(LAN * d)
                run = next((r for r in runs if r[0] - 1 <= s0 <= r[1] + 1), runs[0])
                a = max(run[0], rnd(s0 - la, 50, False)); b = min(run[1], rnd(s1 + la, 50))
                if a - run[0] < la: a = run[0]
                if run[1] - b < la: b = run[1]
                out.append([a, b, d, round(need + BASE_A, 2), flag])
            out.sort(); mg = []
            for o in out:
                same_run = mg and any(r[0] <= mg[-1][0] and o[1] <= r[1] for r in runs)
                if mg and same_run and o[0] <= mg[-1][1] + BRIDGE:
                    mg[-1][1] = max(mg[-1][1], o[1]); mg[-1][2] = max(mg[-1][2], o[2]); mg[-1][3] = max(mg[-1][3], o[3])
                    mg[-1][4] = mg[-1][4] or o[4]
                else: mg.append(o)
            lines.append((p, mg))
        # group consecutive lines (step 200 within one bay) whose pieces overlap
        groups, open_g = [], []
        prevp = None
        for p, mg in lines:
            if prevp is not None and p - prevp > 250:      # rigel strip between: close all groups
                groups += open_g; open_g = []
            prevp = p
            nxt, used = [], set()
            for g in open_g:
                hit = None
                s0, s1 = g['pieces'][-1][1], g['pieces'][-1][2]
                for i, o in enumerate(mg):
                    if i in used: continue
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

            def cost(i, j):
                d = max(q[3] for q in P[i:j + 1]); s0 = min(q[1] for q in P[i:j + 1]); s1 = max(q[2] for q in P[i:j + 1])
                return (j - i + 1) * (s1 - s0) / 1000 * KG[d] + PEN, d, s0, s1
            best = [0.0] + [1e18] * n; cut = [0] * (n + 1)
            for j in range(1, n + 1):
                for i in range(max(0, j - 80), j):
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
        # drop tiny peaks (< 4 bars and < 1500 long) — Obsidian: zone needs >= 4 cells
        zones = [z for z in zones if z['n'] >= 3 or z['s1'] - z['s0'] >= 1500]
        res[key] = split_long(resolve(round300(S, axis, clip_runs(S, axis, resolve(merge_adjacent(clip_runs(S, axis, zones)))))))
    return res


def resolve(zones, gap=50):
    """Bekassyl 04.11: two dop zones never share bar positions — the stronger (Ø, then area) keeps the place,
    the weaker loses the overlapping lines (split) or is trimmed along the bar, with a 50 gap"""
    def lines(z): return set(range(int(z['p0']), int(z['p1']) + 1, 200))
    changed = True
    while changed:
        changed = False
        zs = sorted(zones, key=lambda z: (-z['d'], -(z['n'] * (z['s1'] - z['s0']))))
        for i, A in enumerate(zs):
            for B in zs[i + 1:]:
                common = lines(A) & lines(B)
                if not common or min(A['s1'], B['s1']) - max(A['s0'], B['s0']) <= -gap: continue
                # option 1: trim B along the bar if A covers one end of B
                t = None
                if A['s0'] <= B['s0'] + 1 and A['s1'] < B['s1']: t = ('s0', A['s1'] + gap)
                elif A['s1'] >= B['s1'] - 1 and A['s0'] > B['s0']: t = ('s1', A['s0'] - gap)
                Lrest = (B['s1'] - (A['s1'] + gap)) if t and t[0] == 's0' else ((A['s0'] - gap) - B['s0']) if t else 0
                keep_lines = sorted(lines(B) - common)
                if t and Lrest >= 1000 and (len(keep_lines) < len(lines(B)) / 2 or len(common) == len(lines(B))):
                    B[t[0]] = t[1]
                else:
                    zones.remove(B)
                    run = []
                    for p in keep_lines + [None]:
                        if p is not None and (not run or p - run[-1] == 200): run.append(p); continue
                        if run:
                            nz = dict(B); nz['p0'], nz['p1'], nz['n'] = run[0], run[-1], len(run); zones.append(nz)
                        run = [p] if p is not None else []
                changed = True; break
            if changed: break
    return [z for z in zones if z['s1'] - z['s0'] >= 700]


def merge_adjacent(zones):
    """zones of one face in neighbouring lines (gap <= 400) with overlapping extents -> one zone (max Ø, envelope)"""
    changed = True
    while changed:
        changed = False
        for i, A in enumerate(zones):
            for B in zones[i + 1:]:
                if B['p0'] - A['p1'] > 400 or A['p0'] - B['p1'] > 400: continue
                if max(A['p0'], B['p0']) <= min(A['p1'], B['p1']): continue
                ov = min(A['s1'], B['s1']) - max(A['s0'], B['s0'])
                if ov < 0.5 * min(A['s1'] - A['s0'], B['s1'] - B['s0']): continue
                if abs(A['d'] - B['d']) > 4: continue
                lo, hi = min(A['p0'], B['p0']), max(A['p1'], B['p1'])
                A.update(d=max(A['d'], B['d']), s0=min(A['s0'], B['s0']), s1=max(A['s1'], B['s1']), p0=lo, p1=hi,
                         n=int(round((hi - lo) / 200)) + 1, req=max(A['req'], B['req']), flag=A['flag'] or B['flag'])
                zones.remove(B); changed = True; break
            if changed: break
    return zones


def clip_runs(S, axis, zones):
    """every bar of a zone must lie on the slab: split the zone by the free run of each line, clip the extents"""
    out = []
    for z in zones:
        sig = []
        for p in range(int(z['p0']), int(z['p1']) + 1, 200):
            r = next((r for r in S.free_runs(axis, p) if r[0] - 1 <= (z['s0'] + z['s1']) / 2 <= r[1] + 1), None)
            if r is None:
                r = max(S.free_runs(axis, p), key=lambda r: min(r[1], z['s1']) - max(r[0], z['s0']))
            sig.append((p, max(z['s0'], r[0]), min(z['s1'], r[1])))
        run = []
        for item in sig + [None]:
            if item is not None and run and abs(item[1] - run[-1][1]) < 1 and abs(item[2] - run[-1][2]) < 1:
                run.append(item); continue
            if run:
                nz = dict(z); nz.update(p0=run[0][0], p1=run[-1][0], n=len(run), s0=run[0][1], s1=run[0][2])
                if nz['s1'] - nz['s0'] >= 700: out.append(nz)
            run = [item] if item is not None else []
    return out


def round300(S, axis, zones):
    """BDM rule: dop lengths in multiples of 300 — extend inside the free run of every bar of the zone"""
    for z in zones:
        lo, hi = -1e9, 1e9
        for p in range(int(z['p0']), int(z['p1']) + 1, 200):
            r = next((r for r in S.free_runs(axis, p) if r[0] - 1 <= z['s0'] and z['s1'] <= r[1] + 1), None)
            if r: lo, hi = max(lo, r[0]), min(hi, r[1])
        L = z['s1'] - z['s0']; L3 = math.ceil(L / 300 - 1e-6) * 300; ext = L3 - L
        a = min(ext / 2, z['s0'] - lo); b = min(ext - a, hi - z['s1']); a = min(ext - b, z['s0'] - lo)
        if a + b >= ext - 1: z['s0'] -= a; z['s1'] += b
    return zones


LAPD = {10: 610, 12: 730, 14: 860, 16: 980, 18: 1100, 20: 1220}


def split_long(zones, stock=11700):
    """dop bars longer than the stock length -> two bars lapped 61d in the middle (same lines, overlap = lap only)"""
    out = []
    for z in zones:
        L = z['s1'] - z['s0']
        if L <= stock: out.append(z); continue
        lap = LAPD.get(z['d'], 61 * z['d'])
        h = math.ceil(((L + lap) / 2) / 300) * 300
        a = dict(z); b = dict(z)
        a['s1'] = z['s0'] + h; b['s0'] = z['s1'] - h
        a['lap'] = b['lap'] = True
        out += [a, b]
    return out


def report(R):
    tot = 0
    for key, zs in R.items():
        print('==', key, len(zs))
        for z in sorted(zs, key=lambda z: (z['p0'], z['s0'])):
            L = z['s1'] - z['s0']; tot += z['n'] * L / 1000 * KG[z['d']]
            print('   Ø%d L=%d x%d  p %d..%d  s %d..%d  req %.1f %s' % (z['d'], L, z['n'], z['p0'], z['p1'], z['s0'], z['s1'], z['req'], z['flag'] or ''))
    print('dop mass kg %.0f' % tot)


PM1 = dict(Z=-0.1, rect=(-125, -3275, 20175, 31175),
           openings=[(6925, 15475, 10275, 17775), (6925, 18025, 10275, 20575), (10525, 15475, 13125, 20575)],
           rx=[(-125, 325), (6575, 7025), (13025, 13475), (19725, 20175)],
           ry=[(-1225, -775), (23125, 23575), (28625, 29075)])

import lev
CUR = dict(Z=lev.CUR['z'], rect=lev.CUR['rect'], openings=lev.CUR['openings'], rx=lev.CUR['rx'], ry=lev.CUR['ry'])
if __name__ == '__main__':
    S = Slab(CUR['Z'], CUR['rect'], CUR['openings'], CUR['rx'], CUR['ry'])
    R = design(S)
    report(R)
    json.dump(R, open(os.path.join(HERE, 'arm', lev.CUR['tag'] + '_design.json'), 'w'), indent=1)
