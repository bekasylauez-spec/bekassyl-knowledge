# См-1 sheet 5.2 (analog 4.2 reworked): reinforcement layer redrawn in the analog's grammar with the analog's own objects
#  * groups of storeys as in the analog: G0 = -4.650..-0.100, G1 = -0.100..+7.100, G2 = +7.100..+13.400, G3 = +13.400..+19.700
#    (bars span a group, splices only at -0.100 / +7.100 / +13.400, staggered A;B, lap 61d of the larger Ø, gap 0.3L)
#  * zones per piece: free-end edge zone 450 ш.100 (Ø by the LIRA edge peak), middle ш.200 Ø12-16 (else ш.100)
#  * each zone drawn by its two extreme bars (A left, B right), the upper group 20 mm to the right; notes cloned from the analog note
import sys, os, json, math; sys.path.insert(0, 'wl'); from common import *
from notes import notes
import importlib
CFG = importlib.import_module(sys.argv[1]).VERT                      # e.g. wl/cfg_sm2.py -> VERT dict
SX, SY = CFG['SX'], 455939.0
def W(x, y): return [SX + x, SY + y]
AX1 = CFG['AX1']
L = CFG['L']
G = CFG.get('G', [(0, 1), (1, 3), (3, 5), (5, len(L) - 1)])          # storey index ranges of the groups
SLAB = 250.0; EDGE = 450.0; TOPC = 30.0
PIECES = CFG['PIECES']; LIRA = CFG['LIRA']; ENDS = CFG['ENDS']; NP = len(PIECES)
LAP = lambda d: {10: 610, 12: 730, 14: 860, 16: 980, 18: 1100, 20: 1220}.get(d, int(math.ceil(61 * d / 10.0) * 10))   # 61d as in the analog lap table (B25)
GAP = lambda lap: int(round(0.3 * lap, -1))
A = lambda d: math.pi * d * d / 400
DS = [12, 14, 16, 18, 20, 22, 25, 28]
CELLS = [c for c in json.load(open('arm/wall_cells.json')) if c['pl'] == CFG['PLANE']]
KX = ('x0', 'x1') if CFG['PLANE'][0] == 'y' else ('y0', 'y1')
LEV = CFG.get('LEV', [-4.65, -0.1, 3.95, 7.1, 10.25, 13.4, 16.55, 19.7])
v = lambda c: max(c['As'][2], c['As'][3])

def split(lo, hi, st):
    """bars from lo to hi (both ends included), step st; the leftover (< st) is one space in the middle (analog)"""
    D_ = hi - lo; n = int(D_ // st + 1e-6); rem = int(round(D_ - n * st))
    if rem < 5: spaces = [st] * n
    else: k1 = n // 2; spaces = [st] * k1 + [rem] + [st] * (n - k1)
    pos = [lo]
    for sp_ in spaces: pos.append(pos[-1] + sp_)
    segs = []; x = lo
    for sp_ in spaces:
        if segs and segs[-1][2] == sp_: segs[-1] = (segs[-1][0], x + sp_, sp_, segs[-1][3] + 1)
        else: segs.append((x, x + sp_, sp_, 1))
        x += sp_
    return pos, segs
def make_zones(a, b, el, er, dL, dR, dm, sm):
    """first and last bar 50 from the faces; edge zones 4 x 100 at free ends; the middle divided by its step (leftover in the middle)"""
    zs = []; lo, hi = a + 50, b - 50
    if el: zs.append(('L', a + 50, a + 450, dL, 100, [a + 50 + 100 * k for k in range(5)], [(a + 50, a + 450, 100, 4)])); lo = a + 450
    if er: zs.append(('R', b - 450, b - 50, dR, 100, [b - 450 + 100 * k for k in range(5)], [(b - 450, b - 50, 100, 4)])); hi = b - 450
    pos, segs = split(lo, hi, sm)
    inner = pos[(1 if el else 0):(len(pos) - 1 if er else len(pos))]
    zs.insert(1 if el else 0, ('M', inner[0], inner[-1], dm, sm, inner, segs))
    return zs
TOP = lambda i: CFG.get('PTOP', {}).get(i, G[-1][1])                    # top level index of piece i
REQ = []
for i, ((a, b), (la, lb), (el, er)) in enumerate(zip(PIECES, LIRA, CFG.get('LENDS', ENDS))):     # LENDS: free ends as seen in the LIRA cells (mirrored pieces)
    row = []
    for gi_, (g0, g1) in enumerate(G):
        if gi_ == len(G) - 1: g1 = TOP(i)
        if gi_ == 0 and CFG.get('PIECES0') and CFG['PIECES0'][i] is None: row.append(None); continue
        if gi_ == 0 and CFG.get('PIECES0'):                            # basement pieces differ (e.g. a full wall below the openings)
            (la, lb), (el, er) = CFG['LIRA0'][i], CFG['ENDS0'][i]
        else:
            (la, lb), (el, er) = LIRA[i], CFG.get('LENDS', ENDS)[i]
        cs = [c for c in CELLS if max(LEV[g0], CFG.get('ZMIN', -99)) - 1e-3 <= c['z0'] < LEV[g1] - 1e-3 and c[KX[1]] > la + 1 and c[KX[0]] < lb - 1]
        xs = sorted(set(c[KX[0]] for c in cs))
        colL = [c for c in cs if c[KX[0]] == xs[0]]; colR = [c for c in cs if c[KX[0]] == xs[-1]]
        mid = [c for c in cs if (not el or c[KX[0]] != xs[0]) and (not er or c[KX[0]] != xs[-1])] or cs
        dL = next(d for d in DS if A(d) * 10 >= max(v(c) for c in colL) - 1e-6) if el else None
        dR = next(d for d in DS if A(d) * 10 >= max(v(c) for c in colR) - 1e-6) if er else None
        req = max([v(c) for c in mid] + [0])
        dm, sm = next((d, s) for d, s in ((12, 200), (14, 200), (16, 200), (12, 100), (14, 100), (16, 100), (18, 100), (20, 100), (22, 100), (25, 100)) if A(d) * 1000 / s >= req - 1e-6)
        row.append((dL, dR, dm, sm))
    REQ.append(row)
# one Ø per group for all edge zones and one (Ø, step) for all middle zones (fewer positions, as in the analog)
D = [[None] * 4 for _ in range(NP)]
for g in range(4):
    de = max([x for i in range(NP) if REQ[i][g] for x in REQ[i][g][:2] if x] or [12])
    dm, sm = max([REQ[i][g][2:] for i in range(NP) if REQ[i][g]], key=lambda t: (A(t[0]) * 1000 / t[1], -t[1]))
    if CFG.get('EDGE_GE_MID') and de < dm: de = dm                     # free-end edge zone never thinner than the middle
    for i, ((a, b), (el, er)) in enumerate(zip(PIECES, ENDS)):
        if g == 0 and CFG.get('PIECES0') and CFG['PIECES0'][i] is None: D[i][g] = []; continue
        if g == 0 and CFG.get('PIECES0'): (a, b), (el, er) = CFG['PIECES0'][i], CFG['ENDS0'][i]
        D[i][g] = make_zones(a, b, el, er, de, de, dm, sm)
        if g == 0 and CFG.get('ONE0'): D[i][g] = make_zones(CFG['ONE0'][0], CFG['ONE0'][1], False, False, de, de, dm, sm) if i == 0 else []
if CFG.get('SMOOTH'):                                    # rule: Ø of neighbouring storey groups differ by <= 4 mm (raise the smaller one)
    for kind in 'LRM':
        for _ in range(4):
            for i in range(NP):
                ds = [next((z[3] for z in D[i][g] if z[0] == kind), None) for g in range(4)]
                for g in range(4):
                    if ds[g] is None: continue
                    nb = [ds[h] for h in (g - 1, g + 1) if 0 <= h < 4 and ds[h] is not None]
                    need = max([ds[g]] + [d_ - 4 for d_ in nb]); need = next(d_ for d_ in DS if d_ >= need)
                    if need != ds[g]:
                        D[i][g] = [tuple([z[0], z[1], z[2], need] + list(z[4:])) if z[0] == kind else z for z in D[i][g]]; ds[g] = need
        # one Ø per group and kind over all pieces (as in the analog)
        for g in range(4):
            mx = max([z[3] for i in range(NP) for z in D[i][g] if z[0] == kind] or [0])
            for i in range(NP): D[i][g] = [tuple([z[0], z[1], z[2], mx] + list(z[4:])) if z[0] == kind else z for z in D[i][g]]
def run(go=False):
    WW, HH = CFG.get('WH', (59400, 42000))
    R = listwin(SX, SY, WW, HH, None)
    N = notes(SX, SY, WW, HH)
    tN = next(n['h'] for n in N if n['l2'].startswith('ш.') and len(n['pts']) == 3)
    tC = next((n['h'] for n in N if n['l1'].startswith('Ск') and len(n['pts']) == 3), tN)
    EL = lambda r: CFG.get('XLO', AX1 - 800) < r['x0'] and r['x1'] < CFG['AXES'][-1] + 1700 and r['y0'] > L[0] - 3600
    er = [r['h'] for r in R if r['t'] in ('LINE', 'LWPOLYLINE') and EL(r) and r['lay'].lower().startswith('диам')]
    er += [r['h'] for r in R if r['t'] == 'DIMENSION' and EL(r) and not (r['sp'][0][1] < L[0] - 1947 and r['sp'][1][1] < L[0] - 1947)]
    er += [r['h'] for r in R if r['t'] == 'DIMENSION' and r['y0'] > L[0] - 2900 and r['sp'][0][1] > L[0] - 5 and r['sp'][0][1] < L[0] + 5 and abs(r['sp'][0][1] - r['sp'][1][1]) < 1 and len(r['sp']) > 2 and r['sp'][2][0] > CFG.get('XLO', AX1 - 1300) and r['x1'] < CFG['AXES'][-1] + 2000 and r['h'] not in er]
    AN = CFG.get('ANALOG_NOTES')
    if not AN:
        er += [n['h'] for n in N if AX1 - 2300 < n['pts'][0][0] < CFG['AXES'][-1] + 3200 and n['pts'][0][1] > L[0] - 1600]
    else:                                               # Bekassyl: use the analog's own notes (text / leader points changed, clones for extra zones)
        ANN = {}
        for n in N:
            if len(n['pts']) < 3 or n['pts'][0][1] < L[0] - 1600: continue
            tx_ = [p[0] - AX1 for p in n['pts'][1:]]; cy = n['pts'][1][1]
            for i_, (a_, b_) in enumerate(PIECES):
                if a_ - 300 <= min(tx_) and max(tx_) <= b_ + 300:
                    st_ = next((s_ for s_ in range(len(L) - 1) if L[s_] <= cy < L[s_ + 1]), len(L) - 1)
                    ANN.setdefault((i_, 'C' if n['l1'].startswith('Ск') else st_), []).append(n)
        NSIDE = {}
        for (i_, k_), lst in ANN.items():
            n = lst[0]
            if k_ != 'C': NSIDE[i_] = 'L' if n['pts'][0][0] < min(p[0] for p in n['pts'][1:]) else 'R'
    DIAG = {(round(r['sp'][0][0]), round(r['sp'][0][1])): (r['sp'][1], r['sp'][2]) for r in R if r['t'] == 'LWPOLYLINE' and len(r['sp']) == 3 and r['y0'] > L[0] - 1100}
    DIAGE = {(round(r['sp'][2][0]), round(r['sp'][2][1])): (r['sp'][0], r['sp'][1]) for r in R if r['t'] == 'LWPOLYLINE' and len(r['sp']) == 3 and r['y0'] > L[0] - 1100}
    try:
        mp_ = json.load(open(os.environ['TEMP'] + '/gx_map.json', encoding='utf-8-sig'))
        old_ = [v_ for k_, v_ in mp_.items() if k_.startswith('WVa%d_' % SX)]
    except Exception: old_ = []
    er += old_                                           # clones of an earlier run of this sheet
    ops = [dict(t='clone', h=tN, base=[0, 0], to=[0, -200000], tag='S1N'), dict(t='clone', h=tC, base=[0, 0], to=[0, -200000], tag='S1C'),
           dict(t='erase', h=er)]
    POS = {}; BARS = []; k = [0]; LABELS = {}
    def pos_of(key):
        if key not in POS: POS[key] = len(POS) + 1 + CFG.get('P0', 0)
        return POS[key]
    kk_ = [0]
    def note(tpl, l1, l2, org, tg):          # analog note style; text away from the leaders: right of the origin (new note) or left (clone of the analog's left note)
        if tg and min(p[0] for p in tg) > org[0]:
            tag = 'WVn%d' % kk_[0]; kk_[0] += 1
            ops.append(dict(t='clone', h='TPLNL:59CB4A', base=[0, 0], to=[0, 0], tag=tag))
            ops.append(dict(t='spmove', h=tag, items=[[0] + list(org)] + [[j + 1] + list(p) for j, p in enumerate(tg[:2])]))
            ops.append(dict(t='mcset', h=tag, set={'FirstLine': l1.replace('%%%%', '%%'), 'SecondLine': l2}))
        else:
            ops.append(dict(t='note', l1=l1.replace('%%%%', '%%'), l2=l2, origin=org, targets=tg, scale=100, ts=2.5, style='ГОСТ 2.304', arrow='oblique', layer='Размеры'))
    def zone(i, g, kind):
        for z in (D[i][g] or D[0][g]):
            if z[0] == kind: return z
        return max(D[i][g] or D[0][g], key=lambda z: z[3])                      # other pieces in that group (basement): the largest Ø
    def lap_at(i, g, kind):              # lap at the top splice of group g
        d = zone(i, g, kind)[3]; dn = zone(i, g + 1, kind)[3]
        return LAP(max(d, dn))
    CH = []
    ZM = CFG.get('NOTE_MODE') == 'zone'; ZQ = []; VB = []; PT = []; CHB = []      # PT: placed text boxes / shelves (wall x, sheet-rel y)
    DG = [[(p[0] - AX1, p[1]) for p in r['sp']] for r in R if r['t'] == 'LWPOLYLINE' and len(r['sp']) == 3 and r['y0'] > L[0] - 1100]
    AXR = [a_ - AX1 for a_ in CFG['AXES']]
    for i in range(NP):                                                  # Ск legs at the top (drawn later): obstacles for the notes
        for z in D[i][3]:
            for x in (z[1] - 20, z[2] + 20): VB.append((x, L[TOP(i)] - TOPC - LAP(z[3]), L[TOP(i)] - TOPC))
    def segx(p, q, y):                                                   # x where segment p-q crosses height y (or None)
        if (p[1] - y) * (q[1] - y) > 0 or p[1] == q[1]: return None
        return p[0] + (y - p[1]) / (q[1] - p[1]) * (q[0] - p[0])
    def box_hits_diag(bx0, by0, bx1, by1):
        for pl in DG:
            for p, q in zip(pl, pl[1:]):
                for k in range(21):                                       # sample the segment
                    x = p[0] + (q[0] - p[0]) * k / 20.0; y = p[1] + (q[1] - p[1]) * k / 20.0
                    if bx0 <= x <= bx1 and by0 <= y <= by1: return True
                for yy_ in (by0, by1):
                    x = segx(p, q, yy_)
                    if x is not None and bx0 <= x <= bx1: return True
        return False
    def place_zone_notes(gi, Q):
        if gi == 0 and CFG.get('ONE0'): EDGES = [CFG['ONE0'][0] - 50, CFG['ONE0'][1] + 50]
        elif gi == 0 and CFG.get('PIECES0'): EDGES = [v_ for ab in CFG['PIECES0'] if ab for v_ in ab]
        else: EDGES = [v_ for ab in PIECES for v_ in ab]
        VL = EDGES + CFG.get('VLINES', [])
        XLIM = CFG.get('XLIM', (-1e9, 1e9))
        def search(q, PT, low):
            t1 = q['l1'].replace('%%C', 'D'); w = max(1305 + 158 * (len(t1) - 6) - 52 * t1.count('1'), 1100)     # measured SPDS note widths (h 2.5, 1:100)
            cands = [(q['x0'], 'R')] + [(q['x0'] + 50 * k, 'R') for k in range(1, int((q['x1'] - q['x0']) / 50) + 61)] + [(q['x0'] - 40 - 10 * k, 'L') for k in range(0, 300)]
            best = None
            for ys, ye in sorted(q['bands'], key=lambda b: b != (q['ys'], q['ye'])):           # preferred storey first, then the others of the group
                ypref = ys + (0.0 if low else 0.55) * (ye - ys); pen = 0 if (ys, ye) == (q['ys'], q['ye']) else 400
                for ox, sd in cands:
                    tx0, tx1 = (ox + 40, ox + w) if sd == 'R' else (ox - w, ox)
                    if tx0 < XLIM[0] or tx1 > XLIM[1]: continue
                    sx0, sx1 = min(ox, q['x0']), max(ox, q['x1'])
                    for y in range(int(ys + 450), int(ye - 449), 50):
                        by0, by1 = y - 350, y + 350
                        if any(tx0 - 40 < x_ < tx1 + 40 and b0 < by1 and t0 > by0 and not (x_ == ox and sd == 'R') for x_, b0, t0 in VB): continue
                        if any(tx0 - 40 < x_ < tx1 + 40 for x_ in VL + AXR): continue
                        if box_hits_diag(tx0 - 50, by0 - 30, tx1 + 50, by1 + 30) or box_hits_diag(sx0, y - 5, sx1, y + 5): continue
                        if any(a0 < tx1 and tx0 < a1 and b0 < by1 and by0 < b1 for a0, b0, a1, b1 in CHB): continue          # lap chains
                        if any(a0 < sx1 and sx0 < a1 and b0 < y < b1 for a0, b0, a1, b1 in CHB): continue
                        bad = False
                        for (a0, b0, a1, b1, sy0, sy1, yy0) in PT:
                            if a0 < tx1 + 120 and tx0 - 120 < a1 and b0 < by1 + 120 and by0 - 120 < b1: bad = True; break     # text / text
                            if sy0 - 100 < tx1 and tx0 < sy1 + 100 and by0 - 120 < yy0 < by1 + 120: bad = True; break         # other shelf through my text
                            if sx0 - 100 < a1 and a0 < sx1 + 100 and b0 - 120 < y < b1 + 120: bad = True; break               # my shelf through other text
                        if bad: continue
                        ext = max(0, q['x0'] - sx0) + max(0, sx1 - q['x1'])
                        cr = sum(1 for x_ in AXR if sx0 < x_ < sx1) * 3000 + sum(1 for x_ in VL if sx0 + 1 < x_ < sx1 - 1) * 1500
                        cr += sum(800 for x_, b0, t0 in VB if sx0 + 5 < x_ < sx1 - 5 and b0 < y < t0 and x_ not in (q['x0'], q['x1']))
                        c = ext + cr + 0.3 * abs(y - ypref) + pen
                        if best is None or c < best[0]: best = (c, ox, sd, y, tx0, tx1, sx0, sx1)
            return best
        QS = sorted(Q, key=lambda q: (q['kind'] == 'M', q['x0'])); LOW = set()
        for attempt in range(3):
            PT0 = list(PT); res = []; fail = set()
            for q in QS:
                b_ = search(q, PT0, q['i'] in LOW)
                if b_ is None: fail.add(q['i']); continue
                c, ox, sd, y, tx0, tx1, sx0, sx1 = b_
                PT0.append((tx0, y - 350, tx1, y + 350, sx0, sx1, y)); res.append((q, b_))
            if not fail or fail <= LOW: break
            LOW |= fail
        PT[:] = PT0
        for q in QS:
            if q['i'] in fail and not any(r_[0] is q for r_ in res): print('NO PLACE', gi, q['i'], q['kind'], q['l1'])
        for q, (c, ox, sd, y, tx0, tx1, sx0, sx1) in res:
            note('S1N', q['l1'], q['l2'], [SX + AX1 + ox, SY + y], [[SX + AX1 + q['x0'], SY + y], [SX + AX1 + q['x1'], SY + y]])
            print('note', gi, q['i'], q['kind'], q['l1'], 'org', round(ox), sd, 'y', y, 'cost', round(c))
    for gi, (g0, g1) in enumerate(G):
        DX = 20 * (gi % 2)
        g1_ = g1
        for i in range(NP):
            g1 = TOP(i) if gi == len(G) - 1 else g1_
            yb, yt = L[g0], L[g1]
            for z in D[i][gi]:
                kind, x0, x1, d, st = z[:5]
                lpd = lap_at(i, gi - 1, kind) if gi > 0 else LAP(d)
                bA = yb; bB = yb + lpd + GAP(lpd)
                if gi < 3: lp = lap_at(i, gi, kind); tA = yt + lp; tB = yt + 2 * lp + GAP(lp)
                else: tA = tB = yt - TOPC
                LA = int(round(tA - bA, -1)); LB = int(round(tB - bB, -1))
                pA = pos_of((d, LA))
                pB = pos_of((d, LB))
                nb = len(z[5])
                BARS.append(dict(pos=pA, d=d, L=LA, n=2 * ((nb + 1) // 2)))
                BARS.append(dict(pos=pB, d=d, L=LB, n=2 * (nb // 2)))
                lay = 'диам%d' % d
                ops.append(dict(t='pl', p=[W(AX1 + x0 + DX, bA), W(AX1 + x0 + DX, tA)], layer=lay, lw=40))
                ops.append(dict(t='pl', p=[W(AX1 + x1 + DX, bB), W(AX1 + x1 + DX, tB)], layer=lay, lw=40))
                VB.append((x0 + DX, bA, tA)); VB.append((x1 + DX, bB, tB))
                # note in the upper storey of the group (analog), texts right of the zone
                low = i in CFG.get('NOTE_LOW', [])          # shares the opening with the previous piece's notes: lower storey / lower half
                ys = L[g0] if (low and g1 - g0 > 1) else L[g1 - 1]; ye = (L[g0 + 1] if (low and g1 - g0 > 1) else L[g1]) - SLAB
                if ZM and ye - ys < 2400 and g1 - g0 > 1: ys, ye = L[g1 - 2], L[g1 - 1] - SLAB      # short top storey: notes one storey lower
                if low and g1 - g0 == 1: ye = (ys + ye) / 2 - 100
                ks = [z[0] for z in D[i][gi]]; n_ = len(ks)
                side = CFG['NOTE_SIDE'][i] if CFG.get('NOTE_SIDE') else ('R' if ENDS[i][1] else 'L')
                if side == 'R':
                    ox = AX1 + PIECES[i][1] + ((2050 if n_ == 3 else (1800 if CFG.get('CHAIN_SIDE', 'L' * NP)[i] == 'R' else 1500)) if CFG.get('OPEN_R', [True] * NP)[i] else 450)
                    dg = DIAG.get((round(AX1 + PIECES[i][1]), round(ys)))
                    if dg: (mx, my), (ex, ey) = dg; U = my + (ox - mx) / (ex - mx) * (ey - my) - 420
                    else: U = ye - 450
                else:
                    ox = AX1 + PIECES[i][0] - 900                  # text to the left of the origin (align Right): shelf away from the leaders
                    dg = DIAGE.get((round(AX1 + PIECES[i][0]), round(ye)))
                    xl = ox - 1300
                    if dg: (sx_, sy_), (mx, my) = dg; U = my + (xl - mx) / (AX1 + PIECES[i][0] - mx) * (ye - my) - 420 if xl > mx else my - 420
                    else: U = ye - 450
                Lo = ys + 400
                if g1 - g0 == 1 and CFG.get('NOTE_LOW') and not low and (i + 1) in CFG.get('NOTE_LOW', []): Lo = min((ys + ye) / 2 + 800, U - (n_ - 1) * 800)
                sp_ = max(800, min(1000, (U - Lo) / max(1, n_ - 1))) if n_ > 1 else 0
                top = max(U, Lo + (n_ - 1) * sp_)
                ym = (top - ks.index(kind) * sp_) if n_ > 1 else (U + Lo) / 2
                lab = ('%d' % pA) if pA == pB else ('%d;%d' % (pA, pB)); LABELS['%d|%d|%s' % (i, gi, kind)] = lab
                if AN:
                    src = ANN.get((i, g1 - 1)) or ANN.get((i, g0))
                    if src:
                        n0 = src[0]; k_ = ks.index(kind)
                        sb = next((L[s_] for s_ in range(len(L) - 1) if L[s_] <= n0['pts'][0][1] < L[s_ + 1]), ys); se = next((L[s_ + 1] for s_ in range(len(L) - 1) if L[s_] <= n0['pts'][0][1] < L[s_ + 1]), ye) - SLAB
                        ys_ = [n0['pts'][0][1] + 950 * ((n_ - 1) / 2.0 - j) for j in range(n_)]       # stack centred on the analog note, inside its storey
                        sh = max(0, sb + 450 - min(ys_)) - max(0, max(ys_) - (se - 450))
                        oy = ys_[k_] + sh
                        h_ = n0['h']
                        if k_:
                            h_ = 'WVa%d_%d_%d_%d' % (SX, i, gi, k_); ops.append(dict(t='clone', h=n0['h'], base=[0, 0], to=[0, 0], tag=h_))
                        ops.append(dict(t='spmove', h=h_, items=[[0, SX + n0['pts'][0][0], SY + oy], [1, SX + AX1 + x0 + DX, SY + oy], [2, SX + AX1 + x1 + DX, SY + oy]]))
                        ops.append(dict(t='mcset', h=h_, set={'FirstLine': '%s(%%%%C%d)' % (lab, d), 'SecondLine': 'ш.%d' % st}))
                elif ZM:
                    ZQ.append(dict(i=i, kind=kind, x0=x0 + DX, x1=x1 + DX, l1='%s(%%%%C%d)' % (lab, d), l2='ш.%d' % st, ys=ys, ye=ye,
                                   bands=[(L[s_], L[s_ + 1] - SLAB) for s_ in range(g0, g1)]))
                else:
                    note('S1N', '%s(%%%%C%d)' % (lab, d), 'ш.%d' % st, [SX + ox, SY + ym], [[SX + AX1 + x0 + DX, SY + ym], [SX + AX1 + x1 + DX, SY + ym]])
            if ZM and i == NP - 1:
                place_zone_notes(gi, ZQ); ZQ.clear()
            if gi < 3 and i not in CFG.get('CHAIN_SKIP', []):      # laps are the same in every piece (one Ø per group): one chain per opening
                lp = max(lap_at(i, gi, z[0]) for z in (D[i][gi] or D[0][gi])); gp = GAP(lp)
                xa = AX1 + min(z[1] for z in D[i][0]) + DX if D[i][0] else None; xd = AX1 + CFG['CHAIN_X'][i] - CFG.get('CHAIN_OFF_L', [350] * NP)[i]
                if ZM or xa is None:                      # extension lines from the piece's bars that start at this splice
                    csd_ = CFG.get('CHAIN_SIDE', 'L' * NP)[i]; DX1 = 20 * ((gi + 1) % 2)
                    xa = AX1 + DX1 + (min(z[1] for z in D[i][gi + 1]) if csd_ == 'L' else max(z[2] for z in D[i][gi + 1]))
                    if csd_ == 'R': xd = AX1 + PIECES[i][1] + CFG.get('CHAIN_OFF_R', [350] * NP)[i]
                csd = CFG.get('CHAIN_SIDE', 'L' * NP)[i]
                if AN and i in NSIDE:
                    csd = 'R' if NSIDE[i] == 'L' else 'L'
                    if i in CFG.get('CHAIN_SAME', []): csd = NSIDE[i]      # only free side holds the notes: same side, other storey (analog)
                    if CFG.get('CHAIN_FORCE'): csd = CFG['CHAIN_FORCE'][i]
                    xa = AX1 + (max(z[2] for z in D[i][0]) if csd == 'R' else min(z[1] for z in D[i][0])) + DX
                    xd = AX1 + (PIECES[i][1] + CFG.get('CHAIN_OFF_R', [350] * NP)[i] if csd == 'R' else PIECES[i][0] - 350)
                yy = [yt, yt + lp, yt + lp + gp, yt + 2 * lp + gp]
                CHB.append((xd - AX1 - 750, yt, xd - AX1 + 60, yy[3] + 100) if csd == 'L' else (xd - AX1 - 60, yt, xd - AX1 + 750, yy[3] + 100))
                for kk in range(3):
                    kw = dict(t='dim', h='WT_DV', p1=W(xa, yy[kk]), p2=W(xa, yy[kk + 1]), dl=W(xd, (yy[kk] + yy[kk + 1]) / 2), rot=math.pi / 2, txt='')
                    ym_ = (yy[kk] + yy[kk + 1]) / 2
                    band = 950 if CFG['CHAIN_DIAG'][i] else 350                      # left of pieces 2-4 the opening diagonal comes down to the slab
                    for sl in L:                                  # text never on a slab / the diagonal: slide it along the line
                        if sl - SLAB - band < ym_ < sl + 350:
                            below = sl - SLAB - band - 50
                            ym_ = below if below - 450 > yy[kk] else sl + 450   # below the slab first (the storey above holds notes)
                    sg = 1 if csd == 'R' else -1      # texts on the outer side of the chain
                    if kk == 1: kw['tx'] = W(xd + sg * (260 if sg < 0 else 540), ym_)
                    elif ym_ != (yy[kk] + yy[kk + 1]) / 2:
                        nxt = min([sl for sl in L if sl > yy[kk]] or [L[-1]])
                        if CFG['CHAIN_DIAG'][i] and ym_ > nxt and nxt - SLAB - yy[kk] > 870:   # the storey above holds the next piece's notes: inside, between chain and wall
                            kw['tx'] = W(xd - sg * 175, (yy[kk] + nxt - SLAB) / 2 + 25)
                        else: kw['tx'] = W(xd + sg * 130, ym_)
                    ops.append(kw)
    # П caps Ск at the wall top: vertical legs at the zone extremes (Ø = top bar Ø), one note per piece
    CAPS = {}
    for i in range(NP):
        tg = []; nums = []
        for z in D[i][3]:
            kind, x0, x1, d, st = z[:5]
            if d not in CAPS: CAPS[d] = len(CAPS) + 1 + CFG.get('CK0', 0)
            yt = L[TOP(i)] - TOPC; leg = LAP(d)
            for x in (x0 - 20, x1 + 20):                                   # analog: legs 20 outside the zone's end bars
                ops.append(dict(t='pl', p=[W(AX1 + x, yt), W(AX1 + x, yt - leg)], layer='диам%d' % d, lw=40))
            tg += [AX1 + x0 - 20, AX1 + x1 + 20]; nums.append(CAPS[d])
            BARS.append(dict(pos='Ск%d' % CAPS[d], d=d, L=2 * leg + 170, n=len(z[5])))
        ox = AX1 + PIECES[i][0] + (-300 if ENDS[i][0] else 400)
        LT = L[TOP(i)]
        yy = SY + LT - SLAB - 80          # analog Ск note: two leaders, to the outermost legs of the piece
        lab_c = 'Ск' + ';'.join(str(n) for n in sorted(set(nums)))
        if CFG.get('CK_SPLIT') and PIECES[i][1] - PIECES[i][0] > CFG['CK_SPLIT'] and len(tg) >= 4:      # wide piece: one Ск note at each end, to its two nearest legs
            lg = sorted(tg)
            note('S1C', lab_c, '', [SX + AX1 + PIECES[i][0] + 400, SY + LT + 450], [[SX + lg[0], yy], [SX + lg[2], yy]])
            note('S1C', lab_c, '', [SX + AX1 + PIECES[i][1] - 1500, SY + LT + 450], [[SX + lg[-3], yy], [SX + lg[-1], yy]])
        elif AN and ANN.get((i, 'C')):
            n0 = ANN[(i, 'C')][0]
            ops.append(dict(t='spmove', h=n0['h'], items=[[1, SX + min(tg), yy], [2, SX + max(tg), yy]]))
            ops.append(dict(t='mcset', h=n0['h'], set={'FirstLine': lab_c, 'SecondLine': ''}))
        else:
            note('S1C', lab_c, '', [SX + ox, SY + LT + 450], [[SX + min(tg), yy], [SX + max(tg), yy]])
    # bottom chain (basement): 50 | 100x4 | steps (leftover in the middle) | 100x4 | 50 — as in the analog;
    # texts: inside when they fit, else beside (outward, off the axes); rows chosen greedily so that no two texts overlap
    AXES = CFG['AXES']; CW = 140; TGAP = 120; RY = [L[0] - 1813, L[0] - 2313, L[0] - 2813]
    items = []
    for i in range(NP):
        if CFG.get('ONE0'):
            if i: continue
            a, b = CFG['ONE0']
        else: a, b = (CFG.get('PIECES0') or PIECES)[i] or (None, None)
        if a is None: continue
        segs = [(a, a + 50, 50, 1)] + [sg for z in D[i][0] for sg in z[6]] + [(b - 50, b, 50, 1)]
        for k_, (s0, s1, st, n_) in enumerate(segs):
            txt = ('%dх%d' % (st, n_)) if n_ > 1 else ''
            w = CW * max(len(txt), len(str(int(round(s1 - s0))))) + 100
            if s1 - s0 >= w: cx, moved = AX1 + (s0 + s1) / 2, False
            else:
                out = (s0 + s1) / 2 > (a + b) / 2
                cx = AX1 + (s1 + w / 2 + 30 if out else s0 - w / 2 - 30); moved = True
                for ax_ in AXES:
                    if abs(cx - ax_) < w / 2 + 40: cx = ax_ + (w / 2 + 60) * (1 if cx >= ax_ else -1)
            items.append([cx, w, s0, s1, txt, moved])
    rows = [[] for _ in RY]
    for it in sorted(items, key=lambda t: t[0]):
        cx, w = it[0], it[1]
        r = next((j for j in range(len(RY)) if all(cx + w / 2 + TGAP < c - ww / 2 or cx - w / 2 - TGAP > c + ww / 2 for c, ww in rows[j])), None)
        if r is None:
            r = min(range(len(RY)), key=lambda j: max(c + ww / 2 for c, ww in rows[j]))
            cx = max(c + ww / 2 for c, ww in rows[r]) + TGAP + w / 2; it[5] = True
        rows[r].append((cx, w))
        cx0, w, s0, s1, txt, moved = it
        ty = RY[r]
        kw = dict(t='dim', h='WT_DH', p1=W(AX1 + s0, L[0]), p2=W(AX1 + s1, L[0]), dl=W(AX1 + (s0 + s1) / 2, ty), rot=0, txt=txt)
        if moved or cx != cx0: kw['tx'] = W(cx, ty + 60)
        ops.append(kw)
    ops += [dict(t='erase', h=['S1N', 'S1C']), dict(t='save')]
    json.dump(dict(LABELS=LABELS, D=D, POS={'|'.join(map(str, kk)): vv for kk, vv in POS.items()}, BARS=BARS, CAPS=CAPS), open(CFG['OUT'], 'w', encoding='utf-8'), ensure_ascii=False)
    print('erase', len(er), 'ops', len(ops), 'positions', len(POS))
    for i in range(NP):
        for g in range(4): print('P%d G%d' % (i + 1, g), [(z[0], z[3], z[4], len(z[5]), z[1], z[2]) for z in D[i][g]])
    if go:
        out = gx.run(ops, 'wv')
        print([l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'fail' in l][-8:])
if __name__ == '__main__':
    run('--run' in sys.argv)
