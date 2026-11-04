# Block 3 slabs Пм1 (+7.000) and Пм2 (+4.500): build ops for the copy of the analog Б2.плита1.dwg.
# Local plan coords (mm): x from axis 22, y from axis А.
import json, math
from collections import defaultdict, OrderedDict
from shapely.geometry import Polygon, box, LineString, MultiLineString, Point
from shapely.ops import unary_union
from design import SLABS, slab_geom

ops = []
def add(**k): ops.append(k); return k

# ---------------- templates in the analog ----------------
T = dict(dim='BCEE9EF5', dimtxt='BCEEA30D', ml_zone='BCEEA57B', ml_base='BCEE9F1F', txt='BCEE9F22', sk='BCEE9F23',
         bubble='BCEC453D', title='BCEC7744', secmark='BCEE9F3E')
FR_A3 = 'BCEE9BF2'; FR_A2 = 'BCEDC0D3'
AN_R3 = [-791072, -744072, -697072, -650072, -603072]; AN_R3Y = -2964152       # Пм3 (+4.500) A3 sheets
AN_R1 = [-791072, -726989, -662907, -598507]; AN_R1Y = -2847852                # Пм1 (+7.000) A2 sheets
AN_R1S = (-534107, -2860152)                                                    # Пм1 spec, A3
A3 = (42000, 29700); A2 = (59400, 42000); A1 = (84100, 59400)

AXX = OrderedDict([('22', 0), ('23', 650), ('24', 5950), ('25', 11300), ('26', 17300), ('27', 23300), ('28', 29300), ('29', 35300),
                   ('30', 41300), ('31', 47300), ('32', 53300), ('33', 53950)])
AXY = OrderedDict([('А', 0), ('Б', 9000), ('В', 13900), ('Г', 21000), ('Д', 27500), ('Е', 36000), ('Ж', 39000)])

# ---------------- geometry from the scheme (DWG БДМ Блок 4 Без СПДС) ----------------
def rects_from(fn, kind):
    out = []
    for l in open(fn, encoding='utf-8'):
        if not l.startswith('PL '): continue
        a = l.split(' ', 7)
        pts = eval(a[7])
        if kind == 'col' and a[2] == 'BYLAYER' and a[3] == '0' and a[4] == '30' and len(pts) == 4:
            out.append(Polygon(pts))
        if kind == 'beam' and a[2] == 'невидимая':
            out.append(Polygon(pts))
    return out

SL = {
    'P70': dict(name='Пм1', lvl='+7.000', lvlb='+6.800', geo='../b3/g3.txt', ax=list(AXX), ay=list(AXY), sheets0=1),
    'P45': dict(name='Пм2', lvl='+4.500', lvlb='+4.300', geo='../b3/g2.txt', ax=['22', '23', '24', '25', '26', '27'], ay=['А', 'Б', 'В'], sheets0=8),
}
for k, s in SL.items():
    g = slab_geom(k); s['g'] = g
    cols = [c for c in rects_from(s['geo'], 'col') if c.intersects(g)]
    beams = [b for b in rects_from(s['geo'], 'beam') if b.intersects(g)]
    s['under'] = unary_union(cols + beams).intersection(g.buffer(1))
    s['cols'] = cols

Z = json.load(open('zones4.json'))

def zrect(z):
    a, b = z['pos'][0] - 100, z['pos'][-1] + 100
    return box(z['L0'], a, z['L1'], b) if z['f'] in (0, 1) else box(a, z['L0'], b, z['L1'])

def premerge(k, small=12e6, grow=1.6, envmax=25e6):
    # small neighbouring zones of one face (any Ø) become one zone with the larger Ø when the envelope stays compact
    Zk = Z[k]; ch = True
    while ch:
        ch = False; best = None
        for i in range(len(Zk)):
            for j in range(i + 1, len(Zk)):
                p, q = Zk[i], Zk[j]
                if p['f'] != q['f']: continue
                rp, rq = zrect(p), zrect(q)
                if rp.area > small or rq.area > small: continue
                if rp.distance(rq) > 400: continue
                env = rp.union(rq).envelope
                r = env.area / max(rp.union(rq).area, 1)
                if r <= grow and env.area <= envmax and (best is None or r < best[0]): best = (r, i, j, env)
        if best:
            _, i, j, env = best; p, q = Zk[i], Zk[j]
            x0, y0, x1, y1 = env.bounds
            if p['f'] in (0, 1): L0, L1, P0, P1 = x0, x1, y0, y1
            else: L0, L1, P0, P1 = y0, y1, x0, x1
            pos = sorted(set(p['pos']) | set(q['pos'])); pos = [float(v) for v in range(int(pos[0]), int(pos[-1]) + 1, 200)]
            Zk[i] = dict(f=p['f'], d=max(p['d'], q['d']), pos=pos, n=len(pos), L0=L0, L1=L1)
            Zk.pop(j); ch = True

def split_by_slab(k):
    # every bar clipped to the slab (cover 30); a bar position belongs to one zone only (Bekassyl 04.11:
    # «2 түрлі доп арматура 1 жерге түсе алмайды») - stronger / larger zones take it first, weaker ones are cut around;
    # then bars with the same piece and step 200 form one zone, length down to the 300 module, centred in the piece
    gin = slab_geom(k).buffer(-30, join_style=2); out = []
    premerge(k)
    occ = defaultdict(list)                     # (face, pos) -> taken intervals
    order = sorted(Z[k], key=lambda z: (-z['d'], -len(z['pos']) * (z['L1'] - z['L0'])))
    for z in order:
        alongx = z['f'] in (0, 1); groups = defaultdict(list)
        for p in z['pos']:
            ln = LineString([(z['L0'] - 1, p), (z['L1'] + 1, p)]) if alongx else LineString([(p, z['L0'] - 1), (p, z['L1'] + 1)])
            for q in lines_of(ln.intersection(gin)):
                a, b = (q.bounds[0], q.bounds[2]) if alongx else (q.bounds[1], q.bounds[3])
                free = [(a, b)]
                for (u, v) in occ[(z['f'], p)]:
                    nxt = []
                    for (c, d) in free:
                        if v <= c or u >= d: nxt.append((c, d)); continue
                        if u - 50 > c: nxt.append((c, u - 50))
                        if v + 50 < d: nxt.append((v + 50, d))
                    free = nxt
                for (c, d) in free:
                    if d - c >= 1000: groups[(round(c), round(d))].append(p)
        for (a, b), ps in groups.items():
            ps.sort(); run = [ps[0]]
            for p in ps[1:] + [None]:
                if p is not None and p - run[-1] <= 201: run.append(p); continue
                # 300 module; the bar keeps the end that sits on a slab edge (supports and void edges carry the peaks)
                Lr = int((b - a) // 300 * 300); pm = run[len(run) // 2]
                bnd = slab_geom(k).boundary
                ea = bnd.distance(Point(a, pm) if z['f'] in (0, 1) else Point(pm, a)) < 120
                eb = bnd.distance(Point(b, pm) if z['f'] in (0, 1) else Point(pm, b)) < 120
                if ea and not eb: a2 = math.ceil(a / 10.0) * 10
                elif eb and not ea: a2 = math.floor((b - Lr) / 10.0) * 10
                else: a2 = math.ceil((a + (b - a - Lr) / 2) / 10.0) * 10
                out.append(dict(f=z['f'], d=z['d'], pos=run, n=len(run), L0=a2, L1=a2 + Lr, L=Lr))
                for q in run: occ[(z['f'], q)].append((a, b))
                if p is not None: run = [p]
    Z[k] = out

# ---------------- sheet placement ----------------
SH = {}
for i in range(6): SH[('P70', i)] = dict(X0=-791072 + i * 90000, Y0=-3120000, fmt=A1)
SH[('P70', 6)] = dict(X0=-791072 + 6 * 90000, Y0=-3120000, fmt=A3)
KINDS = {'P70': [('opal', None), ('main', None), ('dop', (0,)), ('dop', (1,)), ('dop', (2,)), ('dop', (3,))],
         'P45': [('opal', None), ('main', None), ('dop', (0, 2)), ('dop', (1, 3))]}
for i in range(5): SH[('P45', i)] = dict(X0=-791072 + i * 64000, Y0=-3200000, fmt=A2 if i < 4 else A3)
def org(k, i):
    s = SH[(k, i)]
    if k == 'P70': return s['X0'] + 6500, s['Y0'] - 51000
    return s['X0'] + 6000, s['Y0'] - 23000

# ---------------- primitives (local coords -> model) ----------------
class Sheet:
    def __init__(s, k, i): s.k = k; s.i = i; s.ox, s.oy = org(k, i)
    def P(s, x, y): return [round(s.ox + x, 2), round(s.oy + y, 2)]
    def pl(s, pts, closed=False, **kw): add(t='pl', pts=[s.P(*p) for p in pts], closed=closed, **kw)
    def line(s, x0, y0, x1, y1, **kw): add(t='line', p=s.P(x0, y0) + s.P(x1, y1), **kw)
    def dim(s, p1, p2, dl, rot=0, text=None):
        o = dict(t='clone', h=T['dimtxt'] if text else T['dim'], p1=s.P(*p1), p2=s.P(*p2), dl=s.P(*dl), rotd=rot)
        if text: o['text'] = text
        else: o['text'] = ''
        add(**o)
    def text(s, x, y, txt, rot=0, h=None):
        o = dict(t='clone', h=T['txt'], text=txt, rotd=rot, hmode=1, vmode=2, pos=s.P(x, y))
        if h: o['height'] = h
        add(**o)
    def bubble(s, x, y, name): add(t='clone', h=T['bubble'], to=s.P(x, y), att={'ОСЬ': name}, from_center=True)
    def ml(s, txt, textloc, arrows, dirx=-1, tpl='ml_zone'): add(t='ml', h=T[tpl], text=txt, textloc=s.P(*textloc), arrows=[s.P(*a) for a in arrows], dir=dirx)
    def mark(s, txt, p0, p1, vert):
        # analog position callout: text in the middle of the leader, arrows on the first and last bar
        (x0, y0), (x1, y1) = p0, p1
        if vert:
            tl = (x0 - 50, (y0 + y1) / 2 if y1 != y0 else y0 + 400)
            add(t='mlx', h='BCEEA57B', text=txt, textloc=s.P(*tl), arrows=[s.P(x0, y0), s.P(x1, y1)])
        else:
            tl = ((x0 + x1) / 2 if x1 != x0 else x0 + 400, y0 + 300)
            add(t='mlx', h='BCEEA57E', text=txt, textloc=s.P(*tl), arrows=[s.P(x0, y0), s.P(x1, y1)])
    def mark_old(s, txt, p0, p1, vert):
        # leader across the bars from p0 to p1 (+350 past p1), 45-degree ticks on the bars, number beyond the end
        (x0, y0), (x1, y1) = p0, p1
        if vert:
            e = y1 + 350; s.line(x0, y0, x0, e, layer='Txt_poz', lw=13)
            for y in sorted(set([y0, y1])): s.line(x0 - 80, y - 80, x0 + 80, y + 80, layer='Txt_poz', lw=13)
            s.text(x0, e + 230, txt)
        else:
            e = x1 + 350; s.line(x0, y0, e, y0, layer='Txt_poz', lw=13)
            for x in sorted(set([x0, x1])): s.line(x - 80, y0 - 80, x + 80, y0 + 80, layer='Txt_poz', lw=13)
            s.text(e + 230, y0, txt)

def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g): return [r for p in polys(g) for r in [p.exterior] + list(p.interiors)]
def holes(g): return [r for p in polys(g) for r in p.interiors]
HOLES = [h for h in SLABS['P70']['holes']]

def lines_of(geom):
    if geom.is_empty: return []
    if geom.geom_type == 'LineString': return [geom]
    if hasattr(geom, 'geoms'): return [g for g in geom.geoms if g.geom_type == 'LineString']
    return []

for _k in list(Z): split_by_slab(_k)

# ---------------- plan background ----------------
OPEN_KINK = {(4600, 8900): (699, 7958), (2550, 5600): (576, 4837)}

def background(sh, kind):
    s = SL[sh.k]; g = s['g']
    x0, y0, x1, y1 = g.bounds
    # hidden: beams + columns under the slab as one outline, edges on the slab contour skipped
    edge = g.boundary.buffer(5)
    und = s['under']
    for poly in (und.geoms if hasattr(und, 'geoms') else [und]):
        if poly.geom_type != 'Polygon': continue
        for ring in [poly.exterior] + list(poly.interiors):
            rest = LineString(ring.coords).difference(edge)
            for ln in lines_of(rest):
                if ln.length < 30: continue
                sh.pl(list(ln.coords), layer='Кж каркас', ltype='ADSK_Сверху', ltscale=100, color=6, lw=9)
    # slab contour and openings
    lw = 50 if kind == 'opal' else 5            # Bekassyl 04.11: contour 0.05 where reinforcement is drawn
    for ring in rings(g):
        sh.pl(list(ring.coords)[:-1], closed=True, layer='Plita', lw=lw, color=7)
    marks = [list(r.coords) for r in holes(g)]
    if sh.k == 'P70': marks.append([(41300, -250), (44300, -250), (44300, 6300), (41300, 6300)])   # stair well cut from the edge
    for ring in marks:
        # opening mark copied from the user's own fix (Б4.плита1 v2, 04.11): corner -> kink near the top-left -> opposite corner
        xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
        a, b, c, d = min(xs), min(ys), max(xs), max(ys)
        kx, ky = OPEN_KINK.get((round(c - a), round(d - b)), (0.15 * (c - a), 0.89 * (d - b)))
        sh.pl([(a, b), (a + kx, b + ky), (c, d)], layer='_0', lw=20)
    # axes
    ax = {n: AXX[n] for n in s['ax']}; ay = {n: AXY[n] for n in s['ay']}
    c1, c2, c3 = (1900, 2700, 4000) if kind == 'main' else (1300, 2100, 3400)
    yb = y0 - c3; xl = x0 - c3
    for n, x in ax.items():
        bx = x
        names = list(ax); j = names.index(n)
        if j + 1 < len(names) and ax[names[j + 1]] - x < 1000: bx = x - 500       # close axes (650): bubbles apart
        if j > 0 and x - ax[names[j - 1]] < 1000: bx = x + 400
        top = y1 + 900
        if bx != x: sh.pl([(x, top), (x, yb + 1500), (bx, yb + 900), (bx, yb + 400)], layer='kж оси', ltype='ACAD_ISO04W100', ltscale=50, color=1)
        else: sh.pl([(x, top), (x, yb + 400)], layer='kж оси', ltype='ACAD_ISO04W100', ltscale=50, color=1)
        sh.bubble(bx, yb, n)
    for n, y in ay.items():
        sh.pl([(x1 + 900, y), (xl + 400, y)], layer='kж оси', ltype='ACAD_ISO04W100', ltscale=50, color=1)
        sh.bubble(xl, y, n)
    # chains: bottom (slab edges + axes), overall between extreme axes; left the same
    xs_ax = sorted(ax.values()); ys_ax = sorted(ay.values())
    cy1, cy2 = y0 - c1, y0 - c2
    pts = sorted(set([round(x0)] + xs_ax + [round(x1)]))
    for a, b in zip(pts, pts[1:]): sh.dim((a, y0), (b, y0), (a, cy1))
    sh.dim((xs_ax[0], y0), (xs_ax[-1], y0), (xs_ax[0], cy2))
    cx1, cx2 = x0 - c1, x0 - c2
    left_edge = [y for p in polys(g) for (x, y) in p.exterior.coords if abs(x - x0) < 1]
    pts = sorted(set([round(v) for v in left_edge] + ys_ax))
    for a, b in zip(pts, pts[1:]): sh.dim((x0, a), (x0, b), (cx1, a), rot=90)
    sh.dim((x0, ys_ax[0]), (x0, ys_ax[-1]), (cx2, ys_ax[0]), rot=90)
    right_edge = [y for p in polys(g) for (x, y) in p.exterior.coords if abs(x - x1) < 1]
    pts = sorted(set([round(v) for v in right_edge] + [y for y in ys_ax if min(right_edge) <= y <= max(right_edge)]))
    for a, b in zip(pts, pts[1:]): sh.dim((x1, a), (x1, b), (x1 + c1, a), rot=90)
    return ax, ay

def opal_extra(sh):
    s = SL[sh.k]; g = s['g']
    if sh.k == 'P70':
        # atrium edges, notch, opening and stair well bound to axes
        sh.dim((2000, 13900), (2000, 16900), (2000, 13900), rot=90)
        sh.dim((2000, 25500), (2000, 27500), (2000, 25500), rot=90)
        sh.dim((16950, 39300), (17300, 39300), (16950, 40300))
        for (a, b, c, d) in [(36700, 2400, 39900, 5600), (41300, -250, 44300, 6300)]:
            axv = max([v for v in AXX.values() if v <= a]); ayv = max([v for v in AXY.values() if v <= max(b, 0)])
            if a - axv > 1: sh.dim((axv, d), (a, d), (axv, d + 700))
            sh.dim((a, d), (c, d), (a, d + 700))
            if b - ayv > 1: sh.dim((c, ayv), (c, b), (c + 700, ayv), rot=90)
            sh.dim((c, b), (c, d), (c + 700, b), rot=90)
    else:
        secmarks(sh)

def secmarks(sh):
    # 1-1 across the slab edge on axis А, 2-2 across an interior beam
    y0 = SL[sh.k]['g'].bounds[1]
    s1x = 8600
    s2 = (11300, 4500)
    add(t='clone', h=T['secmark'], to=sh.P(s1x, y0), dyn={'Расстояние1': 900, 'Расстояние2': 900}, att={'В1': '1', 'В2': '1', 'Г1': '1', 'Г2': '1'})
    add(t='clone', h=T['secmark'], to=sh.P(*s2), rot=90, dyn={'Расстояние1': 900, 'Расстояние2': 900}, att={'В1': '2', 'В2': '2', 'Г1': '2', 'Г2': '2'})

# ---------------- main reinforcement sheet ----------------
def bays(axes, lo, hi):
    out = []
    for a, b in zip(axes, axes[1:]):
        f = a + 300; n = int((b - 300 - f) // 200); out.append((f, f + 200 * n, n, a, b))
    return out

def main_sheet(sh):
    s = SL[sh.k]; g = s['g']; gin = g.buffer(-30, join_style=2)
    x0, y0, x1, y1 = g.bounds
    ax = sorted(set(AXX[n] for n in s['ax'])); ay = sorted(AXY[n] for n in s['ay'])
    ax = [v for v in ax if x0 + 100 < v < x1 - 100]; ay = [v for v in ay if y0 + 100 < v < y1 - 100]
    xb = bays([round(x0)] + ax[1:-1] + [round(x1)] if False else ax, x0, x1)
    # bars Y (vertical lines) - first and last of every axis bay, full slab height (clipped)
    def vbar(x):
        for ln in lines_of(LineString([(x, y0 - 10), (x, y1 + 10)]).intersection(gin)):
            (a, b), (c, d) = ln.coords[0], ln.coords[-1]; sh.line(a, b, c, d, layer='ф10_арм', lw=40)
    def hbar(y):
        for ln in lines_of(LineString([(x0 - 10, y), (x1 + 10, y)]).intersection(gin)):
            (a, b), (c, d) = ln.coords[0], ln.coords[-1]; sh.line(a, b, c, d, layer='ф10_арм', lw=40)
    cy = y0 - 1100
    for (f, l, n, a, b) in xb:
        vbar(f); vbar(l)
        sh.dim((f, y0), (l, y0), (f, cy), text='200х%d=<>' % n)
        sh.dim((a, y0), (f, y0), (a, cy - 0)); sh.dim((l, y0), (b, y0), (l, cy))
    # edge bars beyond the extreme axes
    if x0 < ax[0] - 100: vbar(x0 + 50)
    if x1 > ax[-1] + 100: vbar(x1 - 50)
    yb = bays(ay, y0, y1)
    cx = x0 - 1100
    for (f, l, n, a, b) in yb:
        hbar(f); hbar(l)
        sh.dim((x0, f), (x0, l), (cx, f), rot=90, text='200х%d=<>' % n)
        sh.dim((x0, a), (x0, f), (cx, a), rot=90); sh.dim((x0, l), (x0, b), (cx, l), rot=90)
    if y0 < ay[0] - 100: hbar(y0 + 50)
    if y1 > ay[-1] + 100: hbar(y1 - 50)
    # position 1 labels: one for X bars, one for Y bars (arrows to the bay bars)
    xm = (xb[0][0] + xb[0][1]) / 2; ym = (yb[0][0] + yb[0][1]) / 2
    sh.mark('1', (xb[0][0], ym), (xb[0][1], ym), False)
    sh.mark('1', (xm, yb[0][0]), (xm, yb[0][1]), True)
    secmarks(sh)
    # Ск1 at the slab edges: one symbol per axis bay on every free edge
    edges = []
    for ring in rings(g): edges += list(zip(list(ring.coords), list(ring.coords)[1:]))
    for (a, b) in edges:
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 1500: continue
        horiz = abs(b[1] - a[1]) < 1
        n = max(1, int(L // 7000))
        for j in range(n):
            t = (j + 0.5) / n; px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            nx, ny = (0, 1) if horiz else (1, 0)
            if not g.contains(Point(px + nx * 300, py + ny * 300)): nx, ny = -nx, -ny
            # U-bar symbol outside the edge, open toward the slab; label beyond it
            bx, by = px - nx * 80, py - ny * 80
            tx, ty = -ny, nx
            pts = [(bx + tx * 100, by + ty * 100), (bx + tx * 100 - nx * 313, by + ty * 100 - ny * 313),
                   (bx - tx * 100 - nx * 313, by - ty * 100 - ny * 313), (bx - tx * 100, by - ty * 100)]
            sh.pl(pts, layer='ф8_арм', lw=30)
            sh.text(px - nx * 700, py - ny * 700, 'Ск1')

# ---------------- dop sheets ----------------
POS = defaultdict(dict)
def pos_of(k, d, L):
    P = POS[k]
    if (d, L) not in P: P[(d, L)] = len(P) + 2
    return P[(d, L)]

CW, TH = 185, 250          # text char width / height at 1:100 (model mm)

def tbox(cx, cy, w, h): return box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)

def dop_sheet(sh, faces):
    # every annotation is placed at the free candidate: occupied = bars of all zones + texts placed so far
    s = SL[sh.k]; ax = [AXX[n] for n in s['ax']]; ay = [AXY[n] for n in s['ay']]; g = s['g']
    zs = [z for z in Z[sh.k] if z['f'] in faces]
    zs.sort(key=lambda z: (z['f'], -z['d'], z['pos'][0], z['L0']))
    occ = []
    for z in zs:
        a, b, L0, L1 = z['pos'][0], z['pos'][-1], z['L0'], z['L1']
        for q in sorted(set([a, b])):
            occ.append((LineString([(L0, q), (L1, q)]) if z['f'] in (0, 1) else LineString([(q, L0), (q, L1)])).buffer(60))
    def cost(geoms):
        c = 0
        for gm in geoms:
            for o in occ:
                if gm.intersects(o): c += gm.intersection(o).area + 1e5
            if not g.buffer(1500).contains(gm): c += 5e4
        return c
    def pick(cands):
        best = min(cands, key=lambda t: cost(t[0])); occ.extend(best[0]); return best[1]
    for z in zs:
        d = z['d']; L = z['L']; p = pos_of(sh.k, d, L); z['P'] = p; z['Lr'] = L
        lay = 'ф%d_арм' % d
        a, b, L0, L1 = z['pos'][0], z['pos'][-1], z['L0'], z['L1']
        n1 = len(z['pos']) - 1; st = '200х%d' % n1; Ls = str(int(round(L1 - L0)))
        X = z['f'] in (0, 1)
        if X:
            for y in sorted(set([a, b])): sh.line(L0, y, L1, y, layer=lay, lw=40)
        else:
            for x in sorted(set([a, b])): sh.line(x, L0, x, L1, layer=lay, lw=40)
        # length dim: below the first bar or above the last one
        c = []
        for side, off in (('lo', -350), ('hi', 350)):
            q = (a if side == 'lo' else b) + off
            bx = tbox((L0 + L1) / 2, q + 180, len(Ls) * CW, TH) if X else tbox(q - 180, (L0 + L1) / 2, TH, len(Ls) * CW)
            c.append(([bx, (LineString([(L0, q), (L1, q)]) if X else LineString([(q, L0), (q, L1)])).buffer(20)], q))
        q = pick(c)
        if X: sh.dim((L0, a if q < a else b), (L1, a if q < a else b), (L0, q))
        else: sh.dim((a if q < a else b, L0), (a if q < a else b, L1), (q, L0), rot=90)
        # spacing dim «200xN» at one end of the bars
        if b > a:
            c = []
            for e, off in ((L1, 350), (L0, -350)):
                q2 = e + off
                bx = tbox(q2 - 180, (a + b) / 2, TH, len(st) * CW) if X else tbox((a + b) / 2, q2 + 180, len(st) * CW, TH)
                c.append(([bx], (e, q2)))
            e, q2 = pick(c)
            if X: sh.dim((e, a), (e, b), (q2, a), rot=90, text=st)
            else: sh.dim((a, e), (b, e), (a, q2), text=st)
        # position mark (analog multileader) along the bars where it is free
        c = []
        for f in (0.35, 0.5, 0.2, 0.65, 0.8):
            m = L0 + (L1 - L0) * f
            if X: bx = tbox(m - 60, (a + b) / 2 if b > a else a + 400, TH + 100, len(str(p)) * CW + 100)
            else: bx = tbox((a + b) / 2 if b > a else a + 400, m + 300, len(str(p)) * CW + 100, TH + 100)
            c.append(([bx], m))
        m = pick(c)
        if X: sh.mark(str(p), (m, a), (m, b), True)
        else: sh.mark(str(p), (a, m), (b, m), False)
        # binding of the bar end to the nearest axis, only when free
        axs = ax if X else ay
        near = min(axs, key=lambda v: abs(v - L0))
        if 60 < abs(near - L0) < 4000 and g.boundary.distance(Point(L0, a) if X else Point(a, L0)) > 150:
            for q3 in ((a - 750, a), (b + 750, b)):
                txt = str(int(round(abs(near - L0))))
                bx = tbox((near + L0) / 2, q3[0] + 180, len(txt) * CW, TH) if X else tbox(q3[0] - 180, (near + L0) / 2, TH, len(txt) * CW)
                if cost([bx]) == 0:
                    occ.append(bx)
                    if X: sh.dim((near, q3[1]), (L0, q3[1]), (near, q3[0]))
                    else: sh.dim((q3[1], near), (q3[1], L0), (q3[0], near), rot=90)
                    break

# ---------------- spec ----------------
RHO = {8: 0.395, 10: 0.617, 12: 0.888, 14: 1.208, 16: 1.578, 18: 1.998}
LAP = {10: 610, 12: 730, 14: 850, 16: 980, 18: 1100}
def base_len(k):
    g = SL[k]['g']; gin = g.buffer(-30, join_style=2); x0, y0, x1, y1 = g.bounds; tot = 0
    for x in range(int(x0) + 100, int(x1), 200):
        for ln in lines_of(LineString([(x, y0 - 1), (x, y1 + 1)]).intersection(gin)): tot += ln.length + LAP[10] * max(0, math.ceil(ln.length / 11700) - 1)
    for y in range(int(y0) + 100, int(y1), 200):
        for ln in lines_of(LineString([(x0 - 1, y), (x1 + 1, y)]).intersection(gin)): tot += ln.length + LAP[10] * max(0, math.ceil(ln.length / 11700) - 1)
    return 2 * tot / 1000.0          # top + bottom, m

def spec(k):
    g = SL[k]['g']
    rows = []
    m1 = round(base_len(k), 1); rows.append(['1', 10, 'м.п.', m1, RHO[10]])
    agg = defaultdict(int); mp = defaultdict(float)
    gin = g.buffer(-30, join_style=2)
    for z in Z[k]:
        agg[(z['P'], z['d'], z['Lr'])] += z['n']
        if z['Lr'] > 11700:
            # long bars: real lengths clipped by the slab (atrium, openings) plus laps
            for p in z['pos']:
                ln = LineString([(z['L0'] - 1, p), (z['L1'] + 1, p)]) if z['f'] in (0, 1) else LineString([(p, z['L0'] - 1), (p, z['L1'] + 1)])
                for part in lines_of(ln.intersection(gin)):
                    mp[z['P']] += part.length + LAP[z['d']] * max(0, math.ceil(part.length / 11700) - 1)
    for (p, d, L), n in sorted(agg.items()):
        if L > 11700: rows.append([str(p), d, 'м.п.', round(mp[p] / 1000.0, 1), RHO[d]])
        else: rows.append([str(p), d, L, n, round(RHO[d] * L / 1000, 2)])
    per = sum(r.length for r in rings(g))
    nsk = int(math.ceil(per / 200)); nf = int(math.ceil(g.area / 1e6))
    conc = round(g.area / 1e6 * 0.2, 2)
    return rows, nsk, nf, conc

# ---------------- sections for Пм1 opalubka (analog Пм3 sections 1-1 / 2-2 rebuilt to the Block 4 beams) ----------------
AS1 = dict(cx=8080, yt=-19119)       # analog 1-1 (interior T) anchor, relative to its frame
AS2 = dict(cx=17116, yt=-22820)      # analog 2-2 (edge) anchor
ANF = (AN_R3[0], AN_R3Y)
def section(X, Y, num, b, h, edge, lvl=('+7.000', '+6.800'), lo=918, ro=819, ab=None):
    # X, Y: model point of the beam axis at the slab top; b, h in mm (rib depth below the slab, as in the analog)
    hw = 2 * b; D = 4 * h; yt = Y; ys = yt - 800; yb = ys - D; cx = X
    a = AS2 if edge else AS1
    dx, dy = cx - (ANF[0] + a['cx']), yt - (ANF[1] + a['yt'])
    if edge:
        L0 = cx - hw - 200; R = cx + hw + 820
        out = [(L0, yt), (L0, ys), (cx - hw, ys), (cx - hw, yb), (cx + hw, yb), (cx + hw, ys), (R, ys)]
        top = (L0, R)
    else:
        L0 = cx - hw - lo; R = cx + hw + ro
        out = [(L0, ys), (cx - hw, ys), (cx - hw, yb), (cx + hw, yb), (cx + hw, ys), (R, ys)]
        top = (L0, R)
    add(t='pl', pts=[list(p) for p in out], layer='0.30', lw=30)
    add(t='line', p=[top[0], yt, top[1], yt], layer='0.30', lw=30)
    loop = [(top[0], yt), (R, yt)] + list(reversed(out))
    add(t='hatch', pat='ANSI36', scale=160, layer='006 Штриховка', lw=9, loops=[[list(p) for p in loop]])
    add(t='line', p=[cx, yt + 1000, cx, yb - 1600], layer='0', ltype='осевая', ltscale=25, lw=9)
    add(t='clone', h='BCEE9DAA', to=[cx, yb - 2000])
    add(t='clone', h='BCEE9DA5', p1=[cx - hw, yb], p2=[cx, yb], dl=[cx - hw, yb - 1000], rotd=0, text='')
    add(t='clone', h='BCEE9DA6', p1=[cx, yb], p2=[cx + hw, yb], dl=[cx, yb - 1000], rotd=0, text='')
    if edge:
        add(t='clone', h='BCEE9E30', d=[R - (ANF[0] + 18937), ys - (ANF[1] - 23620), 0])
        add(t='clone', h='BCEE9E0A', d=[R - (ANF[0] + 18937), dy, 0], att={'ОТМЕТКА': lvl[0]})
        add(t='clone', h='BCEE9E1D', d=[R - (ANF[0] + 18937), dy, 0], att={'ОТМЕТКА': lvl[1]})
        add(t='clone', h='BCEE9E02', p1=[R + 97, yt], p2=[R + 97, ys], dl=[R + 1097, ys], rotd=90, text='')
        add(t='clone', h='BCEE9E03', p1=[cx + hw, yb], p2=[R + 97, ys], dl=[R + 1097, ys], rotd=90, text='')
        add(t='clone', h='BCEE9DFC', d=[dx, dy, 0], text='%%%%U%d - %d' % (num, num))
        add(t='clone', h='BCEE9E08', d=[dx, dy, 0])
        add(t='clone', h='BCEE9E09', d=[dx, dy, 0])
        add(t='mleader', h='BCEE9E43', d=[dx, dy, 0], arrow=[cx - hw * 0.4, ys - D * 0.5])
    else:
        add(t='clone', h='BCEE9DAD', d=[L0 - (ANF[0] + 6162), ys - (ANF[1] - 19920), 0])
        add(t='clone', h='BCEE9DE8', d=[R - (ANF[0] + 9899), ys - (ANF[1] - 19919), 0])
        add(t='clone', h='BCEE9DC2', d=[L0 - (ANF[0] + 6162), dy, 0], att={'ОТМЕТКА': lvl[0]})
        add(t='clone', h='BCEE9DD5', d=[L0 - (ANF[0] + 6162), dy, 0], att={'ОТМЕТКА': lvl[1]})
        add(t='clone', h='BCEE9DA7', p1=[L0, ys], p2=[L0, yt], dl=[L0 - 1000, ys], rotd=90, text='')
        add(t='clone', h='BCEE9DA8', p1=[L0, ys], p2=[cx - hw, yb], dl=[L0 - 1000, ys], rotd=90, text='')
        add(t='clone', h='BCEE9DA1', d=[dx, dy, 0], text='%%%%U%d - %d' % (num, num))
        if ab: add(t='mlx', h='BCEE9DC0', textloc=[L0 + 2600, yt + 3000], arrows=[[L0 + 1600, yt - 400]])
        else: add(t='clone', h='BCEE9DC0', d=[dx, dy, 0])
        add(t='clone', h='BCEE9DC1', d=[dx, dy, 0])
        add(t='mleader', h='BCEE9DFB', d=[dx, dy, 0], arrow=[cx + hw * 0.4, ys - D * 0.5])
    if ab:
        # АВ-1: straight bar at the top cover, 1200 into the slab past the beam face, 1300 into the stair landing
        e = cx + hw + 200; yb1 = yt - 160
        add(t='pl', pts=[[e - 4 * 1200, yb1], [e + 4 * 1300, yb1]], layer='ф14_арм', w=100)
        add(t='clone', h='BCEE9DA5', p1=[e - 4 * 1200, yt], p2=[e, yt], dl=[e - 4 * 1200, yt + 900], rotd=0, text='')
        add(t='clone', h='BCEE9DA5', p1=[e, yt], p2=[e + 4 * 1300, yt], dl=[e, yt + 900], rotd=0, text='')
        add(t='mlx', h='BCEC4EDB', textloc=[R + 1800, yt - 2200], arrows=[[e + 4 * 900, yb1]])
        add(t='mlx', h='BCEE9DC1', text='Площадка\\Pлестницы', textloc=[R + 1300, yt + 1500], arrows=[[R - 1200, yt - 400]])

SEC70 = [  # num, b, h, edge, column, row, plan mark (x, y, rot) - LIRA +7.000: X beams 400x700, Y beams 400x1000, secondary 250x600
    (1, 400, 700, False, 0, 0, (3300, 9000, 0)),
    (2, 400, 700, True, 1, 0, (8600, -250, 0)),
    (3, 400, 1000, False, 0, 1, (11300, 4500, 90)),
    (4, 400, 1000, True, 1, 1, (53300, 4500, 90)),
    (5, 250, 600, False, 0, 2, (14300, 3000, 0)),
]
SECX = (69000, 75000)                         # section columns (x from the sheet's left edge); plan is 54 m wide here
AB1 = dict(y0=36450, y1=38850, edge=16950)   # АВ-1 Ø14 @200 along X into the +7.000 landing 15530..16950 (stair Е-Ж / 25-26, LIRA)

def stair_ab(sh):
    # bars along X across the slab edge x = 16950: 1200 into the slab, 1300 into the landing (west)
    a, b, e = AB1['y0'], AB1['y1'], AB1['edge']
    n = int((b - a) // 200) + 1; b = a + 200 * (n - 1)
    for y in (a, b): sh.line(e - 1300, y, e + 1200, y, layer='ф14_арм', lw=40)
    sh.dim((e - 1300, a), (e - 1300, b), (e - 1650, a), rot=90, text='200х%d' % (n - 1))
    sh.dim((e - 1300, a), (e, a), (e - 1300, a - 350)); sh.dim((e, a), (e + 1200, a), (e, a - 350))
    add(t='mlx', h='BCEEA57B', text='АВ-1', textloc=sh.P(e - 700, (a + b) / 2), arrows=[sh.P(e - 500, a), sh.P(e - 500, b)])
    add(t='clone', h=T['secmark'], to=sh.P(e, (a + b) / 2), rot=90, dyn={'Расстояние1': 1700, 'Расстояние2': 1700}, att={'В1': '6', 'В2': '6', 'Г1': '6', 'Г2': '6'})
    X0, Y0 = SH[(sh.k, sh.i)]['X0'], SH[(sh.k, sh.i)]['Y0']
    section(X0 + 72000, Y0 - 9000, 6, 400, 1000, False, lo=5200, ro=5600, ab=True)
    SL[sh.k]['ab1'] = n

def sections70(sh):
    X0, Y0 = SH[('P70', 0)]['X0'], SH[('P70', 0)]['Y0']
    for num, b, h, edge, col, row, (mx, my, mr) in SEC70:
        cx = X0 + SECX[col]
        yt = Y0 - (7000 + 13000 * row + (6500 if col == 1 else 0))
        section(cx, yt, num, b, h, edge)
        n = str(num)
        add(t='clone', h=T['secmark'], to=sh.P(mx, my), rot=mr, dyn={'Расстояние1': 900, 'Расстояние2': 900}, att={'В1': n, 'В2': n, 'Г1': n, 'Г2': n})

if __name__ == '__main__':
    for k in ('P70', 'P45'):
        for i, (kind, faces) in enumerate(KINDS[k]):
            sh = Sheet(k, i)
            background(sh, kind)
            if kind == 'opal':
                opal_extra(sh)
                if k == 'P70': sections70(sh)
            elif kind == 'main': main_sheet(sh)
            else:
                dop_sheet(sh, faces)
                if k == 'P70' and faces == (2,): stair_ab(sh)
    json.dump(ops, open('ops_plan.json', 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump({k: [{kk: vv for kk, vv in z.items()} for z in Z[k]] for k in Z}, open('zones_final.json', 'w'), ensure_ascii=False)
    print(len(ops), 'ops; positions', {k: len(v) for k, v in POS.items()})
    for k in ('P70', 'P45'):
        rows, nsk, nf, conc = spec(k); print(k, rows, nsk, nf, conc)

