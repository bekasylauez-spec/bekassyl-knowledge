# -*- coding: utf-8 -*-
"""Generator of БДМ Блок 1 slab sheets from the Б3 analog (clone templates, then build)."""
import json, math, pickle, os
import geom, design as D0
from shapely.geometry import box, LineString, Polygon

S = geom.S
PARK = -1000000.0  # templates are parked dy = PARK

# ---------------- templates (analog handles) ----------------
TPL = {
    'kark': 'BCEF6B0B', 'axisV': 'BCEF6BC2', 'axisH': 'BCEF6BEA', 'bubD': 'BCEF6BC3', 'bubL': 'BCEF6BEB',
    'plita5': 'BCEF6BB5', 'plita50': 'BCEF4DCA', 'hole': 'BCEF6BB8',
    'dimH': 'BCEF6C3E', 'dimV': 'BCEF6D82',
    'bar10': 'BCEF7725', 'bar12': 'BCEF847F', 'bar14': 'BCEF7E4E',
    'mlX': 'BCEF7757', 'mlY': 'BCEF7E35',
    'dimLenH': 'BCEF7727', 'dimLenV': 'BCEF7E05', 'dimCrossV': 'BCEF773F', 'dimCrossH': 'BCEF7E1D',
    'barMain': 'BCEF5CEE', 'chain': 'BCEF5CF2', 'ml1Y': 'BCEF61D4', 'ml1X': 'BCEF61D5',
    'skB': 'BCEF62C6', 'skT': 'BCEF62B4', 'skL': 'BCEF62C8', 'skR': 'BCEF62C2', 'skTxt': 'BCEF62B5',
    'secmark': 'BCEF5332',
}
# template anchor points (analog absolute coords) used as clone base
ANCH = {
    'mlX': (-508137, -3136100), 'mlY': (-397772, -3166930),
    'ml1Y': (-691322, -3166500), 'ml1X': (-691322, -3166500),
    'bubD': None, 'bubL': None,
}

def park_ops():
    ops = []
    for k, h in TPL.items():
        ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [0, PARK], 'tag': 'T_' + k})
    return ops

def tp(k):
    return 'T_' + k

def anchor(k):
    a = ANCH[k]
    return [a[0], a[1] + PARK]

# ---------------- sheets ----------------
class Sheet:
    def __init__(self, name, x0, top, ax0, yA, w, h, z):
        self.name, self.x0, self.top, self.ax0, self.yA, self.w, self.h, self.z = name, x0, top, ax0, yA, w, h, z
        self.occ = []  # occupied rectangles (sheet coords)
    def T(self, X, Y):
        return [self.x0 + self.ax0 + (X - 12000), self.top + self.yA + Y]

PM1 = 'Пм1'; PM2 = 'Пм2'
def pm1_sheet(k):
    return Sheet('pm1_%d' % k, -791072 + (k - 1) * 90000, -3120000, 6500, -51000, 84100, 59400, '7.0')
def pm2_sheet(k):
    return Sheet('pm2_%d' % k, -791072 + (k - 1) * 64000, -3200000, 6000, -23000, 59400, 42000, '4.5')

AXX = geom.AXX; AXY = geom.AXY

def axes_for(z):
    if z == '7.0':
        return ['3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14'], ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж']
    return ['3', '4', '5', '6'], ['А', 'Б']

# ---------------- occupancy helpers ----------------
def rect_hit(a, b, pad=0):
    return not (a[2] + pad <= b[0] or b[2] + pad <= a[0] or a[3] + pad <= b[1] or b[3] + pad <= a[1])

def free(sh, r, pad=40):
    return not any(rect_hit(r, q, pad) for q in sh.occ)

def occupy(sh, r):
    sh.occ.append(r)

def text_rect(cx, cy, s, h=250, horiz=True, align='c'):
    w = 0.85 * h * len(s) + 60
    if horiz:
        return (cx - w / 2, cy - h / 2 - 40, cx + w / 2, cy + h / 2 + 40)
    return (cx - h / 2 - 40, cy - w / 2, cx + h / 2 + 40, cy + w / 2)

# ---------------- common plan ----------------
def plan_common(sh, kind):
    """kind: 'opal' | 'main' | 'dop'"""
    ops = []
    z = sh.z; sl = geom.slab(z)
    dx, dy = axes_for(z)
    xs = [AXX[a] for a in dx]; ys = [AXY[a] for a in dy]
    x_l, y_b, x_r, y_t = sl['outer'].bounds
    # background beams (as analog: dashed gray outlines)
    ob = sl['outer'].buffer(300)
    for b in sl['beams']:
        if not ob.intersects(box(*b)): continue
        p = [sh.T(b[0], b[1]), sh.T(b[2], b[1]), sh.T(b[2], b[3]), sh.T(b[0], b[3])]
        ops.append({'t': 'pl', 'p': p, 'closed': True, 'tpl': tp('kark')})
    # digit axes
    ytop = max(ys) + 1200
    for a in dx:
        X = AXX[a]
        if a == '13':
            p = [sh.T(X, ytop), sh.T(X, -2100), sh.T(X - 500, -2700), sh.T(X - 500, -3200)]
            bx = X - 500
        elif a == '14':
            p = [sh.T(X, ytop), sh.T(X, -2100), sh.T(X + 400, -2700), sh.T(X + 400, -3200)]
            bx = X + 400
        else:
            p = [sh.T(X, ytop), sh.T(X, -3250)]; bx = X
        ops.append({'t': 'pl', 'p': p, 'tpl': tp('axisV')})
        ops.append({'t': 'clone', 'h': tp('bubD'), 'base': [-508622, -3174650 + PARK], 'to': sh.T(bx, -3650), 'attr': a})
        occupy(sh, tuple(sh.T(bx - 420, -4070) + sh.T(bx + 420, -3230)))
    # letter axes
    xr = x_r + 900
    for a in dy:
        Y = AXY[a]
        ops.append({'t': 'pl', 'p': [sh.T(12000 - 2585, Y), sh.T(xr, Y)], 'tpl': tp('axisH')})
        ops.append({'t': 'clone', 'h': tp('bubL'), 'base': [-517557, -3171000 + PARK], 'to': sh.T(12000 - 2985, Y), 'attr': a})
    # slab contour
    pt = 'plita50' if kind == 'opal' else 'plita5'
    ops.append({'t': 'pl', 'p': [sh.T(*c) for c in list(sl['outer'].exterior.coords)[:-1]], 'closed': True, 'tpl': tp(pt)})
    # openings
    for H in sl['holes']:
        g = H['geom']
        if H['kind'] == 'rect':
            x0, y0, x1, y1 = g.bounds
            ops.append({'t': 'pl', 'p': [sh.T(x0, y0), sh.T(x1, y0), sh.T(x1, y1), sh.T(x0, y1)], 'closed': True, 'tpl': tp(pt)})
            w, h = x1 - x0, y1 - y0
            ops.append({'t': 'pl', 'p': [sh.T(x0, y0), sh.T(x0 + 0.15 * w, y0 + 0.89 * h), sh.T(x1, y1)], 'tpl': tp('hole')})
        else:
            cx, cy = H['c']; r = H['d'] / 2
            ops.append({'t': 'circle', 'c': sh.T(cx, cy), 'r': r, 'tpl': tp(pt)})
            a1, a2 = math.radians(225), math.radians(45)
            p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1)); p2 = (cx + r * math.cos(a2), cy + r * math.sin(a2))
            ops.append({'t': 'pl', 'p': [sh.T(*p1), sh.T(cx - 0.55 * r, cy + 0.6 * r), sh.T(*p2)], 'tpl': tp('hole')})
    # chains
    off = {'opal': (1300, 2100), 'dop': (1300, 2100), 'main': (2100, 2900)}[kind]
    # bottom: slab edges + axes
    bx = sorted(set([x_l, x_r] + xs))
    ops += chainH(sh, bx, y_b, y_b - off[0])
    ops += chainH(sh, [xs[0], xs[-1]], y_b, y_b - off[1])
    # left
    lefty = sorted(set([y_b] + [AXY[a] for a in dy] + [yy for (xx, yy) in sl['outer'].exterior.coords if abs(xx - x_l) < 1]))
    ops += chainV(sh, lefty, x_l, x_l - off[0])
    ops += chainV(sh, [0, max(ys)], x_l, x_l - off[1])
    # right
    righty = sorted(set([AXY[a] for a in dy] + [yy for (xx, yy) in sl['outer'].exterior.coords if abs(xx - x_r) < 1]))
    ops += chainV(sh, righty, x_r, x_r + off[0])
    # top (steps of the north edge)
    if z == '7.0':
        tx = sorted(set([36000, 40500, 42000, 42250, 59250, 59500, 65900, 73100, 73350]))
        ops += chainH(sh, tx, y_t, y_t + 1300)
    return ops

def chainH(sh, xs, yref, ydl):
    ops = []
    segs = [(a, b) for a, b in zip(xs[:-1], xs[1:]) if b - a >= 1]
    for i, (a, b) in enumerate(segs):
        op = {'t': 'dim', 'h': tp('dimH'), 'p1': sh.T(a, yref), 'p2': sh.T(b, yref), 'dl': sh.T(b, ydl), 'rot': 0}
        if b - a < 700:
            w = 0.85 * 250 * len(str(int(round(b - a)))) / 2 + 120
            if i == len(segs) - 1 or (i > 0 and segs[i - 1][1] - segs[i - 1][0] < 700): op['tx'] = sh.T(b + w, ydl + 90)
            elif i == 0: op['tx'] = sh.T(a - w, ydl + 90)
        ops.append(op)
    y = sh.T(0, ydl)[1]
    occupy(sh, (sh.T(xs[0], 0)[0], y - 50, sh.T(xs[-1], 0)[0], y + 450))
    return ops

def chainV(sh, ys, xref, xdl):
    ops = []
    segs = [(a, b) for a, b in zip(ys[:-1], ys[1:]) if b - a >= 1]
    for i, (a, b) in enumerate(segs):
        op = {'t': 'dim', 'h': tp('dimV'), 'p1': sh.T(xref, a), 'p2': sh.T(xref, b), 'dl': sh.T(xdl, b), 'rot': math.pi / 2}
        if b - a < 700:
            w = 0.85 * 250 * len(str(int(round(b - a)))) / 2 + 120
            if i == len(segs) - 1 or (i > 0 and segs[i - 1][1] - segs[i - 1][0] < 700): op['tx'] = sh.T(xdl - 90, b + w)
            elif i == 0: op['tx'] = sh.T(xdl - 90, a - w)
        ops.append(op)
    x = sh.T(xdl, 0)[0]
    occupy(sh, (x - 450, sh.T(0, ys[0])[1], x + 50, sh.T(0, ys[-1])[1]))
    return ops

# ---------------- main (base) reinforcement ----------------
def beam_half(z, dirn, a):
    # half width of the axis beam (for X bars: letter axis beams; for Y bars: digit axis beams)
    if dirn == 'X':
        return 300 if a in (13900, 27500) and z == '7.0' else 250
    return 250

def main_bars(sh):
    """first/last base bar in every band, chains and the pos-1 marks (analog sheet 2 style)"""
    ops = []; z = sh.z; sl = geom.slab(z)
    dx, dy = axes_for(z)
    xa = [AXX[a] for a in dx if a != '14']; ya = [AXY[a] for a in dy]
    x_l, y_b, x_r, y_t = sl['outer'].bounds
    stats = {'X': 0.0, 'Y': 0.0}
    ml_done = {'X': False, 'Y': False}
    # Y bars (vertical) in digit bands
    for a, b in zip(xa[:-1], xa[1:]):
        f = a + beam_half(z, 'Y', a) + 50; lmax = b - beam_half(z, 'Y', b) - 50
        n = int((lmax - f) // 200); l = f + 200 * n
        for c in (f, l):
            for s, e in D0.segs_on_slab(z, 'Y', c, sl, cover=30):
                ops.append({'t': 'lineset', 'h': tp('barMain'), 's': sh.T(c, s), 'e': sh.T(c, e)})
        yd = y_b - 1100
        ops.append({'t': 'dim', 'h': tp('chain'), 'p1': sh.T(a, y_b), 'p2': sh.T(f, y_b), 'dl': sh.T(f, yd), 'rot': 0, 'tx': sh.T(f + 330, yd + 90)})
        ops.append({'t': 'dim', 'h': tp('chain'), 'p1': sh.T(f, y_b), 'p2': sh.T(l, y_b), 'dl': sh.T(l, yd), 'rot': 0, 'txt': '200х%d=<>' % n})
        ops.append({'t': 'dim', 'h': tp('chain'), 'p1': sh.T(l, y_b), 'p2': sh.T(b, y_b), 'dl': sh.T(b, yd), 'rot': 0, 'tx': sh.T(l - 330, yd + 90)})
        if not ml_done['Y']:
            ym = (AXY['В'] + AXY['Г']) / 2 if z == '7.0' else 4500
            ops.append({'t': 'ml', 'h': tp('ml1Y'), 'base': anchor('ml1Y'), 'to': sh.T((f + l) / 2, ym), 'text': '1', 'arrows': [sh.T(f, ym), sh.T(l, ym)]})
            ml_done['Y'] = True
    # X bars (horizontal) in letter bands
    for a, b in zip(ya[:-1], ya[1:]):
        f = a + beam_half(z, 'X', a) + 50; lmax = b - beam_half(z, 'X', b) - 50
        n = int((lmax - f) // 200); l = f + 200 * n
        for c in (f, l):
            for s, e in D0.segs_on_slab(z, 'X', c, sl, cover=30):
                ops.append({'t': 'lineset', 'h': tp('barMain'), 's': sh.T(s, c), 'e': sh.T(e, c)})
        xd = x_l - 1100
        ops.append({'t': 'dim', 'h': tp('chain'), 'p1': sh.T(x_l, a), 'p2': sh.T(x_l, f), 'dl': sh.T(xd, f), 'rot': math.pi / 2, 'tx': sh.T(xd - 90, f + 330)})
        ops.append({'t': 'dim', 'h': tp('chain'), 'p1': sh.T(x_l, f), 'p2': sh.T(x_l, l), 'dl': sh.T(xd, l), 'rot': math.pi / 2, 'txt': '200х%d=<>' % n})
        ops.append({'t': 'dim', 'h': tp('chain'), 'p1': sh.T(x_l, l), 'p2': sh.T(x_l, b), 'dl': sh.T(xd, b), 'rot': math.pi / 2, 'tx': sh.T(xd - 90, l - 330)})
        if not ml_done['X']:
            xm = (xa[1] + xa[2]) / 2 + 1000
            ops.append({'t': 'ml', 'h': tp('ml1X'), 'base': anchor('ml1X'), 'to': sh.T(xm, (f + l) / 2), 'text': '1', 'arrows': [sh.T(xm, f), sh.T(xm, l)]})
            ml_done['X'] = True
    return ops

def base_quantities(z):
    """running metres of pos.1 (Ø10 @200, 2 dirs x 2 faces) incl. laps 61d per 11.7 m stock"""
    sl = geom.slab(z); tot = 0.0
    for dirn in ('X', 'Y'):
        for c in D0.lines_for(z, dirn, base=True):
            for s, e in D0.segs_on_slab(z, dirn, c, sl, cover=30):
                L = e - s
                nl = max(0, math.ceil(L / 11700) - 1)
                tot += L + nl * 610
    return 2 * tot / 1000.0

def sk_marks(sh):
    """Ск1 U-bars along free edges: symbol + text (analog style); returns ops and edge length"""
    ops = []; z = sh.z; sl = geom.slab(z)
    total = 0.0
    G = sl['geom'].buffer(1)
    def side_of(x, y, horiz):
        if horiz: return 'B' if G.contains(LineString([(x, y + 5), (x, y + 300)])) else 'T'
        return 'L' if G.contains(LineString([(x + 5, y), (x + 300, y)])) else 'R'
    ring = list(sl['outer'].exterior.coords)
    for p, q in zip(ring[:-1], ring[1:]):
        L = math.hypot(q[0] - p[0], q[1] - p[1]); total += L
        if L < 900: continue
        horiz = abs(q[1] - p[1]) < 1
        if horiz:
            a, b = sorted((p[0], q[0])); pts = [a] + [x for x in sorted(AXX.values()) if a + 300 < x < b - 300] + [b]
            for u, v in zip(pts[:-1], pts[1:]):
                if v - u < 900: continue
                m = u + 0.78 * (v - u); ops += sk_one(sh, m, p[1], side_of(m, p[1], True))
        else:
            a, b = sorted((p[1], q[1])); pts = [a] + [y for y in sorted(AXY.values()) if a + 300 < y < b - 300] + [b]
            for u, v in zip(pts[:-1], pts[1:]):
                if v - u < 900: continue
                m = u + 0.78 * (v - u); ops += sk_one(sh, p[0], m, side_of(p[0], m, False))
    for H in sl['holes']:
        g = H['geom']; total += g.length
        if H['kind'] != 'rect': continue
        x0, y0, x1, y1 = g.bounds; w, h = x1 - x0, y1 - y0
        sides = []
        if w >= 1500: sides += [('h', x0 + (0.3 if h < 1300 else 0.5) * w - 100, y0), ('h', x0 + (0.7 if h < 1300 else 0.5) * w - 100, y1)]
        if h >= 1500: sides += [('v', x0, y0 + 0.5 * h - 100), ('v', x1, y0 + 0.5 * h - 100)]
        for k, x, y in sides:
            ops += sk_one(sh, x, y, side_of(x, y, k == 'h'))
    return ops, total

def sk_one(sh, x, y, side):
    # side = where the free edge is relative to the slab: B (edge below slab), T, L, R
    if side == 'B':
        p = [(x, y - 80), (x, y - 393), (x + 200, y - 393), (x + 200, y - 80)]; tx = (x + 100, y - 825)
    elif side == 'T':
        p = [(x, y + 80), (x, y + 393), (x + 200, y + 393), (x + 200, y + 80)]; tx = (x + 100, y + 640)
    elif side == 'L':
        p = [(x - 80, y), (x - 393, y), (x - 393, y + 200), (x - 80, y + 200)]; tx = (x - 880, y + 100)
    else:
        p = [(x + 80, y), (x + 393, y), (x + 393, y + 200), (x + 80, y + 200)]; tx = (x + 880, y + 100)
    ops = [{'t': 'pl', 'p': [sh.T(*q) for q in p], 'tpl': tp('skB')},
           {'t': 'clone', 'h': tp('skTxt'), 'base': [-690362.71, -3153400.0 + PARK], 'to': sh.T(*tx)}]
    return ops

# ---------------- dop zones ----------------
BAR_TPL = {8: 'bar10', 10: 'bar10', 12: 'bar12', 14: 'bar14', 16: 'bar14', 18: 'bar14', 20: 'bar14', 22: 'bar14', 25: 'bar14'}

def positions(res, z, start=2):
    """unique (d,L) numbered in sheet order: face 0,1,2,3"""
    pos = {}; n = start
    for f in range(4):
        for Z in sorted(res[z][f], key=lambda q: (-q['d'], -q['L'])):
            k = (Z['d'], Z['L'])
            if k not in pos: pos[k] = n; n += 1
    return pos

def dop_sheet(sh, zones, face, pos):
    ops = []; dirn = 'X' if face in (0, 1) else 'Y'
    sl = geom.slab(sh.z)
    # occupancy of bars first
    for Z in zones:
        c0, c1 = min(Z['cs']), max(Z['cs'])
        if dirn == 'X': r = sh.T(Z['s'], c0) + sh.T(Z['e'], c1)
        else: r = sh.T(c0, Z['s']) + sh.T(c1, Z['e'])
        occupy(sh, (r[0] - 30, r[1] - 30, r[2] + 30, r[3] + 30))
    for Z in sorted(zones, key=lambda q: (min(q['cs']), q['s'])):
        d = Z['d']; lay = 'ф%d_арм' % d
        c0, c1 = min(Z['cs']), max(Z['cs']); s, e = Z['s'], Z['e']; n = len(Z['cs'])
        p = pos[(d, Z['L'])]
        bt = tp(BAR_TPL[d])
        for c in sorted(set([c0, c1])):
            if dirn == 'X': ops.append({'t': 'lineset', 'h': bt, 's': sh.T(s, c), 'e': sh.T(e, c), 'layer': lay, 'laylike': 'ф14_арм'})
            else: ops.append({'t': 'lineset', 'h': bt, 's': sh.T(c, s), 'e': sh.T(c, e), 'layer': lay, 'laylike': 'ф14_арм'})
        L = e - s
        ops += place_zone(sh, dirn, c0, c1, s, e, n, p)
    return ops


def overlap_area(sh, r, pad=40):
    t = 0.0
    for q in sh.occ:
        w = min(r[2], q[2]) + pad - max(r[0], q[0]); h = min(r[3], q[3]) + pad - max(r[1], q[1])
        if w > 0 and h > 0: t += w * h
    return t

def pick(sh, cands):
    for c in cands:
        if free(sh, c[0]): return c
    return min(cands, key=lambda c: overlap_area(sh, c[0]))

def place_zone(sh, dirn, c0, c1, s, e, n, p):
    """length dim, cross dim '200хN' and the position mark of one zone, each in a free spot.
    Dim text may slide only along its dim line (rule: move text along the line only)."""
    ops = []; L = e - s; Ls = str(int(L))
    fr = (0.5, 0.3, 0.7, 0.15, 0.85)
    if dirn == 'X':
        cands = []
        for off in (350, 700, 1050, 1400):
            for cb, cd in ((c1, c1 + off), (c0, c0 - off)):
                for f in fr:
                    tx = s + f * L; ty = cd + (180 if cd > cb else -180)
                    cands.append((text_rect(*sh.T(tx, ty), Ls), cb, cd, f, tx, ty))
        r, cb, cd, f, tx, ty = pick(sh, cands)
        op = {'t': 'dim', 'h': tp('dimLenH'), 'p1': sh.T(s, cb), 'p2': sh.T(e, cb), 'dl': sh.T(e, cd), 'rot': 0}
        if f != 0.5: op['tx'] = sh.T(tx, cd + (90 if cd > cb else -270))
        ops.append(op); occupy(sh, r)
        occupy(sh, tuple(sh.T(s, min(cb, cd)) + sh.T(e, max(cb, cd))))
        if n > 2:
            txt = '200х%d' % (n - 1); W = c1 - c0; cands = []
            for off in (350, 700, 1050, 1400):
                for xb, xd in ((e, e + off), (s, s - off)):
                    for f in fr:
                        ty = c0 + f * W; tx = xd + (180 if xd > xb else -180)
                        cands.append((text_rect(*sh.T(tx, ty), txt, horiz=False), xb, xd, f, ty))
            r, xb, xd, f, ty = pick(sh, cands)
            op = {'t': 'dim', 'h': tp('dimCrossV'), 'p1': sh.T(xb, c0), 'p2': sh.T(xb, c1), 'dl': sh.T(xd, c1), 'rot': math.pi / 2, 'txt': txt}
            if f != 0.5: op['tx'] = sh.T(xd - 90, ty)
            ops.append(op); occupy(sh, r)
        ym = (c0 + c1) / 2; cands = []
        for f in (0.33, 0.5, 0.66, 0.2, 0.8, 0.42, 0.58, 0.12, 0.9):
            xl = s + f * L
            ty = ym if c1 - c0 >= 900 else c0 - 500
            cands.append((text_rect(*sh.T(xl - 200, ty), str(p)), xl, ty))
            if c1 - c0 >= 900: cands.append((text_rect(*sh.T(xl - 200, c0 - 500), str(p)), xl, c0 - 500))
            for dd in (500, 1000, 1500):
                cands.append((text_rect(*sh.T(xl - 200, c1 + dd), str(p)), xl, c1 + dd))
                cands.append((text_rect(*sh.T(xl - 200, c0 - dd), str(p)), xl, c0 - dd))
        r, xl, ty = pick(sh, cands)
        arr = [sh.T(xl, c0)] + ([sh.T(xl, c1)] if n > 1 else [])
        ops.append({'t': 'ml', 'h': tp('mlX'), 'base': anchor('mlX'), 'to': sh.T(xl, ty), 'text': str(p), 'arrows': arr}); occupy(sh, r)
    else:
        cands = []
        for off in (350, 700, 1050, 1400):
            for cb, cd in ((c0, c0 - off), (c1, c1 + off)):
                for f in fr:
                    ty = s + f * L; tx = cd + (180 if cd > cb else -180)
                    cands.append((text_rect(*sh.T(tx, ty), Ls, horiz=False), cb, cd, f, ty))
        r, cb, cd, f, ty = pick(sh, cands)
        op = {'t': 'dim', 'h': tp('dimLenV'), 'p1': sh.T(cb, s), 'p2': sh.T(cb, e), 'dl': sh.T(cd, e), 'rot': math.pi / 2}
        if f != 0.5: op['tx'] = sh.T(cd + (270 if cd > cb else -90), ty)
        ops.append(op); occupy(sh, r)
        occupy(sh, tuple(sh.T(min(cb, cd), s) + sh.T(max(cb, cd), e)))
        if n > 2:
            txt = '200х%d' % (n - 1); W = c1 - c0; cands = []
            for off in (350, 700, 1050, 1400):
                for yb, yd in ((e, e + off), (s, s - off)):
                    for f in fr:
                        tx = c0 + f * W; ty = yd + (180 if yd > yb else -180)
                        cands.append((text_rect(*sh.T(tx, ty), txt), yb, yd, f, tx))
            r, yb, yd, f, tx = pick(sh, cands)
            op = {'t': 'dim', 'h': tp('dimCrossH'), 'p1': sh.T(c0, yb), 'p2': sh.T(c1, yb), 'dl': sh.T(c1, yd), 'rot': 0, 'txt': txt}
            if f != 0.5: op['tx'] = sh.T(tx, yd + 90)
            ops.append(op); occupy(sh, r)
        xm = (c0 + c1) / 2; cands = []
        for f in (0.35, 0.5, 0.65, 0.2, 0.8, 0.42, 0.58, 0.12, 0.9):
            yl = s + f * L
            tx = xm if c1 - c0 >= 900 else c0 - 550
            cands.append((text_rect(*sh.T(tx, yl + 300), str(p)), tx, yl))
            if c1 - c0 >= 900: cands.append((text_rect(*sh.T(c0 - 550, yl + 300), str(p)), c0 - 550, yl))
            for dd in (550, 1100, 1650):
                cands.append((text_rect(*sh.T(c1 + dd, yl + 300), str(p)), c1 + dd, yl))
                cands.append((text_rect(*sh.T(c0 - dd, yl + 300), str(p)), c0 - dd, yl))
        r, tx, yl = pick(sh, cands)
        arr = [sh.T(c0, yl)] + ([sh.T(c1, yl)] if n > 1 else [])
        ops.append({'t': 'ml', 'h': tp('mlY'), 'base': anchor('mlY'), 'to': sh.T(tx, yl), 'text': str(p), 'arrows': arr}); occupy(sh, r)
    return ops

def zone_counts(res, z, pos):
    cnt = {}
    for f in range(4):
        for Z in res[z][f]:
            k = (Z['d'], Z['L']); cnt[k] = cnt.get(k, 0) + len(Z['cs'])
    return cnt

if __name__ == '__main__':
    res, RS = pickle.load(open(S + r'\design.pkl', 'rb'))
    for z in res: D0.RAS[z] = D0.raster(z)
    for z in ('7.0', '4.5'):
        pos = positions(res, z)
        cnt = zone_counts(res, z, pos)
        print(z, 'positions', len(pos), sorted(((p, k, cnt[k]) for k, p in pos.items())))
        print('  base m', round(base_quantities(z), 1))
