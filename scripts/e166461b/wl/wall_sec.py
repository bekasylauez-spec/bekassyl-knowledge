# «Разрез (Армирование) М1:50» of a wall, rebuilt from OUR zones (rule 05.11: analog reinforcement objects of a stretched plan are
# never kept): in each plan band all dots / hoops / pins / notes / fan polylines / horizontal-bar polylines / bottom chain are erased
# and drawn again from templates (wl/sec_tpl.json, stashed at x 3500000):
#   dots = zone bars (wall_vert D); hoops: free end -> two Х1 over the edge zone, end at a cross wall -> Х1 on the last bars + Х2 in
#   the cross-wall band (analog 4.31/4.35); Шп1 pins ш.400 in the middle zones, one Шп1 note per piece; zone notes with their own fan
#   below the wall (legs only to the zone's extreme bars, shelves left->right, never crossing); Ск at free ends; straight-bar note;
#   horizontal bars: U at free ends (leg = lap), straight into cross walls; chain 50 | zone segments | 50.
# usage: python wl/wall_sec.py cfg_module [--run]      cfg: SEC = dict(X, A0, V, H, PLANS=[dict(WL, gi, s, pieces=[...])])
import sys, os, json, math, importlib; sys.path.insert(0, 'wl'); from common import *
from notes import notes
C = importlib.import_module(sys.argv[1]).SEC
X, Y, A0 = C['X'], 455939.0, C['A0']
PX = lambda x: X + A0 + 2 * x
V = json.load(open(C['V'], encoding='utf-8')); H = json.load(open(C['H'], encoding='utf-8'))
D = V['D']; LAB = V['LABELS']; HD = H['HD']; HCK = {int(k): v for k, v in H['CKS'].items()}
LAP = lambda d: {10: 610, 12: 730, 14: 860, 16: 980, 18: 1100, 20: 1220}.get(d, int(math.ceil(61 * d / 10.0) * 10))
T = json.load(open('wl/sec_tpl.json'))
TC = {k: (3500000.0 + i * 3000, 455939.0 + 20000) for i, k in enumerate(['dot', 'x1', 'x2', 'pin'])}
TN = {n['h']: n for n in notes(3400000, 400000, 300000, 200000)}
R = listwin(X, Y, 59400, 42000, None); NS = notes(X, Y, 59400, 42000)
ops = []; er = []; nt = [0]
def ins(k, x, y, layer=None):
    o = dict(t='clone', h=T[k], base=[TC[k][0], TC[k][1]], to=[x, y])
    if layer: o['layer'] = layer
    ops.append(o)
def note(k, pts, l1, l2, ang=None):
    tg = 'WS%d' % nt[0]; nt[0] += 1
    ops.append(dict(t='clone', h=T[k], base=[0, 0], to=[0, 0], tag=tg))
    n = TN[T[k]]; m = len(n['pts'])
    pts = pts + [pts[-1]] * (m - len(pts))
    ops.append(dict(t='spmove', h=tg, items=[[i, p[0], p[1]] for i, p in enumerate(pts[:m])]))
    st = {'FirstLine': l1, 'SecondLine': l2}
    if ang is not None: st['Angle'] = ang
    ops.append(dict(t='mcset', h=tg, set=st))
for P in C['PLANS']:
    WL = P['WL']; gi = P['gi']; s = P['s']; d0, st0 = HD[s]; leg = LAP(d0)
    xa = min(p[1] for p in P['pieces']); xb = max(p[2] for p in P['pieces'])
    inb = lambda r, lo=-1700, hi=2700: WL + lo < (r['y0'] + r['y1']) / 2 < WL + hi and PX(xa) - X - 2500 < (r['x0'] + r['x1']) / 2 < PX(xb) - X + 2500
    # erase: inserts (dots / hoops / pins), fans and bar polylines, notes, bottom chain
    er += [r['h'] for r in R if r['t'] == 'INSERT' and inb(r, -400, 400) and (r['lay'].startswith('диам') or r['lay'] == '0') and r['x1'] - r['x0'] < 600]
    for r in R:
        if r['t'] != 'LWPOLYLINE' or not inb(r): continue                                # any layer: analog fans are on диам*
        ys = [p[1] - WL for p in r['sp']]
        if len(r['sp']) >= 2 and all(abs(v) <= 230 for v in ys) and r['x1'] - r['x0'] > 300 and abs(r['sp'][0][0] - r['sp'][-1][0]) + abs(r['sp'][0][1] - r['sp'][-1][1]) > 1: er.append(r['h'])   # bar polylines (open)
        elif any(abs(v) < 250 for v in ys) and any(-1700 < v < -500 for v in ys): er.append(r['h'])                # fans below
    er += [n['h'] for n in NS if (WL - 2250 < n['pts'][0][1] < WL + 2700 or any(abs(p[1] - WL) < 400 for p in n['pts'][1:])) and PX(xa) - X - 2500 < n['pts'][0][0] < PX(xb) - X + 2500]   # any note pointing at the wall too
    CH = [r for r in R if r['t'] == 'DIMENSION' and len(r['sp']) > 2 and abs(r['sp'][0][1] - (WL - 250)) < 30 and abs(r['sp'][1][1] - (WL - 250)) < 30 and -3300 < r['sp'][2][1] - WL < -1800]
    er += [r['h'] for r in CH]
    ydl = CH[0]['sp'][2][1] if CH else WL - 2352
    tch = 'WSC%d' % len(ops)
    ops.append(dict(t='clone', h=T['ch'], base=[0, 0], to=[0, 0], tag=tch))     # stashed template (sheet chains are erased first)
    cur = None
    for (i, a, b, ea, eb) in P['pieces']:
        zs = D[i][gi]
        # dots
        for z in zs:
            for xb_ in z[5]: ins('dot', PX(xb_), Y + WL, 'диам%d' % z[3])
        # hoops and their notes
        for side, e in (('L', ea), ('R', eb)):
            sg = 1 if side == 'L' else -1
            if e[0] == 'F':
                hk, offs, hl = C.get('FREE_HOOP', ('x1', [150, 350], 'Х1'))       # analog of this wall: См-8 -> two Х1, См-7 -> three Х2
                f = e[1]; hx = [f + sg * o for o in offs]
                for x in hx: ins(hk, PX(x), Y + WL)
                note('nx', [[PX(f) - sg * 311, Y + WL + 1637]] + [[PX(x), Y + WL + 181] for x in hx], hl, 'ш.200', math.pi if side == 'L' else 0)
            else:
                f, bc = e[1], e[2]; hx1 = f + sg * 150
                ins('x1', PX(hx1), Y + WL); ins('x2', PX(bc), Y + WL)
                note('nx', [[PX(bc) - sg * 400, Y + WL + 1637], [PX(bc), Y + WL + 181], [PX(hx1), Y + WL + 181]], 'Х1;Х2', 'ш.200', math.pi if side == 'L' else 0)
        # pins in the middle zones (ш.400), one Шп1 note per piece
        pins = []
        for z in zs:
            if z[0] != 'M': continue
            bars = z[5]; x = bars[0] + 200
            while x <= bars[-1] - 150:
                xb_ = min(bars, key=lambda q: abs(q - x)); pins.append(xb_); x += 400
        for x in pins: ins('pin', PX(x), Y + WL)
        if pins:
            mid = (a + b) / 2; rp = [q for q in pins if q >= mid - 50]
            pk = sorted(rp if len(rp) >= 3 else pins, key=lambda q: abs(q - mid))[:3]     # pins right of the middle: legs clear of the bar note (left)
            note('nsh', [[PX(mid), Y + WL + 2171]] + [[PX(x), Y + WL] for x in sorted(pk, reverse=True)], 'Шп1', 'ш.400х400', 0)
        # horizontal bars: polyline A (bottom bar, U at a free left end), polyline B (top bar, U at a free right end)
        fl = ea[0] == 'F'; fr = eb[0] == 'F'
        x0 = PX(a) + 46 if fl else PX(ea[2] - 105) if ea[0] == 'J' else PX(a + 20)
        x1 = PX(b) - 46 if fr else PX(eb[2] + 105) if eb[0] == 'J' else PX(b - 20)
        yt, yb = Y + WL + 171, Y + WL - 170
        if fl: ops.append(dict(t='pl', p=[[x0 + 2 * leg, yt], [x0 + 113, yt], [x0, yt - 100], [x0, yb + 100], [x0 + 113, yb], [x1, yb]], b=[0, 0.4142, 0, 0.4142, 0, 0], layer='диам%d' % d0, lw=40))
        else: ops.append(dict(t='pl', p=[[x0, yb], [x1, yb]], layer='диам%d' % d0, lw=40))
        yt2, yb2 = Y + WL + 210, Y + WL - 130
        if fr: ops.append(dict(t='pl', p=[[x0, yt2], [x1 - 113, yt2], [x1, yt2 - 100], [x1, yb2 + 100], [x1 - 113, yb2], [x1 - 2 * leg, yb2]], b=[0, -0.4142, 0, -0.4142, 0, 0], layer='диам%d' % d0, lw=40))
        else: ops.append(dict(t='pl', p=[[x0, yt2], [x1, yt2]], layer='диам%d' % d0, lw=40))
        # Ск notes at free ends, straight-bar note at the quarter of the piece
        ck = 'Ск%d' % HCK[d0]
        if fl: note('nck', [[PX(a) - 398, Y + WL + 429], [x0, Y + WL]], ck, '(%%%%C%d)' % d0, math.pi)
        if fr: note('nck', [[PX(b) + 398, Y + WL + 429], [x1, Y + WL]], ck, '(%%%%C%d)' % d0, 0)
        q = a + 0.18 * (b - a)
        note('nck', [[PX(q), Y + WL + 760], [PX(q), Y + WL + 210]], str(P['hpos'][i]), '(%%%%C%d)' % d0, 0)      # vertical leader from the shelf start (Bekassyl 05.11)
        # zone notes: fans below, shelves left -> right
        YT, YS = Y + WL - 144, Y + WL - 1161
        cur = PX(a) - 1e9 if cur is None else cur
        zn = []                                                     # neighbouring zones with the same positions and step: one note
        for z in zs:
            lab = LAB['%d|%d|%s' % (i, gi, z[0])]
            if zn and zn[-1][0] == lab and zn[-1][3] == z[4]: zn[-1] = (lab, zn[-1][1], z[2], z[4])
            else: zn.append((lab, z[1], z[2], z[4]))
        bnd = [PX(v) for sg in [q_ for z in zs for q_ in z[6]] for v in sg[:2]] + [PX(zs[0][1] - 50), PX(zs[-1][2] + 50)]
        bnd += [X + r['sp'][0][0] for r in R if r['t'] == 'SPDSCONSTRUCTIONLINE' and abs(r['sp'][0][0] - r['sp'][1][0]) < 1 and min(r['y0'], r['y1']) < WL - 1161 < max(r['y0'], r['y1'])]   # axis lines
        def place(c0, lo_, hi_):                                     # note text starts at its origin (about 960 wide): clear of extension / axis lines
            for dd in [0] + [sg_ * 60 * k for k in range(1, 70) for sg_ in (1, -1)]:
                c = c0 + dd
                if lo_ <= c and c + 960 <= hi_ and not any(c - 60 < v < c + 1020 for v in bnd): return c
            return c0
        for k_, (lab, z1, z2, stp) in enumerate(zn):
            edge = z2 - z1 <= 600 and len(zn) > 1
            if edge and k_ == 0:                                     # free-end edge zone at the left: fan out of the end, shelf in the opening
                A_ = PX(z1) - 300; c = place(A_ - 1180, A_ - 3200, A_)
                ops.append(dict(t='pl', p=[[PX(z2), YT], [A_, YS], [min(A_ - 1400, c - 60), YS]], layer='Размеры'))
                ops.append(dict(t='pl', p=[[PX(z1), YT], [A_, YS]], layer='Размеры'))
                note('nz', [[c, YS], [c, YS]], lab, 'ш.%d' % stp)
            elif edge:                                                # free-end edge zone at the right
                A_ = PX(z2) + 300; c = place(A_ + 220, A_, A_ + 3200)
                ops.append(dict(t='pl', p=[[PX(z1), YT], [A_, YS], [max(A_ + 1400, c + 1020), YS]], layer='Размеры'))
                ops.append(dict(t='pl', p=[[PX(z2), YT], [A_, YS]], layer='Размеры'))
                note('nz', [[c, YS], [c, YS]], lab, 'ш.%d' % stp)
            else:
                B_ = PX(z1) + 500; E_ = max(PX(z2) - 400, B_ + 1100)
                ops.append(dict(t='pl', p=[[PX(z1), YT], [B_, YS], [E_, YS], [PX(z2), YT]], layer='Размеры'))
                tx0 = place((B_ + E_) / 2 - 480, B_, E_)
                note('nz', [[tx0, YS], [tx0, YS]], lab, 'ш.%d' % stp)
        # bottom chain
        lo = zs[0][1] - 50; hi = zs[-1][2] + 50
        segs = [(lo, lo + 50, 50, 1)] + sorted([sg for z in zs for sg in z[6]]) + [(hi - 50, hi, 50, 1)]
        mg = []
        for q_ in [q_ for q_ in segs if q_[1] > q_[0]]:                    # one dimension per run of equal steps
            if mg and mg[-1][2] == q_[2] and abs(mg[-1][1] - q_[0]) < 1: mg[-1] = (mg[-1][0], q_[1], q_[2], mg[-1][3] + q_[3])
            else: mg.append(q_)
        for k, (s0, s1, stp, n_) in enumerate(mg):
            kw = dict(t='dim', h=tch, p1=[PX(s0), Y + WL - 250], p2=[PX(s1), Y + WL - 250], dl=[PX((s0 + s1) / 2), Y + ydl], rot=0, txt=('%dх%d' % (stp, n_)) if n_ > 1 else '')
            if 2 * (s1 - s0) < 650: kw['tx'] = [PX((s0 + s1) / 2), Y + ydl - 330 - (330 if k % 2 else 0)]
            ops.append(kw)
    ops.append(dict(t='erase', h=[tch]))
ops = [dict(t='erase', h=sorted(set(er)))] + ops + [dict(t='save')]
print('erase', len(set(er)), 'ops', len(ops))
if '--run' in sys.argv:
    out = gx.run(ops, 'wsec'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-8:])
