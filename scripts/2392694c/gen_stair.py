# Stair outlets Вп1/Вп2 + «Разрез 2-2» on the Пм-2 opalubka 6.9, from analog 5.2 Пм-2 opalubka (imported at x 4300000):
# per flight bars Ø16 @200 (50 from the flight edges), 700 into the slab, Вп2 980 out, Вп1 980+1280 out, alternating
# (analog: groups 2DE314.., notes 2DE313/2DE3B5, section 2DE366..). Our flights (LIRA): at y=18025 left 10525..11700 (up),
# right 11700..13125 (arriving from below).
import gx, math
import gen_dop as GD
import lev
C = lev.CUR
SW = 59400.0
K = C['k0']
X = lev.ox(K)
Y = C['oy']
U = 4300000.0
DX = 172179.0 + SW * (K - 1) - U          # analog sheet -> sheet 6.9 (same place on the sheet)
EDGE = 18025
FL = C.get('flights', [(10525, 11700), (11700, 13125)])


def P(a, b): return [X + a, Y + b, 0]


def bars(a, b):
    xs = [a + 50 + 200 * i for i in range(int((b - 50 - (a + 50)) // 200) + 1)]
    if b - 50 - xs[-1] > 1: xs.append(b - 50)
    return xs


def build():
    ops = []
    nb = []
    for gi, (a, b) in enumerate(FL):
        xs = bars(a, b); nb.append(len(xs))
        for i, x in enumerate(xs):
            top = EDGE + 980 + (1280 if i % 2 == 0 else 0)          # Вп1 (long) / Вп2 alternate, as the analog
            ops.append({'t': 'lineset', 'h': '2DE314', 's': P(x, EDGE - 700), 'e': P(x, top)})
        # note «Вп1;Вп2» across the bars (analog 2DE313: shelf + 4 arrows), at 800 above the slab edge
        tg = 'STN%d' % gi
        if gi == 0 and len(FL) > 1:          # analog 2DE313: shelf on the left, 4 arrows
            ops.append({'t': 'clone', 'h': '2DE313', 'tag': tg})
            yy = EDGE + 500
            pick = [xs[0], xs[1], xs[-2], xs[-1]]
            items = [[0, X + a - 900, Y + yy]] + [[i + 1, X + px, Y + yy] for i, px in enumerate(pick)]
        else:                # analog 2DE3B5: shelf on the right, 8 arrows
            ops.append({'t': 'clone', 'h': '2DE3B5', 'tag': tg})
            yy = EDGE + 300
            pick = (xs + xs)[:8]
            items = [[0, X + b + 1300, Y + yy]] + [[i + 1, X + px, Y + yy] for i, px in enumerate(pick)]
        ops.append({'t': 'spmove', 'h': tg, 'items': items})
        # chain under the group: 50 | 200хN | rest | 50 from the flight edges
        pts = [a, xs[0]] + ([xs[0] + 200 * (len(xs) - 2)] if len(xs) > 2 else []) + [xs[-1], b]
        pts = sorted(set(pts))
        for p, q in zip(pts, pts[1:]):
            txt = '200х%d' % ((q - p) // 200) if q - p >= 400 and (q - p) % 200 == 0 else ''
            yb = EDGE - 700
            yl = yb - 450 - 750 * gi
            op = {'t': 'dim', 'h': GD.T_DH, 'p1': P(p, yb), 'p2': P(q, yb), 'dl': P(p, yl), 'rot': 0, 'txt': txt}
            if q - p < 300 and (p == a or q == b): op['tx'] = P(p - 250 if p == a else q + 250, yl + 180)
            elif q - p < 300: op['tx'] = P((p + q) / 2, yl - 330)
            if txt: op['tx'] = P((p + q) / 2, yl + 180)
            ops.append(op)
    # length chain on the right of the right group: 700 | 980 | 1280
    xr = FL[-1][1] + 250 + 600
    for p, q in ((EDGE - 700, EDGE), (EDGE, EDGE + 980), (EDGE + 980, EDGE + 2260)):
        ops.append({'t': 'dim', 'h': GD.T_DV, 'p1': P(FL[-1][1] - 50, p), 'p2': P(FL[-1][1] - 50, q), 'dl': P(xr, p), 'rot': math.pi / 2, 'txt': ''})
    # section mark 2-2 along the left flight
    ops.append({'t': 'clone', 'h': '2DE43E', 'tag': 'STS'})
    ops.append({'t': 'spmove', 'h': 'STS', 'items': [[0, X + (FL[0][0] + FL[0][1]) / 2 - 300, Y + EDGE + 2300], [1, X + (FL[0][0] + FL[0][1]) / 2 - 300, Y + EDGE - 2300]]})
    # Разрез 2-2 (analog group), level of this slab
    SEC = ['2DE366', '2DE367', '2DE368', '2DE369', '2DE36A', '2DE36C', '2DE37B', '2DE388', '2DE395', '2DE396', '2DE397', '2DE3A4']
    for h in SEC: ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [DX, 0], 'tag': 'STX_' + h})
    if len(C['lvl']) == 6: ops.append({'t': 'levelval', 'h': 'STX_2DE396', 'old': '+3.050', 'value': C['lvl'].replace(',', '.')})
    ops.append({'t': 'save'})
    return ops, nb


if __name__ == '__main__':
    ops, nb = build()
    out = gx.run(ops, 'stair')
    print(nb, [l for l in out.splitlines() if 'ERR' in l or 'level' in l or 'done' in l][:8])
