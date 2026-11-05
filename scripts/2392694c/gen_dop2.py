# Dop sheets with collision-free labels (Bekassyl 06.11: oc.py TOTAL 0 on every dop sheet).
# Same content/style as gen_dop.py (zone = first + last bar, chain along the bars split at axes, binding chain
# «axis | 200х(n-1)», SPDS 3-point position note), but every text / dim / note is placed by searching a free spot
# against the REAL geometry already on the sheet (background of scheme 2.x, frame, bars, earlier labels) with the
# oc.py rules: text/text, line/text, shelf/line, text on hatch, inside frame / off stamp.
#   phase A: sheet base (frame, title, background, bars) -> save, dxfout, geomdump -> obstacles
#   phase B: place chains then notes -> ops
#   env SLAB=pm1 python gen_dop2.py <key> <k>
import gx, json, os, sys, math, subprocess
from shapely.geometry import box, LineString, Polygon
from shapely.strtree import STRtree
import gen62 as G
import lev
C = lev.CUR
S = gx.S
SW = 59400.0
AXX = [0, 6800, 13250, 20050]
AXY = [0, 5000, 14750, 22750, 28750]
SX0, SY0, SX1, SY1 = C['rect']
TITLES = {'bot_x': 'нижней зоны по буквенным осям', 'top_x': 'верхней зоны по буквенным осям',
          'bot_y': 'нижней зоны по цифровым осям', 'top_y': 'верхней зоны по цифровым осям'}
T_BAR, T_NOTE, T_DV, T_DH = 'TPL_BAR', 'TPL_NOTE', 'TPL_DV', 'TPL_DH'
FRAME = ['2B479C', '2B47A1', '2B47A2']
CW, TH, TG = 180.0, 250.0, 225.0          # char width, text height, text centre offset from the dim line (calibrated)
W = os.path.join(S, 'chk').replace(os.sep, '/')
from gen_dop import positions


def base_ops(key, k):
    dx = SW * (k - 2)
    X, Y = lev.ox(k), C['oy']
    def P(a, b): return [X + a, Y + b, 0]
    x0 = 231579 + dx
    ops = [{'t': 'eraseregion', 'win': [x0 - 1, 455930, x0 + SW + 1, 497950]}]
    for h in FRAME: ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [dx, 0]})
    name = 'Дополнительное армирование плиты перекрытия %s %s на отм %s' % (C['name'], TITLES[key], C['mark'])
    ops.append({'t': 'clone', 'h': '2B47A5', 'base': [0, 0], 'to': [dx - 2500, -650], 'text': '{\\L\\C0;' + name + '}'})
    ops.append({'t': 'clone', 'h': '2B479D', 'base': [0, 0], 'to': [dx, 0], 'text': '{\\C0;' + name + '}'})
    ops.append({'t': 'clone', 'h': '2B479F', 'base': [0, 0], 'to': [dx, 0], 'text': '7.%d' % k})
    mp = gx.tagmap()
    for tg, h in mp.items():
        if tg.startswith(C['bgp']): ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [SW * (k - C['km']), 0]})
    along_x = key.endswith('_x')
    for zi, z in enumerate(R[key]):
        for p in sorted({z['p0'], z['p1']}):
            s, e = (P(z['s0'], p), P(z['s1'], p)) if along_x else (P(p, z['s0']), P(p, z['s1']))
            ops.append({'t': 'lineset', 'h': T_BAR, 's': s, 'e': e})
    ops.append({'t': 'trepl', 'win': [x0 - 5, 455900, x0 + SW + 5, 498000], 'pairs': [['КЖ-7.1 ... 7.8', 'КЖ-7.%d ... 7.%d' % (C['k0'], C['k0'] + 7)]]})
    ops.append({'t': 'save'})
    return ops, x0


def dump(x0):
    out = gx.run([{'t': 'dxfout', 'file': W + '/live.dxf'}, {'t': 'geomdump', 'win': [x0 - 10, 455900, x0 + SW + 10, 498100], 'file': W + '/geom.txt'}], 'dmp')
    print([l for l in out.splitlines() if 'geomdump' in l or 'ERR' in l])


def load(x0, name):
    """oc.py parse (texts, segs, hatches) -> obstacles of this sheet"""
    json.dump({name: [x0, 455939, x0 + SW, 497939]}, open(W + '/one.json', 'w'))
    src = open(W + '/oc.py', encoding='utf-8').read()
    src = src[:src.index('total = 0')]
    old = sys.argv
    sys.argv = ['oc.py', W + '/live.dxf', W + '/one.json', '--geom=' + W + '/geom.txt']
    ns = {'__name__': 'ocparse'}
    exec(compile(src, 'oc.py', 'exec'), ns)
    sys.argv = old
    win = box(x0, 455939, x0 + SW, 497939)
    texts = [(p, poly) for p, poly, s in ns['texts'] if win.contains(poly.centroid)]
    segs = [ls for p, ls in ns['segs'] if win.intersects(ls)]
    hat = [hg for h, hg in ns['hatches'] if win.intersects(hg)]
    return texts, segs, hat


class Board:
    def __init__(self, x0, texts, segs, hat):
        self.segs = list(segs); self.texts = [t for p, t in texts]; self.hat = hat
        self.inner = box(x0 + 2000 + 50, 455939 + 550, x0 + SW - 550, 497939 - 550)
        self.stamp = box(x0 + SW - 500 - 18500 - 50, 455939, x0 + SW, 455939 + 500 + 5500 + 50)
        self._idx()

    def _idx(self):
        self.st = STRtree(self.segs) if self.segs else None
        self.tt = STRtree(self.texts) if self.texts else None

    def text_bad(self, poly):
        n = 0
        if not self.inner.contains(poly) or poly.intersects(self.stamp): n += 5
        q = poly.buffer(60)
        if self.st is not None:
            for i in self.st.query(q):
                if self.segs[i].intersects(q): n += 1
        if self.tt is not None:
            for i in self.tt.query(q):
                if self.texts[i].intersects(q): n += 1
        for hg in self.hat:
            if hg.intersects(poly): n += 1
        return n

    def lines_bad(self, lines):
        n = 0
        if self.tt is None: return 0
        for ls in lines:
            for i in self.tt.query(ls):
                if self.texts[i].buffer(15).intersects(ls): n += 1
        return n

    def shelf_bad(self, ls):
        n = 0
        if self.st is not None:
            for i in self.st.query(ls):
                if self.segs[i].intersects(ls): n += 1
        return n

    def add(self, texts=(), lines=()):
        self.texts += list(texts); self.segs += list(lines); self._idx()


def tw(t): return CW * len(t) + 40


def hbox(xc, yc, t): w = tw(t); return box(xc - w / 2, yc - TH / 2, xc + w / 2, yc + TH / 2)
def vbox(xc, yc, t): w = tw(t); return box(xc - TH / 2, yc - w / 2, xc + TH / 2, yc + w / 2)


def chain_try(B, X, Y, segs_, horiz, dl, base_pts, texts):
    """segs_ [(a,b)] along the chain axis; horiz: dim line horizontal at y=dl (else vertical at x=dl);
    base_pts: feature coordinate across (ext-line start) per chain point; texts per segment.
    returns (bad, ops, newtexts, newlines)"""
    bad = 0; ops = []; nt = []; nl = []
    pts = sorted({a for a, b in segs_} | {b for a, b in segs_})
    a0, a1 = pts[0], pts[-1]
    # dim line and extension lines
    if horiz:
        nl.append(LineString([(X + a0 - 120, Y + dl), (X + a1 + 120, Y + dl)]))
        for p in pts: nl.append(LineString([(X + p, Y + base_pts[p]), (X + p, Y + dl + (100 if dl > base_pts[p] else -100))]))
    else:
        nl.append(LineString([(X + dl, Y + a0 - 120), (X + dl, Y + a1 + 120)]))
        for p in pts: nl.append(LineString([(X + base_pts[p], Y + p), (X + dl + (100 if dl > base_pts[p] else -100), Y + p)]))
    bad += B.lines_bad(nl)
    import itertools
    per = []
    for i, (a, b) in enumerate(segs_):
        t = texts[i]; w = tw(t); c = (a + b) / 2
        fits = b - a >= w + 120
        cands = []
        if fits: cands += [c, a + w / 2 + 120, b - w / 2 - 120]
        for ex in (0, 250, 500, 800):
            if i == len(segs_) - 1 or ex == 0: cands.append(b + w / 2 + 160 + ex)
            if i == 0 or ex == 0: cands.append(a - w / 2 - 160 - ex)
        if not fits: cands.append(c)
        opts = []
        for j, cc in enumerate(cands):
            poly = hbox(X + cc, Y + dl + TG, t) if horiz else vbox(X + dl - TG, Y + cc, t)
            sc = B.text_bad(poly) + (3 if (not fits and cc == c) else 0) + (0 if j == 0 else 0.01 * j)
            ext = None
            if cc - w / 2 < a or cc + w / 2 > b:          # text outside -> AutoCAD extends the dim line up to it
                e0, e1 = min(a, cc - w / 2), max(b, cc + w / 2)
                ext = LineString([(X + e0, Y + dl), (X + e1, Y + dl)]) if horiz else LineString([(X + dl, Y + e0), (X + dl, Y + e1)])
                sc += B.lines_bad([ext])
            opts.append((sc, cc, poly, ext))
        opts.sort(key=lambda q: q[0]); per.append(opts[:6])
    best = None
    for combo in itertools.product(*per):
        sc = sum(o[0] for o in combo)
        if best is not None and sc >= best[0]: continue
        polys = [o[2] for o in combo]
        if any(polys[i].intersects(polys[j]) for i in range(len(polys)) for j in range(i + 1, len(polys))): continue
        exts = [o[3] for o in combo if o[3] is not None]
        if any(e.intersects(p) for e in exts for p in polys if not e.touches(p)) and len(polys) > 1:
            sc += 0.5 * sum(1 for e in exts for p in polys if e.intersects(p))
        if best is None or sc < best[0]: best = (sc, combo)
    if best is None: best = (99, [o[0] for o in per])
    bad += int(best[0] + 0.5)
    for i, (a, b) in enumerate(segs_):
        sc, cc, poly, ext = best[1][i]; t = texts[i]
        nt.append(poly)
        if ext is not None: nl.append(ext)
        tx = [X + cc, Y + dl, 0] if horiz else [X + dl, Y + cc, 0]
        txt = t if t.startswith('200х') else ''
        if horiz: ops.append({'t': 'dim', 'h': T_DH, 'p1': [X + a, Y + base_pts[a], 0], 'p2': [X + b, Y + base_pts[b], 0], 'dl': [X + a, Y + dl, 0], 'rot': 0, 'txt': txt, 'tx': tx})
        else: ops.append({'t': 'dim', 'h': T_DV, 'p1': [X + base_pts[a], Y + a, 0], 'p2': [X + base_pts[b], Y + b, 0], 'dl': [X + dl, Y + a, 0], 'rot': math.pi / 2, 'txt': txt, 'tx': tx})
    return bad, ops, nt, nl


def place(key, k, B, order='LBN'):
    X, Y = lev.ox(k), C['oy']
    along_x = key.endswith('_x')
    zl = R[key]
    ops = []; report = []
    for st in order:
        {'L': stL, 'B': stB, 'N': stN}[st](key, k, B, X, Y, along_x, zl, ops, report)
    ops.append({'t': 'save'})
    return ops, report


def stL(key, k, B, X, Y, along_x, zl, ops, report):
    # ---- 1. length chains along the bars (split at axes)
    for zi, z in enumerate(zl):
        p0, p1, s0, s1 = z['p0'], z['p1'], z['s0'], z['s1']
        ax2 = AXX if along_x else AXY
        pts = [s0] + [a for a in ax2 if s0 + 300 < a < s1 - 300] + [s1]
        segs_ = list(zip(pts, pts[1:])); texts = [str(int(round(b - a))) for a, b in segs_]
        best = None
        for side, d in [(1, 300), (-1, 550), (1, 600), (-1, 850), (1, 950), (-1, 1200), (1, 1350), (-1, 1600), (1, 1800), (-1, 2050), (1, 2300), (-1, 2550)]:
            bar = p1 if side > 0 else p0
            dl = bar + side * d
            bp = {p: bar for p in pts}
            r = chain_try(B, X, Y, segs_, along_x, dl, bp, texts)
            if best is None or r[0] < best[0]: best = r
            if r[0] == 0: break
        ops += best[1]; B.add(best[2], best[3])
        if best[0]: report.append(('L', zi, best[0]))


def stB(key, k, B, X, Y, along_x, zl, ops, report):
    # ---- 2. binding chains across the bars at the start or the end
    for zi, z in enumerate(zl):
        n = z['n']; p0, p1, s0, s1 = z['p0'], z['p1'], z['s0'], z['s1']
        axes = AXY if along_x else AXX
        edge0 = SY0 if along_x else SX0
        cand = [a for a in axes + [edge0] if a <= p0 - 100]
        b0 = max(cand) if cand else None
        cp = ([b0] if b0 is not None and 300 <= p0 - b0 < 6000 else []) + [p0] + ([p1] if p1 > p0 else [])
        segs_ = list(zip(cp, cp[1:]))
        if not segs_: continue
        texts = ['200х%d' % (n - 1) if (a, b) == (p0, p1) else str(int(round(b - a))) for a, b in segs_]
        best = None
        for at, sg in [(s0, -1), (s1, 1)]:
            pass
        for d in (350, 700, 1050, 1400, 1800, 2200):
            for at, sg in ((s0, -1), (s1, 1)):
                dl = at + sg * d
                bp = {p: at for p in cp}
                r = chain_try(B, X, Y, segs_, not along_x, dl, bp, texts)
                if best is None or r[0] < best[0]: best = r
                if r[0] == 0: break
            if best[0] == 0: break
        ops += best[1]; B.add(best[2], best[3])
        if best[0]: report.append(('B', zi, best[0]))


def stN(key, k, B, X, Y, along_x, zl, ops, report):
    # ---- 3. position notes (shelf to the left of the origin, box 1200 x 840)
    for zi, z in enumerate(zl):
        n = z['n']; d = z['d']; L = int(round(z['s1'] - z['s0']))
        p0, p1, s0, s1 = z['p0'], z['p1'], z['s0'], z['s1']
        num = pos[(d, L)]
        cands = []
        fr = sorted([i / 20 for i in range(21)], key=lambda f: abs(f - 0.5))
        offs = (520, 900, 1300, 1800, 2300)
        for f in fr:
            c = s0 + 50 + f * (s1 - s0 - 100)
            if along_x:
                ys = ([(p0 + p1) / 2] if p1 - p0 >= 940 else []) + [v for o in offs for v in (p1 + o, p0 - o)]
                for oy in ys: cands.append((c, oy, [(c, p1), (c, p0)], c))
            else:
                xs = ([p1 - 100] if p1 - p0 >= 1400 else []) + [p0 - 110] + [p0 - o for o in (600, 1100, 1600, 2100)]
                for ox in xs: cands.append((ox, c, [(p1, c), (p0, c)], None))
        cands.sort(key=lambda q: (abs(q[1] - (p0 + p1) / 2) if along_x else abs(q[0] - (p0 + p1) / 2)) // 300)
        best = None
        for ox, oy, arr, lx in cands:
            poly = box(X + ox - 1200, Y + oy - 420, X + ox + 20, Y + oy + 420)
            shelf = LineString([(X + ox - 1170, Y + oy), (X + ox, Y + oy)])
            lead = [LineString([(X + ox, Y + oy), (X + a[0], Y + a[1])]) for a in arr]
            lead = [l for l in lead if l.length > 1]
            sc = B.text_bad(poly) + B.shelf_bad(shelf) * 2 + B.lines_bad(lead)
            if best is None or sc < best[0]: best = (sc, ox, oy, arr, poly, shelf, lead)
            if sc == 0: break
        sc, ox, oy, arr, poly, shelf, lead = best
        B.add([poly], [shelf] + lead)
        if sc: report.append(('N', zi, sc))
        tg = 'N%s_%d' % (key, zi)
        ops.append({'t': 'clone', 'h': T_NOTE, 'tag': tg})
        items = [[0, X + ox, Y + oy], [1, X + arr[0][0], Y + arr[0][1]], [2, X + arr[1][0], Y + arr[1][1]]]
        ops.append({'t': 'spmove', 'h': tg, 'items': items})
        ops.append({'t': 'noteh', 'h': tg, 'l1': str(num), 'l2': 'ш.200'})


R = json.load(open(os.path.join(S, 'arm', C['tag'] + '_design.json')))
pos = positions(R)
if __name__ == '__main__':
    key, k = sys.argv[1], int(sys.argv[2])
    ops, x0 = base_ops(key, k)
    out = gx.run(ops, 'dopA_' + key); print([l for l in out.splitlines() if 'ERR' in l][:5])
    dump(x0)
    ob = load(x0, '7.%d' % k)
    res = []
    for order in ('LBN', 'NLB', 'LNB', 'BLN', 'NBL'):
        B = Board(x0, *ob)
        o_, r_ = place(key, k, B, order)
        res.append((sum(v[2] for v in r_), order, o_, r_)); print(order, r_)
        if not r_: break
    res.sort(key=lambda q: q[0]); _, order, ops, rep = res[0]
    out = gx.run(ops, 'dopB_' + key)
    print(key, len(R[key]), 'unresolved', rep, [l for l in out.splitlines() if 'ERR' in l][:8])
