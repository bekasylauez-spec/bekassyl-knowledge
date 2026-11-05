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
G = [(0, 1), (1, 3), (3, 5), (5, 7)]                      # storey index ranges of the groups
SLAB = 250.0; EDGE = 450.0; TOPC = 30.0
PIECES = CFG['PIECES']; LIRA = CFG['LIRA']; ENDS = CFG['ENDS']; NP = len(PIECES)
LAP = lambda d: int(math.ceil(61 * d / 10.0) * 10)
GAP = lambda lap: int(round(0.3 * lap, -1))
A = lambda d: math.pi * d * d / 400
DS = [12, 14, 16, 18, 20, 22, 25, 28]
CELLS = [c for c in json.load(open('arm/wall_cells.json')) if c['pl'] == CFG['PLANE']]
KX = ('x0', 'x1') if CFG['PLANE'][0] == 'y' else ('y0', 'y1')
LEV = [-4.65, -0.1, 3.95, 7.1, 10.25, 13.4, 16.55, 19.7]
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
REQ = []
for i, ((a, b), (la, lb), (el, er)) in enumerate(zip(PIECES, LIRA, CFG.get('LENDS', ENDS))):     # LENDS: free ends as seen in the LIRA cells (mirrored pieces)
    row = []
    for g0, g1 in G:
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
    de = max([x for i in range(NP) for x in REQ[i][g][:2] if x] or [12])
    dm, sm = max([REQ[i][g][2:] for i in range(NP)], key=lambda t: (A(t[0]) * 1000 / t[1], -t[1]))
    for i, ((a, b), (el, er)) in enumerate(zip(PIECES, ENDS)): D[i][g] = make_zones(a, b, el, er, de, de, dm, sm)
def run(go=False):
    R = listwin(SX, SY, 59400, 42000, None)
    N = notes(SX, SY, 59400, 42000)
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
                    st_ = next((s_ for s_ in range(7) if L[s_] <= cy < L[s_ + 1]), 7)
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
        for z in D[i][g]:
            if z[0] == kind: return z
    def lap_at(i, g, kind):              # lap at the top splice of group g
        d = zone(i, g, kind)[3]; dn = zone(i, g + 1, kind)[3]
        return LAP(max(d, dn))
    CH = []
    for gi, (g0, g1) in enumerate(G):
        yb, yt = L[g0], L[g1]
        DX = 20 * (gi % 2)
        for i in range(NP):
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
                # note in the upper storey of the group (analog), texts right of the zone
                low = i in CFG.get('NOTE_LOW', [])          # shares the opening with the previous piece's notes: lower storey / lower half
                ys = L[g0] if (low and g1 - g0 > 1) else L[g1 - 1]; ye = (L[g0 + 1] if (low and g1 - g0 > 1) else L[g1]) - SLAB
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
                        sb = next((L[s_] for s_ in range(7) if L[s_] <= n0['pts'][0][1] < L[s_ + 1]), ys); se = next((L[s_ + 1] for s_ in range(7) if L[s_] <= n0['pts'][0][1] < L[s_ + 1]), ye) - SLAB
                        ys_ = [n0['pts'][0][1] + 950 * ((n_ - 1) / 2.0 - j) for j in range(n_)]       # stack centred on the analog note, inside its storey
                        sh = max(0, sb + 450 - min(ys_)) - max(0, max(ys_) - (se - 450))
                        oy = ys_[k_] + sh
                        h_ = n0['h']
                        if k_:
                            h_ = 'WVa%d_%d_%d_%d' % (SX, i, gi, k_); ops.append(dict(t='clone', h=n0['h'], base=[0, 0], to=[0, 0], tag=h_))
                        ops.append(dict(t='spmove', h=h_, items=[[0, SX + n0['pts'][0][0], SY + oy], [1, SX + AX1 + x0 + DX, SY + oy], [2, SX + AX1 + x1 + DX, SY + oy]]))
                        ops.append(dict(t='mcset', h=h_, set={'FirstLine': '%s(%%%%C%d)' % (lab, d), 'SecondLine': 'ш.%d' % st}))
                else:
                    note('S1N', '%s(%%%%C%d)' % (lab, d), 'ш.%d' % st, [SX + ox, SY + ym], [[SX + AX1 + x0 + DX, SY + ym], [SX + AX1 + x1 + DX, SY + ym]])
            if gi < 3 and i not in CFG.get('CHAIN_SKIP', []):      # laps are the same in every piece (one Ø per group): one chain per opening
                lp = max(lap_at(i, gi, z[0]) for z in D[i][gi]); gp = GAP(lp)
                xa = AX1 + min(z[1] for z in D[i][0]) + DX; xd = AX1 + CFG['CHAIN_X'][i] - 350
                csd = CFG.get('CHAIN_SIDE', 'L' * NP)[i]
                if AN and i in NSIDE:
                    csd = 'R' if NSIDE[i] == 'L' else 'L'
                    if i in CFG.get('CHAIN_SAME', []): csd = NSIDE[i]      # only free side holds the notes: same side, other storey (analog)
                    if CFG.get('CHAIN_FORCE'): csd = CFG['CHAIN_FORCE'][i]
                    xa = AX1 + (max(z[2] for z in D[i][0]) if csd == 'R' else min(z[1] for z in D[i][0])) + DX
                    xd = AX1 + (PIECES[i][1] + CFG.get('CHAIN_OFF_R', [350] * NP)[i] if csd == 'R' else PIECES[i][0] - 350)
                yy = [yt, yt + lp, yt + lp + gp, yt + 2 * lp + gp]
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
            yt = L[7] - TOPC; leg = LAP(d)
            for x in (x0 - 20, x1 + 20):                                   # analog: legs 20 outside the zone's end bars
                ops.append(dict(t='pl', p=[W(AX1 + x, yt), W(AX1 + x, yt - leg)], layer='диам%d' % d, lw=40))
            tg += [AX1 + x0 - 20, AX1 + x1 + 20]; nums.append(CAPS[d])
            BARS.append(dict(pos='Ск%d' % CAPS[d], d=d, L=2 * leg + 170, n=len(z[5])))
        ox = AX1 + PIECES[i][0] + (-300 if ENDS[i][0] else 400)
        yy = SY + L[7] - SLAB - 80          # analog Ск note: two leaders, to the outermost legs of the piece
        lab_c = 'Ск' + ';'.join(str(n) for n in sorted(set(nums)))
        if AN and ANN.get((i, 'C')):
            n0 = ANN[(i, 'C')][0]
            ops.append(dict(t='spmove', h=n0['h'], items=[[1, SX + min(tg), yy], [2, SX + max(tg), yy]]))
            ops.append(dict(t='mcset', h=n0['h'], set={'FirstLine': lab_c, 'SecondLine': ''}))
        else:
            note('S1C', lab_c, '', [SX + ox, SY + L[7] + 450], [[SX + min(tg), yy], [SX + max(tg), yy]])
    # bottom chain (basement): 50 | 100x4 | steps (leftover in the middle) | 100x4 | 50 — as in the analog;
    # texts: inside when they fit, else beside (outward, off the axes); rows chosen greedily so that no two texts overlap
    AXES = CFG['AXES']; CW = 140; TGAP = 120; RY = [L[0] - 1813, L[0] - 2313, L[0] - 2813]
    items = []
    for i in range(NP):
        a, b = PIECES[i]
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
    json.dump(dict(LABELS=LABELS, D=D, POS={'|'.join(map(str, kk)): vv for kk, vv in POS.items()}, BARS=BARS, CAPS=CAPS), open(CFG['OUT'], 'w'), ensure_ascii=False)
    print('erase', len(er), 'ops', len(ops), 'positions', len(POS))
    for i in range(NP):
        for g in range(4): print('P%d G%d' % (i + 1, g), [(z[0], z[3], z[4], len(z[5]), z[1], z[2]) for z in D[i][g]])
    if go:
        out = gx.run(ops, 'wv')
        print([l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'fail' in l][-8:])
if __name__ == '__main__':
    run('--run' in sys.argv)
