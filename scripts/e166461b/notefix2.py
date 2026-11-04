# Position callouts of 3.3–3.6 in Bekassyl's style (04.11 ✓ sample): note origin ON the comb line, comb = straight line
# across the zone from the first to the last bar (Oblique ticks), extended past the zone to the shelf if the shelf is
# outside; shelf starts at the comb and goes to the free side. Placement against the REAL drawing (live.dxf + geom.txt).
import json, os, sys, math
import ezdxf, logging
logging.disable(logging.CRITICAL)
from shapely.geometry import LineString as LS, box
from shapely.strtree import STRtree
sys.path.insert(0, '.')
import model as M, gen_fm as G
m = json.load(open(os.environ['TEMP'] + '/gx_map.json', encoding='utf-8-sig'))
F = json.load(open('arm/fm_final.json'))
KEYS = {'3.3': 'bot_x', '3.4': 'top_x', '3.5': 'bot_y', '3.6': 'top_y'}
sheets = sys.argv[1].split(',') if len(sys.argv) > 1 else list(KEYS)
ONLY = set(os.environ.get('NF_ONLY', '').split(',')) - {''}
FD = {v for k, v in m.items() if k.startswith('FD') and (not ONLY or k in ONLY)}
segs = []; texts = []
for ln in open('w/geom.txt', encoding='utf-8-sig'):
    f = ln.rstrip('\r\n').split('|')
    if f[1] in FD: continue
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
    elif t == 'MTEXT':
        ins = e.dxf.insert; h = e.dxf.char_height; txt = e.plain_text().split('\n')
        w = max(len(s) for s in txt) * 0.7 * h; hh = len(txt) * 1.6 * h
        texts.append((e.dxf.handle, box(ins[0], ins[1] - hh, ins[0] + w, ins[1])))
ops = []
SH_W = 194 * 5 + 300            # shelf length for «ш.200»
for sh in sheets:
    fx, X, Y = G.origin(sh)
    key = KEYS[sh]; axis = key.split('_')[1]
    zs = [(z, False) for z in F[key]] + [(z, True) for z in F.get(key + '_3', [])]
    A = M.AX_X if axis == 'x' else M.AX_Y
    P = lambda s_, p: (X + s_, Y + p) if axis == 'x' else (X + p, Y + s_)
    W = box(fx, 455939, fx + 59400, 497939)
    inner = box(fx + 2600, 455939 + 600, fx + 59400 - 600, 497939 - 600)
    stamp = box(fx + 59400 - 19500, 455939, fx + 59400, 455939 + 9000)
    L = [g for h, g in segs if g.intersects(W)]
    T = [g for h, g in texts if g.intersects(W)]
    tl = STRtree(L)
    placed = []
    def nl(g): return sum(1 for i in tl.query(g) if L[i].intersects(g))
    def nt(g): return sum(1 for o in T if o.intersects(g)) + sum(1 for o in placed if o.intersects(g))
    # bigger zones first (they have fewer good spots)
    order = sorted(range(len(zs)), key=lambda k: (zs[k][0]['p1'] - zs[k][0]['p0']))
    for k in order:
        z, th = zs[k]
        tag = 'FD%s_%d' % (sh, k)
        if ONLY and tag not in ONLY: continue
        name = z['pos'] + ('*' if th else '')
        gap = z['p1'] - z['p0'] if z['n'] > 1 else 0
        Ls = z['s1'] - z['s0']
        best = None
        for f in [i / 30 for i in range(1, 30)]:
            c = z['s0'] + Ls * f
            if any(abs(c - a) < 250 for a in A.values()): continue
            ys = []
            if gap >= (1100 if axis == 'x' else SH_W - 100):
                for q in (0.5, 0.4, 0.6, 0.3, 0.7, 0.2, 0.8, 0.12, 0.88): ys.append((z['p0'] + gap * q, 'in'))
            for dn in (600, 800, 1000, 1250, 1500, 1800, 2100, 2400, 2800, 3200):
                ys.append((z['p1'] + dn, 'up')); ys.append((z['p0'] - dn, 'dn'))
            for yv, where in ys:
                Op = P(c, yv)
                lo, hi = min(yv, z['p0']), max(yv, z['p1'] if gap else z['p0'])
                lead = LS([P(c, lo), P(c, hi)])
                for side in (1, -1):
                    if axis == 'x':        # shelf horizontal, comb vertical: text box beside the comb
                        lab = box(Op[0], Op[1] - 420, Op[0] + SH_W, Op[1] + 420) if side > 0 else box(Op[0] - SH_W, Op[1] - 420, Op[0], Op[1] + 420)
                    else:                  # bars vertical, comb horizontal: shelf still horizontal, text above/below it
                        lab = box(Op[0], Op[1] - 420, Op[0] + SH_W, Op[1] + 420) if side > 0 else box(Op[0] - SH_W, Op[1] - 420, Op[0], Op[1] + 420)
                    if not inner.contains(lab) or lab.intersects(stamp): continue
                    if axis == 'y':            # horizontal comb: the shelf continues the comb away from the zone
                        if where == 'up' and side < 0: continue
                        if where == 'dn' and side > 0: continue
                        if where == 'in' and not (X + z['p0'] - 1 <= lab.bounds[0] and lab.bounds[2] <= X + z['p1'] + 150): continue
                    cst = 50 * nl(lab.buffer(40)) + 80 * nt(lab.buffer(80))
                    cst += 40 * nt(lead.buffer(20)) + 4 * max(0, nl(lead) - 2)
                    cst += (0 if where == 'in' else 3 + abs(yv - (z['p1'] if where == 'up' else z['p0'])) / 300)
                    cst += abs(f - 0.5) * 2
                    if best is None or cst < best[0]: best = (cst, Op, lab, side, c, lead)
        cst, Op, lab, side, c, lead = best
        placed.append(lab)
        T.append(lead.buffer(30))            # keep later shelves off this comb
        tg = [P(c, z['p0'])] + ([P(c, z['p1'])] if gap else [])
        tg.sort(key=lambda t: abs(t[0] - Op[0]) + abs(t[1] - Op[1]))
        ops.append({'t': 'erase', 'h': [tag]})
        ops.append({'t': 'clone', 'h': 'E7E6A', 'base': [986.812891713809, -2983441.65079645], 'to': list(Op), 'tag': tag})
        ops.append({'t': 'spmove', 'h': tag, 'items': [[1, tg[0][0], tg[0][1]]]})
        ops.append({'t': 'mcset', 'h': tag, 'set': {'FirstLine': name, 'SecondLine': 'ш.200', 'Angle': 0.0 if side > 0 else math.pi, 'Arrow': 'Oblique'}})
        for t in tg[1:]: ops.append({'t': 'addleader', 'h': tag, 'target': list(t)})
        print(tag, round(cst, 1))
json.dump(ops, open('ops/notefix2.json', 'w', encoding='utf-8'), ensure_ascii=False)
