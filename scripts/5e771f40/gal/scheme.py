# Схемы расположения ригелей (plans 1:200 on A4x3 sheets of the kit, 1 m = 250 units): columns from the scheme,
# rigel outlines between supports (hidden line), marks Рм-N along the rigel, axes + chains of the kit objects.
import json, math, os, sys, pickle, gx, prep, stamp2
sys.path.insert(0, prep.LIRA)
import design as DS
K = 0.25
SY = prep.SY
# (level, window in LIRA mm or None = whole plan, sheet-relative origin of axis 14 / axis А)
SHEETS = [('6.1', [(-0.05, None, (3200, 2300))]),
          ('6.2', [(4.45, None, (3200, 2300)), (1.65, (128000, -2000, 136000, 9600), (19300, 9400)),
                   (3.45, (128000, -2000, 136000, 9600), (25300, 9400)), (5.15, (128000, -2000, 136000, 9600), (19300, 4900))]),
          ('6.3', [(6.95, None, (3200, 2300)), (9.9, (110000, 9000, 118500, 27000), (19300, 7300)),
                   (12.7, (110000, 9000, 118500, 27000), (24300, 7300))])]
SX = {'6.1': prep.SX0 - 4 * 31500.0, '6.2': prep.SX0 - 3 * 31500.0, '6.3': prep.SX0 - 2 * 31500.0}
X9, YA = 86500.0, -1350.0
XMAX, YMAX = 135100.0, 38150.0
marks = json.load(open(os.path.join(prep.LIRA, 'marks.json'), encoding='utf-8'))
rr, _g = pickle.load(open(os.path.join(prep.LIRA, 'groups.pkl'), 'rb'))
groups = pickle.load(open(os.path.join(prep.LIRA, 'groups_u.pkl'), 'rb'))
# run -> mark (unified groups are in marks order); runs matched by end points
RM = {}
for m, (sg, rs) in zip(marks, groups):
    for r, rev in rs: RM[(r['z'], tuple(r['A']), tuple(r['B']))] = m['mark']


def plan(z, ox, oy, P, title, win=None):
    """ox, oy: sheet coordinates of axis 9 / axis А"""
    ops = []; n = [0]
    wx0, wy0, wx1, wy1 = win if win else (X9 - 2000, YA - 2000, XMAX + 2000, YMAX + 2000)
    bx0 = max(wx0, X9) if win is None else wx0; by0 = YA if win is None else wy0
    T = lambda x, y: [ox + (x - bx0) * K, oy + (y - by0) * K]
    inw = lambda x, y: wx0 <= x <= wx1 and wy0 <= y <= wy1
    COLS = [c for c in DS.cols_at(z) if inw((c[0] + c[2]) / 2, (c[1] + c[3]) / 2)]
    def tag(s): n[0] += 1; return '%s_%s%d' % (P, s, n[0])
    # columns
    for c in COLS:
        x0, y0, x1, y1 = c
        p = [T(x0, y0), T(x1, y0), T(x1, y1), T(x0, y1)]
        ops.append(dict(t='pl', p=p, closed=True, layer='0', lw=30, tag=tag('C')))
        ops.append(dict(t='hatch', pat='ANSI36', sc=5, layer='0', lw=5, loops=[p], tag=tag('H')))
    # rigels: outline per span between supports, hidden line
    from shapely.geometry import LineString, Polygon, box
    from shapely import affinity
    runs = [r for r in rr if abs(r['z'] - z) < 0.01 and inw(*r['A']) and inw(*r['B'])]
    obst = [box(*c) for c in COLS]
    XS = [(c, v) for c, v in sorted(DS.AXX.items()) if wx0 <= c <= wx1]
    YS = [(c, v) for c, v in sorted(DS.AXY.items()) if wy0 <= c <= wy1]
    if win:     # fragment: axes of the columns inside
        XS = [(c, v) for c, v in XS if any(abs((q[0] + q[2]) / 2 - c) < 500 for q in COLS)] or XS
        YS = [(c, v) for c, v in YS if any(abs((q[1] + q[3]) / 2 - c) < 700 for q in COLS)] or YS
    for c, v in XS: obst.append(LineString([(c, wy0 - 3000), (c, wy1 + 3000)]))
    for c, v in YS: obst.append(LineString([(wx0 - 3000, c), (wx1 + 3000, c)]))
    geo = []
    for r in runs:
        A, B, L = r['A'], r['B'], r['L']
        ux, uy = (B[0] - A[0]) / L, (B[1] - A[1]) / L; nx, ny = -uy, ux
        hb = r['b'] / 2.0
        faces = [r['E0']] + [c for a, b, _ in r['sups'] for c in (a, b)] + [r['E1']]
        spans = [(faces[i], faces[i + 1]) for i in range(0, len(faces), 2) if faces[i + 1] - faces[i] > 1]
        for a, b in spans:
            P_ = lambda t, s_: (A[0] + ux * t + nx * s_, A[1] + uy * t + ny * s_)
            q = lambda t, s_: T(*P_(t, s_))
            for sg in (-hb, hb):
                ops.append(dict(t='pl', p=[q(a, sg), q(b, sg)], layer='0', lw=30, ltype='ACAD_ISO02W100', ltscale=25, tag=tag('B')))
                obst.append(LineString([P_(a, sg), P_(b, sg)]))
        geo.append((r, A, ux, uy, nx, ny, hb, spans))
    placed = []
    for r, A, ux, uy, nx, ny, hb, spans in geo:
        txt = RM[(r['z'], tuple(r['A']), tuple(r['B']))]
        ang = math.atan2(uy, ux)
        rot = ang + math.pi if (ang > math.pi / 2 + 0.01 or ang < -math.pi / 2 + 0.01) else ang
        tw, th = 0.62 * 500 * len(txt), 500.0          # text box, real mm (2.5 mm at 1:200)
        cands = []
        E0, E1 = r['E0'], r['E1']
        tl = [a + (b - a) * f for a, b in sorted(spans, key=lambda s_: -(s_[1] - s_[0])) for f in (0.5, 0.3, 0.7, 0.2, 0.8)]
        tl += [E0 + (E1 - E0) * k / 10.0 for k in range(1, 10)]
        for t in tl:
                inspan = any(a + 100 <= t - tw / 2 and t + tw / 2 <= b - 100 for a, b in spans)
                f = 0.0 if inspan else 1.0
                for sd, lvl in ((1, 1.0), (-1, 1.0), (1, 2.1), (-1, 2.1), (1, 3.4), (-1, 3.4), (1, 4.8), (-1, 4.8), (1, 6.2), (-1, 6.2)):
                    off = sd * (hb + 120 + th / 2 * lvl)
                    cx, cy = A[0] + ux * t + nx * off, A[1] + uy * t + ny * off
                    bx = affinity.rotate(box(cx - tw / 2, cy - th / 2, cx + tw / 2, cy + th / 2), ang, origin=(cx, cy), use_radians=True)
                    bad = sum(1 for o in obst + placed if bx.buffer(40).intersects(o))
                    cands.append((bad, f + (lvl > 1) * 0.5 + (lvl > 2.5) * 2, (cx, cy), bx, (A[0] + ux * t + nx * sd * hb, A[1] + uy * t + ny * sd * hb) if lvl > 2.5 else None))
        if not cands:
            a, b = max(spans, key=lambda s_: s_[1] - s_[0]); t = (a + b) / 2; off = hb + 120 + th / 2
            cx, cy = A[0] + ux * t + nx * off, A[1] + uy * t + ny * off
            cands = [(99, 0, (cx, cy), box(cx - tw / 2, cy - th / 2, cx + tw / 2, cy + th / 2), None)]
        bad, _, (cx, cy), bx, lead = min(cands, key=lambda c_: (c_[0], c_[1]))
        placed.append(bx)
        if lead:      # far mark: thin leader from the rigel edge to the text box
            ex, ey = bx.exterior.interpolate(bx.exterior.project(__import__('shapely.geometry', fromlist=['Point']).Point(*lead))).coords[0]
            ops.append(dict(t='pl', p=[T(*lead), T(ex, ey)], layer='0', lw=5, tag=tag('LD')))
        ops.append(dict(t='mtext', at=T(cx, cy), h=125, att=5, rot=rot, s=txt, layer='TEXT 2.5', tag=tag('M')))
    # axes (kit SPDS axis), chains
    xs = XS; ys = YS
    gx0 = min(T(c, 0)[0] for c, _ in xs); gx1 = max(T(c, 0)[0] for c, _ in xs)
    gy0 = min(T(0, c)[1] for c, _ in ys); gy1 = max(T(0, c)[1] for c, _ in ys)
    cb = [T(q[0], q[1]) + T(q[2], q[3]) for q in COLS]
    if cb:
        gx0 = min(gx0, min(q[0] for q in cb)); gx1 = max(gx1, max(q[2] for q in cb))
        gy0 = min(gy0, min(q[1] for q in cb)); gy1 = max(gy1, max(q[3] for q in cb))
    ybot = gy0 - 1000; xleft = gx0 - 1000
    ytop = gy1 + 400; xright = gx1 + 400
    for c, v in xs:
        h = tag('AX'); ops.append(dict(t='clone', h='A5:401290', tag=h)); ops.append(dict(t='axis', h=h, s=[T(c, 0)[0], ytop], e=[T(c, 0)[0], ybot], val=v))
    for c, v in ys:
        h = tag('AY'); ops.append(dict(t='clone', h='A5:401290', tag=h)); ops.append(dict(t='axis', h=h, s=[xright, T(0, c)[1]], e=[xleft, T(0, c)[1]], val=v))
    yd = ybot + 450
    for (c0, _), (c1, _) in zip(xs, xs[1:]):
        h = tag('DX'); ops.append(dict(t='clone', h='A5:401292', tag=h))
        ops.append(dict(t='dimpts', h=h, p1=[T(c0, 0)[0], yd, 0], p2=[T(c1, 0)[0], yd, 0], dl=[T(c1, 0)[0], yd, 0]))
        ops.append(dict(t='dimset', h=[h], lfac=1.0 / K)); ops.append(dict(t='dimtext', h=h, s=''))
    yk = list(ys)
    xd = xleft + 450
    for (c0, _), (c1, _) in zip(yk, yk[1:]):
        h = tag('DY')
        ops.append(dict(t='dim', h='A5:401292', p1=[xd, T(0, c0)[1], 0], p2=[xd, T(0, c1)[1], 0], dl=[xd, T(0, c1)[1], 0], rot=math.pi / 2, lfac=1.0 / K, tag=h))
        ops.append(dict(t='dimtext', h=h, s=''))
    # title
    h = tag('T'); ops.append(dict(t='clone', h='A5:4038B1', tag=h))
    ops.append(dict(t='moveto', h=h, idx=0, to=[(xleft + xright) / 2.0, ytop + 700]))
    ops.append(dict(t='settext', h=h, s=title, w=9000 if not win else 4200))
    return ops


def run(no):
    sx = SX[no]; P = 'S' + no.replace('.', '')
    kx, ky = prep.KY, None
    ops = [dict(t='eraseregion', win=[sx - 50, SY - 50, sx + 31550, SY + 14900]), dict(t='ltload', names=['ACAD_ISO02W100'])]
    # frame of the kit (format + stamp texts) -> this sheet
    dx, dy = sx - 298179.0, SY - prep.KY
    for r in ['A5:401330', 'A5:404440', 'A5:404442', 'A5:40443F']:
        ops.append(dict(t='clone', h=r, base=[0, 0], to=[dx, dy], tag=P + ':' + r[3:]))
    lv = [q for n_, zz in SHEETS if n_ == no for q in zz]
    for i, (z, win, (rx, ry)) in enumerate(lv):
        ops += plan(z, sx + rx, SY + ry, P + 'L%d' % i, 'Схема расположения ригелей на отм. %s' % DS.LEVEL[z], win)
    ops.append(dict(t='settext', h=P + ':404442', s='Схемы расположения ригелей'))
    ops.append(dict(t='settext', h=P + ':404440', s=no))
    out = gx.run(ops, 'sch' + P)
    st = stamp2.stamp(dict(P=P, SX=sx, SY=SY))
    return out, st


if __name__ == '__main__':
    for no in sys.argv[1:] or ['6.1', '6.2', '6.3']:
        o, st = run(no)
        print(no, [l for l in (o + st).splitlines() if 'ERR' in l or 'done' in l][:8])
