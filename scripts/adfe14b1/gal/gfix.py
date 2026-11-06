# global check of all rigel sheets (one dxfout + one geomdump + oc) and batch free-spot fixing of colliding texts
import sys, os, json, re, pickle, subprocess, gx, prep
from shapely.geometry import Polygon, LineString
from shapely import affinity
import fix as F
W = os.path.join(gx.S, 'w')
marks = json.load(open(os.path.join(prep.LIRA, 'marks.json'), encoding='utf-8'))
SH = {p['no']: [p['SX'], p['SY'], p['SX'] + 31500, p['SY'] + 14850] for M, p in prep.build(marks)}
only = [a for a in sys.argv[1:] if not a.startswith('--')]
if only: SH = {k: v for k, v in SH.items() if k in only}
json.dump(SH, open(os.path.join(W, 'sh_all.json'), 'w'))


def check():
    dxf = os.path.join(W, 'live.dxf'); geo = os.path.join(W, 'geo_all.txt')
    x0 = min(v[0] for v in SH.values()); x1 = max(v[2] for v in SH.values())
    gx.run([dict(t='dxfout', file=dxf), dict(t='geomdump', win=[x0, 420000, x1, 434850], file=geo)], 'gchk', wait=1500)
    r = subprocess.run([sys.executable, '-X', 'utf8', os.path.join(W, 'oc.py'), dxf, os.path.join(W, 'sh_all.json'), '--geom=' + geo,
                        '--dump=' + os.path.join(W, 'dump_{}.pkl')], capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.stdout


def parse(out):
    res = {}; cur = None
    for l in out.splitlines():
        m = re.match(r'== (\S+) (\d+)', l)
        if m: cur = m.group(1); res[cur] = [int(m.group(2)), []]; continue
        if cur and l.startswith('  '): res[cur][1].append(l)
    return res


def moves(no, lines):
    d = pickle.load(open(os.path.join(W, 'dump_%s.pkl' % no), 'rb'))
    T = [(p, Polygon(c), s) for p, c, s in d['T']]; L = [(p, LineString(c)) for p, c in d['L']]
    ptype = d['ptype']; sx, sy = SH[no][0], SH[no][1]
    bad = []
    for l in lines:
        m = re.match(r'\s+(ТЕКСТ/ТЕКСТ|ЛИНИЯ/ТЕКСТ)\s+"(.*)#([0-9A-F]+)"\s+<>\s+(.*?)(?:#([0-9A-F]+))?\s+@', l)
        if m:
            bad.append(m.group(3))
            if m.group(1) == 'ТЕКСТ/ТЕКСТ' and m.group(5): bad.append(m.group(5))
    ops = []; done = set(); frame = (sx + 1000, sy + 250, sx + 31250, sy + 14600)
    for pid in bad:
        if pid in done: continue
        done.add(pid)
        ty = ptype.get(pid, '')
        if ty not in ('DIMENSION', 'TEXT', 'MTEXT'): continue
        mine = [(p, b, s) for p, b, s in T if p == pid]
        if not mine: continue
        poly = mine[0][1]; x0, y0, x1, y1 = poly.bounds; w, h = x1 - x0, y1 - y0
        cands = []
        for dy in (0, -h - 60, h + 60, -2 * h - 120, 2 * h + 120):
            for dx in (0, w * 0.6 + 80, -(w * 0.6 + 80), w + 150, -(w + 150), 1.6 * w + 200, -(1.6 * w + 200), 2.4 * w, -2.4 * w):
                if dx or dy: cands.append((abs(dx) + 1.5 * abs(dy), dx, dy))
        for _, dx, dy in sorted(cands):
            q = affinity.translate(poly, dx, dy); bx = q.bounds
            if bx[0] < frame[0] or bx[2] > frame[2] or bx[1] < frame[1] or bx[3] > frame[3]: continue
            if F.clean(q, pid, T, L):
                c = q.centroid
                ops += [dict(t='dimset', h=[pid], tmove=2), dict(t='dimtx', h=pid, at=[c.x, c.y, 0])] if ty == 'DIMENSION' else [dict(t='move', h=[pid], d=[dx, dy])]
                T = [(p, (q if p == pid else b), ss) for p, b, ss in T]
                break
    return ops


if __name__ == '__main__':
    for k in range(4):
        out = check(); res = parse(out)
        tot = sum(v[0] for v in res.values())
        print('round', k, 'TOTAL', tot, {n: v[0] for n, v in res.items() if v[0]}, flush=True)
        if tot == 0 or '--checkonly' in sys.argv: break
        ops = []
        for no, (n, lines) in res.items():
            if n: ops += moves(no, lines)
        if not ops: break
        gx.run(ops, 'gfix')
    open(os.path.join(W, 'gcheck.txt'), 'w', encoding='utf-8').write(out)
    gx.run([dict(t='save')], 'sv')
