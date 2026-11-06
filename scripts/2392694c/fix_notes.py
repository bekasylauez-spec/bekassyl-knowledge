# Re-place flagged SPDS position notes (shelf left of the origin) of sheet 7.k: origin along the leader line, or the
# whole note shifted along the bars (arrows must stay on a bar LINE). python fix_notes.py <k> [passes]
import sys, os, json, math, re
import gx
from shapely.geometry import box, LineString, Point
from shapely.strtree import STRtree
import fix_texts as FT
W = FT.W


def pts_of(h):
    o = gx.run([{'t': 'spmove', 'h': h}], 'sp')
    l = [x for x in o.splitlines() if x.startswith('spmove')]
    if not l: return None
    return [tuple(map(float, q.split(','))) for q in re.findall(r'\(([-\d.]+),([-\d.]+)\)', l[0]) and re.findall(r'\(([-\d.]+,[-\d.]+)\)', l[0])]


def run(k, passes=2):
    fr = json.load(open(W + '/sheets.json', encoding='utf-8'))['7.%d' % k]
    tot, lines = FT.check(k)
    print('7.%d notes start TOTAL %d' % (k, tot))
    for ps in range(passes):
        if tot == 0: break
        owners = []
        for l in lines:
            m = re.search(r'\{([0-9A-F/]+)\}', l)
            if m:
                for o in m.group(1).split('/'):
                    if o and o not in owners: owners.append(o)
        ns = FT.parse(); ptype = ns['ptype']
        win = box(*fr)
        owners = [o for o in owners if ptype.get(o, '').startswith('SPDSNOTE')]
        if not owners: break
        texts = [(p, poly) for p, poly, s in ns['texts'] if win.intersects(poly)]
        segs = [(p, ls) for p, ls in ns['segs'] if win.intersects(ls)]
        bars = [ls for p, ls in segs if ptype.get(p) == 'LINE']
        hats = [hg for h, hg in ns['hatches'] if win.intersects(hg)]
        inner = box(fr[0] + 2050, fr[1] + 550, fr[2] - 550, fr[3] - 550)
        stamp = box(fr[2] - 500 - 18550, fr[1], fr[2], fr[1] + 6050)
        ops = []; left = []
        for o in owners:
            P = pts_of(o)
            if not P or len(P) < 3: left.append((o, 'pts')); continue
            org, a1, a2 = P[0], P[1], P[2]
            dx, dy = a1[0] - a2[0], a1[1] - a2[1]; L = math.hypot(dx, dy)
            if L < 1:                                          # one bar: leader perpendicular to that bar
                bl = [x for x in bars if x.distance(Point(a1)) < 2]
                if not bl: left.append((o, 'one-arrow')); continue
                (xa, ya), (xb, yb) = bl[0].coords[0], bl[0].coords[-1]; lb = math.hypot(xb - xa, yb - ya)
                b = ((xb - xa) / lb, (yb - ya) / lb); d = (-b[1], b[0]); L = 0.0
            else:
                d = (dx / L, dy / L); b = (-d[1], d[0])           # leader direction, bar direction
            oth_t = [poly for p, poly in texts if p != o]; oth_s = [ls for p, ls in segs if p != o]
            st = STRtree(oth_s); tt = STRtree(oth_t)
            def on_bar(q): return any(bl.distance(Point(q)) < 2 for bl in bars)
            def score(ox, oy, A1, A2):
                poly = box(ox - 1200, oy - 420, ox + 20, oy + 420); qq = poly.buffer(50)
                sc = 0
                if not inner.contains(poly) or poly.intersects(stamp): sc += 5
                sc += sum(1 for i in st.query(qq) if oth_s[i].intersects(qq))
                sc += sum(1 for i in tt.query(qq) if oth_t[i].intersects(qq))
                sc += sum(1 for hg in hats if hg.intersects(poly))
                shelf = LineString([(ox - 1170, oy), (ox, oy)])
                sc += 2 * sum(1 for i in st.query(shelf) if oth_s[i].intersects(shelf))
                for A in (A1, A2):
                    ld = LineString([(ox, oy), A])
                    if ld.length > 1: sc += sum(1 for i in tt.query(ld) if oth_t[i].buffer(15).intersects(ld))
                return sc, poly, shelf, [LineString([(ox, oy), A1]), LineString([(ox, oy), A2])]
            # parameter t along the leader from a2 (0) to a1 (L)
            ts = [L / 2] + [v for e in (520, 900, 1300, 1800, 2300) for v in (L + e, -e)]
            shifts = [0] + [s * sg for s in (200, 400, 600, 900, 1200, 1600, 2000) for sg in (1, -1)]
            best = None
            for sh in shifts:
                A1 = (a1[0] + b[0] * sh, a1[1] + b[1] * sh); A2 = (a2[0] + b[0] * sh, a2[1] + b[1] * sh)
                if sh and not (on_bar(A1) and on_bar(A2)): continue
                for t in ts:
                    if t == L / 2 and L < 900: continue
                    ox, oy = A2[0] + d[0] * t, A2[1] + d[1] * t
                    if abs(d[1]) < 0.2:                        # horizontal leader: shelf (to the left) must not lie on it
                        mnx = min(A1[0], A2[0]); mxx = max(A1[0], A2[0])
                        if not (ox <= mnx - 100 or (ox <= mxx - 100 and ox - 1200 >= mnx + 80)): continue
                    sc, poly, shelf, lead = score(ox, oy, A1, A2)
                    sc += 0.001 * abs(sh) + 0.0001 * abs(t - L / 2)
                    if best is None or sc < best[0]: best = (sc, ox, oy, A1, A2, poly, shelf, lead)
                if best and best[0] < 1: break
            sc, ox, oy, A1, A2, poly, shelf, lead = best
            ops.append({'t': 'spmove', 'h': o, 'items': [[0, ox, oy], [1, A1[0], A1[1]], [2, A2[0], A2[1]]]})
            texts = [(p, pl) for p, pl in texts if p != o] + [(o, poly)]
            segs = [(p, ls) for p, ls in segs if p != o] + [(o, shelf)] + [(o, l) for l in lead]
            if sc >= 1: left.append((o, 'best %.0f' % sc))
        if ops:
            ops.append({'t': 'save'}); out = gx.run(ops, 'fn%d' % k)
            print('notes moved', len(ops) - 1, [l for l in out.splitlines() if 'ERR' in l][:4])
        tot, lines = FT.check(k)
        print('7.%d notes pass %d TOTAL %d left %s' % (k, ps, tot, left[:10]))
    return tot, lines


if __name__ == '__main__':
    tot, lines = run(int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 2)
    print('\n'.join(lines[:30]))
