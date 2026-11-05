# См-1 sheet 5.2 (analog 4.2 reworked): reinforcement layer redrawn in the analog's grammar with the analog's own objects
#  * groups of storeys as in the analog: G0 = -4.650..-0.100, G1 = -0.100..+7.100, G2 = +7.100..+13.400, G3 = +13.400..+19.700
#    (bars span a group, splices only at -0.100 / +7.100 / +13.400, staggered A;B, lap 61d of the larger Ø, gap 0.3L)
#  * zones per piece: free-end edge zone 450 ш.100 (Ø by the LIRA edge peak), middle ш.200 Ø12-16 (else ш.100)
#  * each zone drawn by its two extreme bars (A left, B right), the upper group 20 mm to the right; notes cloned from the analog note
import sys, os, json, math; sys.path.insert(0, 'wl'); from common import *
from notes import notes
SX, SY = 889400.0, 455939.0
def W(x, y): return [SX + x, SY + y]
AX1 = 9810.0
L = [15147, 19697, 23747, 26897, 30047, 33197, 36347, 39497]
G = [(0, 1), (1, 3), (3, 5), (5, 7)]                      # storey index ranges of the groups
SLAB = 250.0; EDGE = 450.0; TOPC = 30.0
PIECES = [(125, 1225), (5875, 7725), (12325, 14175), (18825, 19925)]   # scheme x (axis 1 = 0)
LIRA = [(0, 1225), (5875, 7725), (12325, 14175), (18825, 20050)]
ENDS = [(False, True), (True, True), (True, True), (True, False)]
LAP = lambda d: int(math.ceil(61 * d / 10.0) * 10)
GAP = lambda lap: int(round(0.3 * lap, -1))
A = lambda d: math.pi * d * d / 400
DS = [12, 14, 16, 18, 20, 22, 25, 28]
CELLS = [c for c in json.load(open('arm/wall_cells.json')) if c['pl'] == ['y', 0]]
LEV = [-4.65, -0.1, 3.95, 7.1, 10.25, 13.4, 16.55, 19.7]
v = lambda c: max(c['As'][2], c['As'][3])

def design():
    """D[i][g] = list of zones (kind, x0, x1, d, step) in scheme x"""
    D = []
    for i, ((a, b), (la, lb), (el, er)) in enumerate(zip(PIECES, LIRA, ENDS)):
        row = []
        for g0, g1 in G:
            cs = [c for c in CELLS if LEV[g0] - 1e-3 <= c['z0'] < LEV[g1] - 1e-3 and c['x1'] > la + 1 and c['x0'] < lb - 1]
            xs = sorted(set(c['x0'] for c in cs))
            colL = [c for c in cs if c['x0'] == xs[0]]; colR = [c for c in cs if c['x0'] == xs[-1]]
            mid = [c for c in cs if (not el or c['x0'] != xs[0]) and (not er or c['x0'] != xs[-1])]
            zs = []; lo, hi = a + 50, b - 50
            if el:
                req = max(v(c) for c in colL); d = next(d for d in DS if A(d) * 10 >= req - 1e-6)
                zs.append(('L', a + 50, a + EDGE, d, 100)); lo = a + EDGE + 100
            if er:
                req = max(v(c) for c in colR); d = next(d for d in DS if A(d) * 10 >= req - 1e-6)
                zs.append(('R', b - EDGE, b - 50, d, 100)); hi = b - EDGE - 100
            req = max([v(c) for c in mid] + [0])
            md, ms = next((d, s) for d, s in ((12, 200), (14, 200), (16, 200), (12, 100), (14, 100), (16, 100), (18, 100), (20, 100), (22, 100), (25, 100)) if A(d) * 1000 / s >= req - 1e-6)
            n = max(1, int(round((hi - lo) / ms)))
            zs.insert(1 if el else 0, ('M', lo, lo + n * ms, md, ms))
            row.append(zs)
        D.append(row)
    return D
D = design()
# P1 and P4 mirror each other: one design (max Ø), as in the analog (same positions)
for g in range(4):
    zr = {z[0]: z for z in D[0][g]}; zl = {z[0]: z for z in D[3][g]}
    dR = max(zr['R'][3], zl['L'][3]); dM = max(zr['M'][3], zl['M'][3]); sM = min(zr['M'][4], zl['M'][4])
    D[0][g] = [('M',) + zr['M'][1:3] + (dM, sM), ('R',) + zr['R'][1:3] + (dR, 100)]
    D[3][g] = [('L',) + zl['L'][1:3] + (dR, 100), ('M',) + zl['M'][1:3] + (dM, sM)]

def run(go=False):
    R = listwin(SX, SY, 59400, 42000, None)
    N = notes(SX, SY, 59400, 42000)
    tN = next(n['h'] for n in N if n['l2'].startswith('ш.') and len(n['pts']) == 3)
    tC = next((n['h'] for n in N if n['l1'].startswith('Ск') and len(n['pts']) == 3), tN)
    EL = lambda r: 9000 < r['x0'] and r['x1'] < 31500 and r['y0'] > 11500
    er = [r['h'] for r in R if r['t'] in ('LINE', 'LWPOLYLINE') and EL(r) and r['lay'].lower().startswith('диам')]
    er += [r['h'] for r in R if r['t'] == 'DIMENSION' and EL(r) and not (r['sp'][0][1] < 13200 and r['sp'][1][1] < 13200)]
    er += [r['h'] for r in R if r['t'] == 'DIMENSION' and r['y0'] > 14000 and len(r['sp']) > 2 and r['sp'][2][0] > 8500 and r['x1'] < 31800 and r['h'] not in er]
    er += [n['h'] for n in N if 7500 < n['pts'][0][0] < 33000 and n['pts'][0][1] > 13500]
    DIAG = {(round(r['sp'][0][0]), round(r['sp'][0][1])): (r['sp'][1], r['sp'][2]) for r in R if r['t'] == 'LWPOLYLINE' and len(r['sp']) == 3 and r['y0'] > 14000}
    ops = [dict(t='clone', h=tN, base=[0, 0], to=[0, -200000], tag='S1N'), dict(t='clone', h=tC, base=[0, 0], to=[0, -200000], tag='S1C'),
           dict(t='erase', h=er)]
    POS = {}; BARS = []; k = [0]
    def pos_of(key):
        if key not in POS: POS[key] = len(POS) + 1
        return POS[key]
    def note(tpl, l1, l2, org, tg):          # same style as the analog notes (ГОСТ 2.304, 2.5, ticks); new object so the shelf faces away from the leaders
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
        for i in range(4):
            base0 = {z[0]: (z[1], z[2]) for z in D[i][0]}
            for kind, x0, x1, d, st in D[i][gi]:
                x0, x1 = base0[kind]                      # bar positions as they start in the basement
                lpd = lap_at(i, gi - 1, kind) if gi > 0 else LAP(d)
                bA = yb; bB = yb + lpd + GAP(lpd)
                if gi < 3: lp = lap_at(i, gi, kind); tA = yt + lp; tB = yt + 2 * lp + GAP(lp)
                else: tA = tB = yt - TOPC
                LA = int(round(tA - bA, -1)); LB = int(round(tB - bB, -1))
                pA = pos_of((d, LA))
                pB = pos_of((d, LB))
                nb = int(round((x1 - x0) / st)) + 1
                BARS.append(dict(pos=pA, d=d, L=LA, n=2 * ((nb + 1) // 2)))
                BARS.append(dict(pos=pB, d=d, L=LB, n=2 * (nb // 2)))
                lay = 'диам%d' % d
                ops.append(dict(t='pl', p=[W(AX1 + x0 + DX, bA), W(AX1 + x0 + DX, tA)], layer=lay, lw=40))
                ops.append(dict(t='pl', p=[W(AX1 + x1 + DX, bB), W(AX1 + x1 + DX, tB)], layer=lay, lw=40))
                # note in the upper storey of the group (analog), texts right of the zone
                ys = L[g1 - 1]; ye = L[g1] - SLAB
                ks = [z[0] for z in D[i][gi]]
                ox = AX1 + PIECES[i][1] + ((2050 if len(ks) == 3 else 1500) if i < 3 else 450)
                dg = DIAG.get((round(AX1 + PIECES[i][1]), round(ys)))
                if dg: (mx, my), (ex, ey) = dg; U = my + (ox - mx) / (ex - mx) * (ey - my) - 420
                else: U = ye - 450
                Lo = ys + 400; n_ = len(ks)
                sp_ = max(800, min(1000, (U - Lo) / max(1, n_ - 1))) if n_ > 1 else 0
                top = max(U, Lo + (n_ - 1) * sp_)
                ym = (top - ks.index(kind) * sp_) if n_ > 1 else (U + Lo) / 2
                lab = ('%d' % pA) if pA == pB else ('%d;%d' % (pA, pB))
                note('S1N', '%s(%%%%C%d)' % (lab, d), 'ш.%d' % st, [SX + ox, SY + ym], [[SX + AX1 + x0 + DX, SY + ym], [SX + AX1 + x1 + DX, SY + ym]])
            if gi < 3:
                lp = max(lap_at(i, gi, z[0]) for z in D[i][gi]); gp = GAP(lp)
                xa = AX1 + min(z[1] for z in D[i][0]) + DX; xd = AX1 + (PIECES[i][0] if i else -125) - 350
                yy = [yt, yt + lp, yt + lp + gp, yt + 2 * lp + gp]
                for kk in range(3):
                    kw = dict(t='dim', h='WT_DV', p1=W(xa, yy[kk]), p2=W(xa, yy[kk + 1]), dl=W(xd, (yy[kk] + yy[kk + 1]) / 2), rot=math.pi / 2, txt='')
                    ym_ = (yy[kk] + yy[kk + 1]) / 2
                    for sl in L:                                  # text never on a slab: slide it along the line
                        if sl - SLAB - 350 < ym_ < sl + 350: ym_ = sl + 400 if yy[kk + 1] - sl > sl - SLAB - yy[kk] else sl - SLAB - 400
                    if kk == 1: kw['tx'] = W(xd - 260, ym_)
                    elif ym_ != (yy[kk] + yy[kk + 1]) / 2: kw['tx'] = W(xd - 130, ym_)
                    ops.append(kw)
    # П caps Ск at the wall top: vertical legs at the zone extremes (Ø = top bar Ø), one note per piece
    CAPS = {}
    for i in range(4):
        tg = []; nums = []
        for kind, x0, x1, d, st in D[i][3]:
            if d not in CAPS: CAPS[d] = len(CAPS) + 1
            yt = L[7] - TOPC; leg = LAP(d)
            for x in (x0, x1):
                ops.append(dict(t='pl', p=[W(AX1 + x + 20, yt), W(AX1 + x + 20, yt - leg)], layer='диам%d' % d, lw=40))
            tg += [AX1 + x0 + 20, AX1 + x1 + 20]; nums.append(CAPS[d])
            BARS.append(dict(pos='Ск%d' % CAPS[d], d=d, L=2 * leg + 170, n=int(round((x1 - x0) / st)) + 1))
        ox = AX1 + PIECES[i][0] + (400 if i in (0, 3) else -300)
        yy = SY + L[7] - SLAB - 80          # analog Ск note: two leaders, to the outermost legs of the piece
        note('S1C', 'Ск' + ';'.join(str(n) for n in sorted(set(nums))), '', [SX + ox, SY + L[7] + 450], [[SX + min(tg), yy], [SX + max(tg), yy]])
    # bottom chain: bar positions in the basement
    AXES = [9810, 16610, 23060, 29860]
    for i in range(4):
        for kind, x0, x1, d, st in D[i][0]:
            n_ = round((x1 - x0) / st); txt = ('%dх%d' % (st, n_)) if n_ > 1 else ''
            tw = 110 * len(txt) / 2 + 150
            tx = AX1 + (x0 + x1) / 2
            if kind == 'L': tx = AX1 + x0 - tw
            if kind == 'R': tx = AX1 + x1 + tw
            if kind == 'M':
                for c in (AX1 + (x0 + x1) / 2, AX1 + x1 + tw, AX1 + x0 - tw):
                    fits = c != AX1 + (x0 + x1) / 2 or (x1 - x0) > 2 * tw
                    if fits and not any(abs(c - a) < tw - 100 for a in AXES): tx = c; break
            ty = 13334 if kind != 'M' else 12634
            ops.append(dict(t='dim', h='WT_DH', p1=W(AX1 + x0, L[0]), p2=W(AX1 + x1, L[0]), dl=W(AX1 + (x0 + x1) / 2, ty), rot=0, txt=txt, tx=W(tx, ty + 60)))
    ops += [dict(t='erase', h=['S1N', 'S1C']), dict(t='dimtx', h='13FA81', at=W(5461, 28700)), dict(t='save')]
    json.dump(dict(D=D, POS={'|'.join(map(str, kk)): vv for kk, vv in POS.items()}, BARS=BARS, CAPS=CAPS), open('wl/sm1_vert.json', 'w'), ensure_ascii=False)
    print('erase', len(er), 'ops', len(ops), 'positions', len(POS))
    for i in range(4):
        for g in range(4): print('P%d G%d' % (i + 1, g), [(z[0], z[3], z[4]) for z in D[i][g]])
    if go:
        out = gx.run(ops, 'sm1v')
        print([l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'fail' in l][-8:])
if __name__ == '__main__':
    run('--run' in sys.argv)
