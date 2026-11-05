# Sheet 6.7 «Поперечное армирование Пм-1 -0.100» = analog 5.1/5.7: zones of vertical bars @200x200 where LIRA ASW1 > 0
# (cm²/m² -> 25 bars per m²), rectangle (analog polyline) + TRIANG hatch on layer диам<Ø> + note «N(фØ) ш.200х200»
# + width/height dims bound to the nearest axes. python gen_shear.py
import gx, json, os, sys, math, csv, pickle
import gen62 as G
import gen_dop as GD
import slab_design as SD
import lev
C = lev.CUR
S = gx.S
SW = 59400.0
BARA = [(8, .503), (10, .785), (12, 1.131), (14, 1.539), (16, 2.011), (18, 2.545), (20, 3.142)]


def cells_asw(Z):
    els, nodes = pickle.load(open(os.path.join(S, 'lira6', 'm.pkl'), 'rb'))
    W = {}
    for r in csv.reader(open(os.path.join(S, 'arm', 'as_pl6.csv'), encoding='utf-8', errors='replace'), delimiter=';'):
        if len(r) < 17 or not r[4].strip().isdigit(): continue
        try: v = float(r[15])
        except ValueError: continue
        e = int(r[4]); W[e] = max(W.get(e, 0), v)
    out = []
    for i, r in enumerate(els):
        if int(r[0]) not in (41, 42, 44): continue
        ns = [nodes[int(k) - 1] for k in r[2:]]; zs = [n[2] for n in ns]
        Zs = Z if isinstance(Z, (list, tuple)) else [Z]
        if max(zs) - min(zs) > 1e-3 or not any(abs(zs[0] - z) < 1e-3 for z in Zs): continue
        w = W.get(i + 1, 0)
        if w > 0:
            xs = [n[0] * 1000 for n in ns]; ys = [SD.M.fy(n[1]) for n in ns]
            out.append([min(xs), min(ys), max(xs), max(ys), w])
    return out


def zones(Z, rect, gap=800):
    C = cells_asw(Z)
    Zs = [[c[0], c[1], c[2], c[3], c[4]] for c in C]
    changed = True
    while changed:
        changed = False
        for i, a in enumerate(Zs):
            for b in Zs[i + 1:]:
                if a[0] - gap <= b[2] and b[0] - gap <= a[2] and a[1] - gap <= b[3] and b[1] - gap <= a[3]:
                    a[:] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]), max(a[4], b[4])]
                    Zs.remove(b); changed = True; break
            if changed: break
    out = []
    x0, y0, x1, y1 = rect
    for a, b, c, d, w in Zs:
        # grid @200 with 50 cover: snap the rectangle to whole steps, at least 600
        a, b = max(a, x0 + 50), max(b, y0 + 50); c, d = min(c, x1 - 50), min(d, y1 - 50)
        wdt = max(600, math.ceil((c - a) / 200) * 200); hgt = max(600, math.ceil((d - b) / 200) * 200)
        cx, cy = (a + c) / 2, (b + d) / 2
        a, c = cx - wdt / 2, cx + wdt / 2; b, d = cy - hgt / 2, cy + hgt / 2
        if a < x0 + 50: a, c = x0 + 50, x0 + 50 + wdt
        if c > x1 - 50: a, c = x1 - 50 - wdt, x1 - 50
        if b < y0 + 50: b, d = y0 + 50, y0 + 50 + hgt
        if d > y1 - 50: b, d = y1 - 50 - hgt, y1 - 50
        a, b = math.floor(a / 25) * 25, math.floor(b / 25) * 25; c, d = a + wdt, b + hgt
        if a < x0 + 50: a, c = x0 + 75, x0 + 75 + wdt
        if b < y0 + 50: b, d = y0 + 75, y0 + 75 + hgt
        if c > x1 - 50: a, c = x1 - 75 - wdt, x1 - 75
        if d > y1 - 50: b, d = y1 - 75 - hgt, y1 - 75
        dia = next(dd for dd, ar in BARA if ar * 25 >= w - 1e-6) if w <= 3.142 * 25 else 20
        out.append(dict(x0=round(a), y0=round(b), x1=round(c), y1=round(d), asw=round(w, 1), d=dia,
                        n=(round((c - a) / 200) + 1) * (round((d - b) / 200) + 1)))
    return out


def build(k, Zn, posmap):
    dx = SW * (k - 2)
    X, Y = lev.ox(k), C['oy']
    def P(a, b): return [X + a, Y + b, 0]
    x0 = 231579 + dx
    ops = [{'t': 'eraseregion', 'win': [x0 - 1, 455930, x0 + SW + 1, 497950]}]
    for h in GD.FRAME: ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [dx, 0]})
    name = 'Поперечное армирование плиты перекрытия %s на отм %s' % (C['name'], C['mark'])
    ops.append({'t': 'clone', 'h': '2B47A5', 'base': [0, 0], 'to': [dx, 0], 'text': '{\\L\\C0;' + name + '}'})
    ops.append({'t': 'clone', 'h': '2B479D', 'base': [0, 0], 'to': [dx, 0], 'text': '{\\C0;' + name + '}'})
    ops.append({'t': 'clone', 'h': '2B479F', 'base': [0, 0], 'to': [dx, 0], 'text': '6.%d' % k})
    for tg, h in gx.tagmap().items():
        if tg.startswith(C['bgp']): ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [SW * (k - C['km']), 0]})
    occ = []
    def hit(r): return any(not (r[2] < o[0] or r[0] > o[2] or r[3] < o[1] or r[1] > o[3]) for o in occ)
    for z in Zn: occ.append((z['x0'], z['y0'], z['x1'], z['y1']))
    for i, z in enumerate(Zn):
        a, b, c, d = z['x0'], z['y0'], z['x1'], z['y1']
        tg = 'SHR%d' % i
        ops.append({'t': 'clone', 'h': '2BD598', 'tag': tg})
        ops.append({'t': 'plset', 'h': tg, 'p': [P(a, b), P(c, b), P(c, d), P(a, d), P(a, b)]})
        ops.append({'t': 'hatch', 'pat': 'TRIANG', 'sc': 10, 'layer': 'диам%d' % z['d'], 'lw': 9,
                    'loops': [[P(a, b), P(c, b), P(c, d), P(a, d)]]})
        # dims: width under/over, height left/right, each bound to the nearest axis
        for horiz in (True, False):
            lo, hi = (a, c) if horiz else (b, d)
            axes = GD.AXX if horiz else GD.AXY
            ax = min(axes, key=lambda v: min(abs(v - lo), abs(v - hi)))
            pts = sorted({lo, hi} | ({ax} if min(abs(ax - lo), abs(ax - hi)) < 4000 and min(abs(ax - lo), abs(ax - hi)) >= 150 else set()))
            for side in ((-1, 1) if horiz else (-1, 1)):
                base = (b if side < 0 else d) if horiz else (a if side < 0 else c)
                dl = base + side * 450
                rects = []
                for p, q in zip(pts, pts[1:]):
                    t = str(int(round(q - p))); m = (p + q) / 2; w = 175 * len(t) + 60
                    tc = dl + 180
                    rects.append((m - w / 2, tc - 150, m + w / 2, tc + 150) if horiz else (tc - 150, m - w / 2, tc + 150, m + w / 2))
                if not any(hit(r) for r in rects) or side == 1: break
            occ += rects
            segs = list(zip(pts, pts[1:]))
            for j, (p, q) in enumerate(segs):
                op = {'t': 'dim', 'h': GD.T_DH if horiz else GD.T_DV, 'rot': 0 if horiz else math.pi / 2, 'txt': ''}
                if horiz: op.update(p1=P(p, base), p2=P(q, base), dl=P(p, dl))
                else: op.update(p1=P(base, p), p2=P(base, q), dl=P(dl, p))
                if q - p < 450 and len(segs) > 1:          # short piece: text slid out beyond the chain end
                    m = p - 300 if j == 0 else q + 300
                    op['tx'] = P(m, dl + 180) if horiz else P(dl - 60, m)
                ops.append(op)
        # note: arrow into the zone, shelf right (template 2BD602) or left (2BD67B), free place
        cx, cy = (a + c) / 2, (b + d) / 2
        cand = [('2BD602', c + 700, b - 350, (c + 650, b - 750, c + 3500, b + 50)), ('2BD67B', a - 700, b - 350, (a - 3500, b - 750, a - 650, b + 50)),
                ('2BD602', c + 700, d + 450, (c + 650, d + 50, c + 3500, d + 850)), ('2BD67B', a - 700, d + 450, (a - 3500, d + 50, a - 650, d + 850))]
        pick = next((q for q in cand if not hit(q[3])), cand[0])
        occ.append(pick[3])
        tn = 'SHN%d' % i
        ops.append({'t': 'clone', 'h': pick[0], 'tag': tn})
        ops.append({'t': 'spmove', 'h': tn, 'items': [[0, X + pick[1], Y + pick[2]], [1, X + cx, Y + cy]]})
        ops.append({'t': 'noteh', 'h': tn, 'l1': '%d(ф%d)' % (posmap[z['d']], z['d']), 'l2': 'ш.200х200'})
    ops.append({'t': 'trepl', 'win': [x0 - 5, 455900, x0 + SW + 5, 498000], 'pairs': [['КЖ-6.1 ... 6.8', 'КЖ-6.%d ... 6.%d' % (lev.CUR['k0'], lev.CUR['k0'] + 7)]]})
    ops.append({'t': 'save'})
    return ops


if __name__ == '__main__':
    Zn = zones(C['z'], C['rect'])
    pos = json.load(open(os.path.join(S, 'arm', C['tag'] + '_pos.json')))
    nxt = max(pos.values()) + 1
    posmap = {}
    for dd in sorted({z['d'] for z in Zn}): posmap[dd] = nxt; nxt += 1
    json.dump(dict(zones=Zn, pos={str(k): v for k, v in posmap.items()}), open(os.path.join(S, 'arm', C['tag'] + '_shear.json'), 'w'), indent=1)
    for z in Zn: print(z)
    out = gx.run(build(C['k0'] + 6, Zn, posmap), 'shear')
    print(len(Zn), posmap, [l for l in out.splitlines() if 'ERR' in l or 'done' in l][:10])
