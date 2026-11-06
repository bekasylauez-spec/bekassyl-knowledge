# Схемы расположения ригелей (plans 1:200 on A4x3 sheets of the kit, 1 m = 250 units): columns from the scheme,
# rigel outlines between supports (hidden line), marks Рм-N along the rigel, axes + chains of the kit objects.
import json, math, os, sys, pickle, gx, prep, stamp2
sys.path.insert(0, prep.LIRA)
import design as DS
K = 0.25
SY = prep.SY
SHEETS = [('6.1', [-0.05, 4.0]), ('6.2', [4.8, 6.95]), ('6.3', [10.5])]
SX = {'6.1': prep.SX0 - 4 * 31500.0, '6.2': prep.SX0 - 3 * 31500.0, '6.3': prep.SX0 - 2 * 31500.0}
X9, YA = 53850.0, -1350.0
PW = 32 * 250 + 400               # plan width incl. columns
marks = json.load(open(os.path.join(prep.LIRA, 'marks.json'), encoding='utf-8'))
rr, _g = pickle.load(open(os.path.join(prep.LIRA, 'groups.pkl'), 'rb'))
groups = pickle.load(open(os.path.join(prep.LIRA, 'groups_u.pkl'), 'rb'))
# run -> mark (unified groups are in marks order); runs matched by end points
RM = {}
for m, (sg, rs) in zip(marks, groups):
    for r, rev in rs: RM[(r['z'], tuple(r['A']), tuple(r['B']))] = m['mark']


def plan(z, ox, oy, P, title):
    """ox, oy: sheet coordinates of axis 9 / axis А"""
    ops = []; n = [0]
    T = lambda x, y: [ox + (x - X9) * K, oy + (y - YA) * K]
    def tag(s): n[0] += 1; return '%s_%s%d' % (P, s, n[0])
    # columns
    for c in DS.cols_at(z):
        x0, y0, x1, y1 = c
        p = [T(x0, y0), T(x1, y0), T(x1, y1), T(x0, y1)]
        ops.append(dict(t='pl', p=p, closed=True, layer='0', lw=30, tag=tag('C')))
        ops.append(dict(t='hatch', pat='ANSI36', sc=5, layer='0', lw=5, loops=[p], tag=tag('H')))
    # rigels: outline per span between supports, hidden line
    runs = [r for r in rr if abs(r['z'] - z) < 0.01]
    for r in runs:
        A, B, L = r['A'], r['B'], r['L']
        ux, uy = (B[0] - A[0]) / L, (B[1] - A[1]) / L; nx, ny = -uy, ux
        hb = r['b'] / 2.0
        faces = [r['E0']] + [c for a, b, _ in r['sups'] for c in (a, b)] + [r['E1']]
        spans = [(faces[i], faces[i + 1]) for i in range(0, len(faces), 2) if faces[i + 1] - faces[i] > 1]
        for a, b in spans:
            q = lambda t, s: T(A[0] + ux * t + nx * s, A[1] + uy * t + ny * s)
            ops.append(dict(t='pl', p=[q(a, -hb), q(b, -hb)], layer='0', lw=30, ltype='ACAD_ISO02W100', tag=tag('B')))
            ops.append(dict(t='pl', p=[q(a, hb), q(b, hb)], layer='0', lw=30, ltype='ACAD_ISO02W100', tag=tag('B')))
        # mark on the longest span, beside the rigel (above / left)
        a, b = max(spans, key=lambda s: s[1] - s[0])
        tm = (a + b) / 2.0
        ang = math.atan2(uy, ux)
        if ang > math.pi / 2 + 0.01 or ang < -math.pi / 2 + 0.01: ang += math.pi       # readable
        side = hb + 330
        px, py = A[0] + ux * tm + nx * side, A[1] + uy * tm + ny * side
        ops.append(dict(t='mtext', at=T(px, py), h=125, att=5, rot=ang, s=RM[(r['z'], tuple(r['A']), tuple(r['B']))], layer='TEXT 2.5', tag=tag('M')))
    # axes (kit SPDS axis), chains
    xs = sorted(DS.AXX.items()); ys = sorted(DS.AXY.items())
    ybot = oy - 1000; xleft = ox - 1000
    ytop = oy + 29000 * K + 400; xright = ox + 31200 * K + 400
    for c, v in xs:
        h = tag('AX'); ops.append(dict(t='clone', h='A5:401290', tag=h)); ops.append(dict(t='axis', h=h, s=[T(c, 0)[0], ytop], e=[T(c, 0)[0], ybot], val=v))
    for c, v in ys:
        if v in ('В', 'Г', 'Е', 'И'): continue      # architectural axes without columns of block 2
        h = tag('AY'); ops.append(dict(t='clone', h='A5:401290', tag=h)); ops.append(dict(t='axis', h=h, s=[xright, T(0, c)[1]], e=[xleft, T(0, c)[1]], val=v))
    yd = ybot + 450
    for (c0, _), (c1, _) in zip(xs, xs[1:]):
        h = tag('DX'); ops.append(dict(t='clone', h='A5:401292', tag=h))
        ops.append(dict(t='dimpts', h=h, p1=[T(c0, 0)[0], yd, 0], p2=[T(c1, 0)[0], yd, 0], dl=[T(c1, 0)[0], yd, 0]))
        ops.append(dict(t='dimset', h=[h], lfac=1.0 / K)); ops.append(dict(t='dimtext', h=h, s=''))
    yk = [(c, v) for c, v in ys if v not in ('В', 'Г', 'Е', 'И')]
    xd = xleft + 450
    for (c0, _), (c1, _) in zip(yk, yk[1:]):
        h = tag('DY'); ops.append(dict(t='clone', h='A5:401292', tag=h))
        ops.append(dict(t='dimpts', h=h, p1=[xd, T(0, c0)[1], 0], p2=[xd, T(0, c1)[1], 0], dl=[xd, T(0, c1)[1], 0]))
        ops.append(dict(t='dimset', h=[h], lfac=1.0 / K)); ops.append(dict(t='dimtext', h=h, s=''))
    # title
    h = tag('T'); ops.append(dict(t='clone', h='A5:4038B1', tag=h))
    ops.append(dict(t='moveto', h=h, idx=0, to=[ox + 31200 * K / 2, ytop + 700]))
    ops.append(dict(t='settext', h=h, s=title))
    return ops


def run(no):
    sx = SX[no]; P = 'S' + no.replace('.', '')
    kx, ky = prep.KY, None
    ops = [dict(t='eraseregion', win=[sx - 50, SY - 50, sx + 31550, SY + 14900]), dict(t='ltload', names=['ACAD_ISO02W100'])]
    # frame of the kit (format + stamp texts) -> this sheet
    dx, dy = sx - 298179.0, SY - prep.KY
    for r in ['A5:401330', 'A5:404440', 'A5:404442', 'A5:40443F']:
        ops.append(dict(t='clone', h=r, base=[0, 0], to=[dx, dy], tag=P + ':' + r[3:]))
    lv = [z for n_, zz in SHEETS if n_ == no for z in zz]
    for i, z in enumerate(lv):
        ox = sx + 2700 + i * 15300
        ops += plan(z, ox, SY + 5200, P + 'L%d' % i, 'Схема расположения ригелей на отм. %s' % DS.LEVEL[z])
    ops.append(dict(t='settext', h=P + ':404442', s='Схемы расположения ригелей'))
    ops.append(dict(t='settext', h=P + ':404440', s=no))
    out = gx.run(ops, 'sch' + P)
    st = stamp2.stamp(dict(P=P, SX=sx, SY=SY))
    return out, st


if __name__ == '__main__':
    for no in sys.argv[1:] or ['6.1', '6.2', '6.3']:
        o, st = run(no)
        print(no, [l for l in (o + st).splitlines() if 'ERR' in l or 'done' in l][:8])
