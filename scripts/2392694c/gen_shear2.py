# Shear (поперечное) sheet 7.(k0+6) with collision-free labels — same content as gen_shear.py (zones from
# arm/<tag>_shear.json), placement against the real dumped geometry like gen_dop2.  env SLAB=pm1 python gen_shear2.py
import gx, json, os, sys, math
from shapely.geometry import box, LineString
import lev
import gen_dop2 as G2
C = lev.CUR
S = gx.S
SW = 59400.0
AXX, AXY = G2.AXX, G2.AXY


def base(k, Zn):
    dx = SW * (k - 2)
    X, Y = lev.ox(k), C['oy']
    def P(a, b): return [X + a, Y + b, 0]
    x0 = 231579 + dx
    ops = [{'t': 'eraseregion', 'win': [x0 - 1, 455930, x0 + SW + 1, 497950]}]
    for h in G2.FRAME: ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [dx, 0]})
    name = 'Поперечное армирование плиты перекрытия %s на отм %s' % (C['name'], C['mark'])
    ops.append({'t': 'clone', 'h': '2B47A5', 'base': [0, 0], 'to': [dx, 0], 'text': '{\\L\\C0;' + name + '}'})
    ops.append({'t': 'clone', 'h': '2B479D', 'base': [0, 0], 'to': [dx, 0], 'text': '{\\C0;' + name + '}'})
    ops.append({'t': 'clone', 'h': '2B479F', 'base': [0, 0], 'to': [dx, 0], 'text': '7.%d' % k})
    for tg, h in gx.tagmap().items():
        if tg.startswith(C['bgp']): ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [SW * (k - C['km']), 0]})
    for i, z in enumerate(Zn):
        a, b, c, d = z['x0'], z['y0'], z['x1'], z['y1']
        tg = 'SHR%d' % i
        ops.append({'t': 'clone', 'h': 'TPL_SZ', 'tag': tg})
        ops.append({'t': 'plset', 'h': tg, 'p': [P(a, b), P(c, b), P(c, d), P(a, d), P(a, b)]})
        ops.append({'t': 'hatch', 'pat': 'TRIANG', 'sc': 10, 'layer': 'диам%d' % z['d'], 'lw': 9, 'loops': [[P(a, b), P(c, b), P(c, d), P(a, d)]]})
    ops.append({'t': 'trepl', 'win': [x0 - 5, 455900, x0 + SW + 5, 498000], 'pairs': [['КЖ-7.1 ... 7.8', 'КЖ-7.%d ... 7.%d' % (C['k0'], C['k0'] + 7)]]})
    ops.append({'t': 'save'})
    return ops, x0


def place(k, Zn, posmap, B, order):
    X, Y = lev.ox(k), C['oy']
    ops = []; rep = []
    def dims(i, z):
        a, b, c, d = z['x0'], z['y0'], z['x1'], z['y1']
        for horiz in (True, False):
            lo, hi = (a, c) if horiz else (b, d)
            axes = AXX if horiz else AXY
            ax = min(axes, key=lambda v: min(abs(v - lo), abs(v - hi)))
            pts = sorted({lo, hi} | ({ax} if 150 <= min(abs(ax - lo), abs(ax - hi)) < 4000 else set()))
            segs_ = list(zip(pts, pts[1:])); texts = [str(int(round(q - p))) for p, q in segs_]
            best = None
            for dd in (450, 800, 1150, 1500, 1900, 2400):
                for side in (-1, 1):
                    bs = (b if side < 0 else d) if horiz else (a if side < 0 else c)
                    dl = bs + side * dd
                    r = G2.chain_try(B, X, Y, segs_, horiz, dl, {p: bs for p in pts}, texts)
                    if best is None or r[0] < best[0]: best = r
                    if r[0] == 0: break
                if best[0] == 0: break
            ops.extend(best[1]); B.add(best[2], best[3])
            if best[0]: rep.append(('D', i, best[0]))
    def note(i, z):
        a, b, c, d = z['x0'], z['y0'], z['x1'], z['y1']; cx, cy = (a + c) / 2, (b + d) / 2
        cands = []
        for ddx in (700, 1100, 1600, 2200, 3000):
            for yy in (cy, b - 350, d + 450, b - 900, d + 1000, cy + 800, cy - 800, b - 1500, d + 1600):
                cands.append(('TPL_SNR', c + ddx, yy)); cands.append(('TPL_SNL', a - ddx, yy))
        best = None
        for tpl, ox, oy in cands:
            if tpl == 'TPL_SNR': poly = box(X + ox - 20, Y + oy - 420, X + ox + 1920, Y + oy + 420); shelf = LineString([(X + ox, Y + oy), (X + ox + 1900, Y + oy)])
            else: poly = box(X + ox - 1920, Y + oy - 420, X + ox + 20, Y + oy + 420); shelf = LineString([(X + ox - 1900, Y + oy), (X + ox, Y + oy)])
            lead = LineString([(X + ox, Y + oy), (X + cx, Y + cy)])
            sc = B.text_bad(poly) + 2 * B.shelf_bad(shelf) + B.lines_bad([lead]) + 0.0001 * lead.length
            if best is None or sc < best[0]: best = (sc, tpl, ox, oy, poly, shelf, lead)
            if sc < 1: break
        sc, tpl, ox, oy, poly, shelf, lead = best
        B.add([poly], [shelf, lead])
        if sc >= 1: rep.append(('N', i, int(sc)))
        tn = 'SHN%d' % i
        ops.extend([{'t': 'clone', 'h': tpl, 'tag': tn},
                    {'t': 'spmove', 'h': tn, 'items': [[0, X + ox, Y + oy], [1, X + cx, Y + cy]]},
                    {'t': 'noteh', 'h': tn, 'l1': '%d(ф%d)' % (posmap[str(z['d'])], z['d']), 'l2': 'ш.200х200'}])
    for st in order:
        for i, z in enumerate(Zn): (dims if st == 'D' else note)(i, z)
    ops.append({'t': 'save'})
    return ops, rep


if __name__ == '__main__':
    J = json.load(open(os.path.join(S, 'arm', C['tag'] + '_shear.json')))
    Zn, posmap = J['zones'], J['pos']
    k = C['k0'] + 6
    ops, x0 = base(k, Zn)
    out = gx.run(ops, 'shA'); print([l for l in out.splitlines() if 'ERR' in l][:5])
    G2.dump(x0)
    ob = G2.load(x0, '7.%d' % k)
    res = []
    for order in ('DN', 'ND'):
        B = G2.Board(x0, *ob)
        o_, r_ = place(k, Zn, posmap, B, order)
        res.append((sum(v[2] for v in r_), order, o_, r_)); print(order, r_)
        if not r_: break
    res.sort(key=lambda q: q[0]); _, order, ops, rep = res[0]
    out = gx.run(ops, 'shB')
    print('7.%d' % k, len(Zn), 'unresolved', rep, [l for l in out.splitlines() if 'ERR' in l][:8])
