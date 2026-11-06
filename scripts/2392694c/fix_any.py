# Generic nudger for sheet 7.k: flagged SPDS notes -> move only the origin (arrows stay), MTEXT -> small move,
# level marks -> horizontal move only; scored against the real geometry (oc.py parse).  python fix_any.py k [passes]
import sys, os, json, math, re
import gx
from shapely.geometry import box, LineString, Point
from shapely import affinity
from shapely.strtree import STRtree
import fix_texts as FT
W = FT.W


def spts(h):
    o = gx.run([{'t': 'spmove', 'h': h}], 'sp')
    l = [x for x in o.splitlines() if x.startswith('spmove')]
    return [tuple(map(float, q.split(','))) for q in re.findall(r'\(([-\d.]+,[-\d.]+)\)', l[0])] if l else None


def run(k, passes=2, only=None):
    fr = json.load(open(W + '/sheets.json', encoding='utf-8'))['7.%d' % k]
    tot, lines = FT.check(k)
    print('7.%d any start TOTAL %d' % (k, tot))
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
        texts = [(p, poly) for p, poly, s in ns['texts'] if win.intersects(poly)]
        segs = [(p, ls) for p, ls in ns['segs'] if win.intersects(ls)]
        hats = [hg for h, hg in ns['hatches'] if win.intersects(hg)]
        inner = box(fr[0] + 2050, fr[1] + 550, fr[2] - 550, fr[3] - 550)
        stamp = box(fr[2] - 500 - 18550, fr[1], fr[2], fr[1] + 6050)
        ops = []; left = []
        for o in owners:
            t = ptype.get(o, '')
            if only and o not in only: continue
            if not (t.startswith('SPDSNOTE') or t in ('MTEXT', 'TEXT', 'SPDSLEVELMARK')): continue
            own_t = [poly for p, poly in texts if p == o]
            own_s = [ls for p, ls in segs if p == o]
            if not own_t: left.append((o, 'notext')); continue
            oth_t = [poly for p, poly in texts if p != o]; oth_s = [ls for p, ls in segs if p != o]
            st = STRtree(oth_s); tt = STRtree(oth_t)
            if t.startswith('SPDSNOTE'):
                P = spts(o)
                if not P: left.append((o, 'pts')); continue
                org, arr = P[0], P[1:]
                # parts that travel with the origin: texts + horizontal shelf at origin height
                mov_s = [ls for ls in own_s if abs(ls.coords[0][1] - ls.coords[-1][1]) < 1 and abs(ls.coords[0][1] - org[1]) < 2]
            else:
                org, arr = None, []
                mov_s = own_s
            def score(dx, dy):
                sc = 0
                for poly in own_t:
                    q = affinity.translate(poly, dx, dy)
                    if not inner.contains(q) or q.intersects(stamp): sc += 5
                    qb = q.buffer(50)
                    sc += sum(1 for i in st.query(qb) if oth_s[i].intersects(qb))
                    sc += sum(1 for i in tt.query(qb) if oth_t[i].intersects(qb))
                    sc += sum(1 for hg in hats if hg.intersects(q))
                for ls in mov_s:
                    q = affinity.translate(ls, dx, dy)
                    sc += sum(1 for i in st.query(q) if oth_s[i].intersects(q) and oth_s[i].intersection(q).length > 1 or oth_s[i].crosses(q))
                if org:
                    o2 = (org[0] + dx, org[1] + dy)
                    for A in arr:
                        ld = LineString([o2, A])
                        if ld.length > 1: sc += sum(1 for i in tt.query(ld) if oth_t[i].buffer(15).intersects(ld))
                return sc
            if t == 'SPDSLEVELMARK': grid = [(dx, 0) for dx in sorted(range(-3000, 3001, 100), key=abs)]
            else:
                R = 2400 if t.startswith('SPDSNOTE') else 1200
                grid = sorted([(dx, dy) for dx in range(-R, R + 1, 100) for dy in range(-R, R + 1, 100)], key=lambda q: math.hypot(*q))
            s0 = score(0, 0); best = (s0, 0, 0)
            for dx, dy in grid:
                if (dx, dy) == (0, 0): continue
                sc = score(dx, dy)
                if sc < best[0]: best = (sc, dx, dy)
                if sc == 0: break
            sc, dx, dy = best
            if (dx, dy) == (0, 0): left.append((o, 'stuck %d' % sc)); continue
            if t.startswith('SPDSNOTE'): ops.append({'t': 'spmove', 'h': o, 'items': [[0, org[0] + dx, org[1] + dy]]})
            else: ops.append({'t': 'move', 'h': [o], 'd': [dx, dy]})
            texts = [(p, (affinity.translate(pl, dx, dy) if p == o else pl)) for p, pl in texts]
            segs = [(p, (affinity.translate(ls, dx, dy) if (p == o and any(ls.equals(m) for m in mov_s)) else ls)) for p, ls in segs]
            if sc: left.append((o, 'best %d' % sc))
        if ops:
            ops.append({'t': 'save'}); out = gx.run(ops, 'fa%d' % k)
            print('moved', len(ops) - 1, [l for l in out.splitlines() if 'ERR' in l][:4])
        tot, lines = FT.check(k)
        print('7.%d any pass %d TOTAL %d left %s' % (k, ps, tot, left[:10]))
        if not ops: break
    return tot, lines


if __name__ == '__main__':
    tot, lines = run(int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 2)
    print('\n'.join(lines[:30]))
