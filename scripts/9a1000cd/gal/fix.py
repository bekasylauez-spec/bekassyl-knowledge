# automatic free-spot placement for colliding texts of one sheet (after chk1.py): dims via dimtx (no leader), TEXT/MTEXT via move
import sys, os, pickle, re, subprocess, json, gx
from shapely.geometry import Polygon, LineString
from shapely import affinity
W = os.path.join(gx.S, 'w')


def check(no, sx, sy):
    r = subprocess.run([sys.executable, '-X', 'utf8', 'chk1.py', no, str(sx), str(sy)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    tot = [int(l.split()[1]) for l in r.stdout.splitlines() if l.startswith('TOTAL')]
    return (tot[0] if tot else 999), r.stdout


def clean(poly, pid, T, L, skip=()):
    sh = poly.buffer(-0.12 * (poly.area / 4) ** 0.5 * 0.3)
    for p, b, s in T:
        if p == pid or p in skip: continue
        if sh.intersects(b) and sh.intersection(b).area > 0.005 * min(poly.area, b.area): return False
    for p, ls in L:
        if p == pid: continue
        if sh.intersects(ls) and sh.intersection(ls).length > 5: return False
    return True


def fix(no, sx, sy, rounds=3, width=31250):
    tot, out = check(no, sx, sy)
    for k in range(rounds):
        if tot == 0: break
        d = pickle.load(open(os.path.join(W, 'dump_%s.pkl' % no), 'rb'))
        T = [(p, Polygon(c), s) for p, c, s in d['T']]; L = [(p, LineString(c)) for p, c in d['L']]
        ptype = d['ptype']
        bad = []
        for l in out.splitlines():
            m = re.match(r'\s+(ТЕКСТ/ТЕКСТ|ЛИНИЯ/ТЕКСТ)\s+"(.*)#([0-9A-F]+)"\s+<>\s+(.*?)(?:#([0-9A-F]+))?\s+@', l)
            if m:
                bad.append(m.group(3))
                if m.group(1) == 'ТЕКСТ/ТЕКСТ' and m.group(5): bad.append(m.group(5))
        ops = []; done = set()
        frame = (sx + 1000, sy + 250, sx + width, sy + 14600)
        for pid in bad:
            if pid in done: continue
            done.add(pid)
            ty = ptype.get(pid, '')
            if ty not in ('DIMENSION', 'TEXT', 'MTEXT'): continue
            mine = [(p, b, s) for p, b, s in T if p == pid]
            if not mine: continue
            _, poly, s = mine[0]
            x0, y0, x1, y1 = poly.bounds; w, h = x1 - x0, y1 - y0
            cands = []
            for dy in (0, -h - 60, h + 60, -2 * h - 120, 2 * h + 120):
                for dx in (0, w * 0.6 + 80, -(w * 0.6 + 80), w + 150, -(w + 150), 1.6 * w + 200, -(1.6 * w + 200), 2.4 * w, -2.4 * w):
                    if dx == 0 and dy == 0: continue
                    cands.append((abs(dx) + 1.5 * abs(dy), dx, dy))
            cands.sort()
            for _, dx, dy in cands:
                q = affinity.translate(poly, dx, dy)
                bx = q.bounds
                if bx[0] < frame[0] or bx[2] > frame[2] or bx[1] < frame[1] or bx[3] > frame[3]: continue
                if clean(q, pid, T, L):
                    c = q.centroid
                    if ty == 'DIMENSION':
                        ops += [dict(t='dimset', h=[pid], tmove=2), dict(t='dimtx', h=pid, at=[c.x, c.y, 0])]
                    else:
                        ops.append(dict(t='move', h=[pid], d=[dx, dy]))
                    T = [(p, (q if p == pid else b), ss) for p, b, ss in T]
                    break
        if not ops: break
        gx.run(ops, 'fix')
        tot, out = check(no, sx, sy)
    return tot, out


if __name__ == '__main__':
    no, sx, sy = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    tot, out = fix(no, sx, sy)
    print('\n'.join(l for l in out.splitlines() if l.startswith('  ') or l.startswith('TOTAL'))[-3000:])
