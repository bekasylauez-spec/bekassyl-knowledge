# re-place flagged position notes (FD<sheet>_<k>) of 3.3–3.6 against the REAL drawing geometry (live.dxf + geom.txt):
# comb across the zone with ticks on the first/last bar, short 45° leader, shelf free of lines and texts (rules §2, 31.10).
import json, os, re, sys, math
import ezdxf, logging
logging.disable(logging.CRITICAL)
from shapely.geometry import LineString as LS, box
from shapely.strtree import STRtree
sys.path.insert(0, '.')
import model as M, gen_fm as G
S = os.path.dirname(os.path.abspath(__file__))
m = json.load(open(os.environ['TEMP'] + '/gx_map.json', encoding='utf-8-sig'))
inv = {v: k for k, v in m.items()}
F = json.load(open('arm/fm_final.json'))
oc = open('w/oc_fm.txt', encoding='utf-8').read()
bad = set()
for h in re.findall(r'"[^"#]*#([0-9A-F]+)"', oc): bad.add(h)
for ln in oc.splitlines():
    mm = re.search(r'ПОЛКА/ЛИНИЯ\s+"[^"]*"\s+<>\s+([0-9A-F]+)', ln)
for ln in oc.splitlines():
    if 'ПОЛКА' in ln:
        # find note handle by position later
        pass
flagged = [inv[h] for h in bad if inv.get(h, '').startswith('FD')]
# ПОЛКА/ЛИНИЯ lines carry no handle: take notes whose shelf contains the reported point
pts = [(float(a), float(b)) for a, b in re.findall(r'ПОЛКА/ЛИНИЯ.*@\((\-?[\d.]+), (\-?[\d.]+)\)', oc)]
segs = []; texts = []; own = {}
for ln in open('w/geom.txt', encoding='utf-8-sig'):
    f = ln.rstrip('\r\n').split('|')
    if f[0] == 'S':
        a = (float(f[3]), float(f[4])); b = (float(f[5]), float(f[6]))
        if a != b: segs.append((f[1], LS([a, b])))
    elif f[0] == 'T' and len(f) > 7 and f[7].strip():
        texts.append((f[1], box(*[float(v) for v in f[3:7]])))
d = ezdxf.readfile('w/live.dxf'); ms = d.modelspace()
for e in ms:
    t = e.dxftype()
    if t == 'LINE': segs.append((e.dxf.handle, LS([(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)])))
    elif t == 'LWPOLYLINE':
        p = [tuple(q[:2]) for q in e.get_points('xy')]
        if e.closed: p = p + p[:1]
        if len(p) > 1: segs.append((e.dxf.handle, LS(p)))
sheet_of = {}
for sh in ('3.3', '3.4', '3.5', '3.6'):
    fx, X, Y = G.origin(sh)
    sheet_of[sh] = (fx, X, Y)
# add notes whose text box contains a ПОЛКА point
for sh in sheet_of:
    fx = sheet_of[sh][0]
    for k in range(80):
        tag = 'FD%s_%d' % (sh, k)
        if tag not in m: continue
        hb = [t for h, t in texts if h == m[tag]]
        for (px, py) in pts:
            X = px + fx; Y = py + 455939
            if any(t.buffer(300).contains(box(X - 1, Y - 1, X + 1, Y + 1)) for t in hb): flagged.append(tag)
flagged = sorted(set(flagged))
print(len(flagged), 'notes to re-place')
KEYS = {'3.3': 'bot_x', '3.4': 'top_x', '3.5': 'bot_y', '3.6': 'top_y'}
ops = []
placed = []
for tag in flagged:
    sh, k = tag[2:].split('_'); k = int(k)
    fx, X, Y = sheet_of[sh]
    key = KEYS[sh]; axis = key.split('_')[1]
    zs = [(z, False) for z in F[key]] + [(z, True) for z in F.get(key + '_3', [])]
    z, th = zs[k]
    A = M.AX_X if axis == 'x' else M.AX_Y
    P = lambda s_, p: (X + s_, Y + p) if axis == 'x' else (X + p, Y + s_)
    hown = m[tag]
    W = box(fx, 455939, fx + 59400, 497939)
    L = [g for h, g in segs if h != hown and g.intersects(W)]
    T = [g for h, g in texts if h != hown and g.intersects(W)] + placed
    tl = STRtree(L); tt = STRtree(T)
    def nl(g): return sum(1 for i in tl.query(g) if L[i].intersects(g))
    def nt(g): return sum(1 for i in tt.query(g) if T[i].intersects(g))
    name = z['pos'] + ('*' if th else '')
    Lsh = 194 * 5 + 300
    gap = z['p1'] - z['p0'] if z['n'] > 1 else 0
    Ls = z['s1'] - z['s0']
    best = None
    for f in [i / 20 for i in range(1, 20)]:
        c = z['s0'] + Ls * f
        if any(abs(c - a) < 300 for a in A.values()): continue
        comb = LS([P(c, z['p0']), P(c, z['p1'])]) if gap else None
        combcost = 0
        if comb is not None:
            # the comb may cross only lines perpendicular to it that are not bars of other zones: count crossings
            combcost = nl(comb.buffer(-0.5) if False else comb) - 2 + 10 * nt(comb)
        Ks = [(c, z['p1']), (c, z['p0'])] + ([(c, (z['p0'] + z['p1']) / 2)] if gap >= 1300 else [])
        for K in Ks:
            for dd in (350, 450, 600, 800, 1000):
                for sg in (1, -1):
                    for sv in (1, -1):
                        O = (K[0] + sg * dd, K[1] + sv * dd)
                        Kp = P(*K); Op = P(*O)
                        left = Op[0] < Kp[0]
                        lab = box(Op[0] - Lsh if left else Op[0], Op[1] - 420, Op[0] if left else Op[0] + Lsh, Op[1] + 420)
                        if not W.buffer(-800).contains(lab): continue
                        ld = LS([Op, Kp])
                        cst = 40 * nl(lab.buffer(30)) + 60 * nt(lab.buffer(60)) + 25 * nt(ld) + 6 * max(0, nl(ld) - 2) + 3 * combcost + dd / 400 + abs(f - 0.5)
                        if best is None or cst < best[0]: best = (cst, Kp, Op, lab, left, c)
    cst, Kp, Op, lab, left, c = best
    placed.append(lab)
    ops.append({'t': 'erase', 'h': [tag]})
    ops.append({'t': 'clone', 'h': 'E7E6A', 'base': [986.812891713809, -2983441.65079645], 'to': list(Op), 'tag': tag})
    ops.append({'t': 'spmove', 'h': tag, 'items': [[1, Kp[0], Kp[1]]]})
    ops.append({'t': 'mcset', 'h': tag, 'set': {'FirstLine': name, 'SecondLine': 'ш.200', 'Angle': math.pi if left else 0.0, 'Arrow': 'Oblique'}})
    tg = [P(c, z['p0'])] + ([P(c, z['p1'])] if gap else [])
    tg = [list(t) for t in tg if abs(t[0] - Kp[0]) + abs(t[1] - Kp[1]) > 1]
    if tg:
        o = {'t': 'comb', 'h': tag, 'k': list(Kp), 'targets': tg, 'arrow': 'oblique'}
        if len(tg) == 1: o['karrow'] = 1
        ops.append(o)
    print(tag, round(cst, 1))
json.dump(ops, open('ops/notefix.json', 'w', encoding='utf-8'), ensure_ascii=False)
