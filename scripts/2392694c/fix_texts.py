# Move flagged dimension texts of sheet 7.k to a free spot along their own dimension line (oc.py rules).
# python fix_texts.py <k> [passes]   — needs chk1.py (dump + oc) ; prints what is left for manual work
import sys, os, json, math, re, subprocess
import gx
from shapely.geometry import box, LineString, Polygon, Point
from shapely import affinity
from shapely.strtree import STRtree
W = os.path.join(gx.S, 'chk').replace(os.sep, '/')


def check(k):
    r = subprocess.run([sys.executable, os.path.join(gx.S, 'chk1.py'), str(k)], capture_output=True, text=True, encoding='utf-8',
                       env=dict(os.environ, PYTHONIOENCODING='utf-8'), cwd=gx.S)
    txt = open(W + '/oc_%d.txt' % k, encoding='utf-8').read()
    m = re.search(r'TOTAL (\d+)', txt)
    return (int(m.group(1)) if m else -1), [l for l in txt.splitlines() if l.startswith('  ')]


def parse():
    src = open(W + '/oc.py', encoding='utf-8').read(); src = src[:src.index('total = 0')]
    old = sys.argv; sys.argv = ['oc.py', W + '/live.dxf', W + '/one.json', '--geom=' + W + '/geom.txt']
    ns = {'__name__': 'ocparse'}; exec(compile(src, 'oc.py', 'exec'), ns); sys.argv = old
    return ns


def run(k, passes=3):
    fr = json.load(open(W + '/sheets.json', encoding='utf-8'))['7.%d' % k]
    tot, lines = check(k)
    print('7.%d start TOTAL %d' % (k, tot))
    for ps in range(passes):
        if tot == 0: break
        owners = []
        for l in lines:
            m = re.search(r'\{([0-9A-F/]+)\}', l)
            if m:
                for o in m.group(1).split('/'):
                    if o and o not in owners: owners.append(o)
        ns = parse(); doc = ns['doc']; ptype = ns['ptype']
        win = box(*fr)
        texts = [(p, poly) for p, poly, s in ns['texts'] if win.intersects(poly)]
        segs = [(p, ls) for p, ls in ns['segs'] if win.intersects(ls)]
        hats = [hg for h, hg in ns['hatches'] if win.intersects(hg)]
        inner = box(fr[0] + 2050, fr[1] + 550, fr[2] - 550, fr[3] - 550)
        stamp = box(fr[2] - 500 - 18550, fr[1], fr[2], fr[1] + 6050)
        ops = []; manual = []; moved = set()
        for o in owners:
            if ptype.get(o) != 'DIMENSION':
                manual.append((o, ptype.get(o))); continue
            try: e = doc.entitydb[o]
            except Exception: manual.append((o, 'nodxf')); continue
            ang = math.radians(e.dxf.get('angle', 0)) if e.dimtype & 7 == 0 else None
            p2, p3, dp = e.dxf.defpoint2, e.dxf.defpoint3, e.dxf.defpoint
            if ang is None:                                    # aligned
                ang = math.atan2(p3.y - p2.y, p3.x - p2.x)
            while ang > math.pi / 2 + 1e-6: ang -= math.pi
            while ang <= -math.pi / 2 + 1e-6: ang += math.pi
            u = (math.cos(ang), math.sin(ang)); n = (-u[1], u[0])
            t2 = (p2.x - dp.x) * u[0] + (p2.y - dp.y) * u[1]; t3 = (p3.x - dp.x) * u[0] + (p3.y - dp.y) * u[1]
            ta, tb = min(t2, t3), max(t2, t3)
            own = [poly for p, poly in texts if p == o]
            if not own: manual.append((o, 'notext')); continue
            tp = own[0]; c = tp.centroid
            # text size along u / n
            pts = list(tp.exterior.coords)
            wu = max((x - c.x) * u[0] + (y - c.y) * u[1] for x, y in pts) * 2
            hn = max((x - c.x) * n[0] + (y - c.y) * n[1] for x, y in pts) * 2
            side = 1                                           # AutoCAD: text on the reading-up side of the dim line
            oth_t = [poly for p, poly in texts if p != o]
            oth_s = [ls for p, ls in segs if p != o]
            st = STRtree(oth_s); tt = STRtree(oth_t)
            def bad(poly, ext):
                q = poly.buffer(50); nb = 0
                if not inner.contains(poly) or poly.intersects(stamp): nb += 5
                nb += sum(1 for i in st.query(q) if oth_s[i].intersects(q))
                nb += sum(1 for i in tt.query(q) if oth_t[i].intersects(q))
                nb += sum(1 for hg in hats if hg.intersects(poly))
                if ext is not None: nb += sum(1 for i in tt.query(ext) if oth_t[i].buffer(15).intersects(ext))
                return nb
            cands = []
            if tb - ta >= wu + 120: cands.append((ta + tb) / 2)
            for ex in (0, 250, 500, 800, 1200, 1700):
                cands += [tb + wu / 2 + 160 + ex, ta - wu / 2 - 160 - ex]
            best = None
            for j, t in enumerate(cands):
                cx = dp.x + u[0] * t + n[0] * side * (hn / 2 + 100); cy = dp.y + u[1] * t + n[1] * side * (hn / 2 + 100)
                poly = affinity.rotate(box(cx - wu / 2, cy - hn / 2, cx + wu / 2, cy + hn / 2), ang, origin=(cx, cy), use_radians=True)
                ext = None
                if t - wu / 2 < ta or t + wu / 2 > tb:
                    e0, e1 = min(ta, t - wu / 2), max(tb, t + wu / 2)
                    ext = LineString([(dp.x + u[0] * e0, dp.y + u[1] * e0), (dp.x + u[0] * e1, dp.y + u[1] * e1)])
                sc = bad(poly, ext) + 0.01 * j
                if best is None or sc < best[0]: best = (sc, t, poly, ext)
                if sc < 1: break
            sc, t, poly, ext = best
            at = [dp.x + u[0] * t + n[0] * side * 0.01, dp.y + u[1] * t + n[1] * side * 0.01, 0]
            # text position point: AutoCAD puts the text 100 off the given point on the dim-line side -> pass the point on the line
            ops.append({'t': 'dimtx', 'h': o, 'at': at}); moved.add(o)
            texts = [(p, pl) for p, pl in texts if p != o] + [(o, poly)]
            if ext is not None: segs.append((o, ext))
            if sc >= 1: manual.append((o, 'best %.0f' % sc))
        if ops:
            ops.append({'t': 'save'})
            out = gx.run(ops, 'fx%d' % k); print('moved', len(moved), [l for l in out.splitlines() if 'ERR' in l][:5])
        tot, lines = check(k)
        print('7.%d pass %d TOTAL %d manual %s' % (k, ps, tot, manual[:12]))
        if not ops: break
    return tot, lines


if __name__ == '__main__':
    tot, lines = run(int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 3)
    print('\n'.join(lines[:40]))
