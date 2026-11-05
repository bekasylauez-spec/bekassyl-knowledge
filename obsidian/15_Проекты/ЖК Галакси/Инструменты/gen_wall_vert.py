# Wall См-1 — sheet 5.2 «Вертикальное армирование» (v2, by analog 4.1 См-1 Тип С):
#  * each zone is drawn by its two extreme bars only: left extreme = group A, right extreme = group B (2 positions «pA;pB»)
#  * laps staggered: A lap starts at the slab top, B lap starts 0.3·lap above the end of A lap (analog 730/220/730)
#  * odd storeys drawn 20 mm to the right (lap reads on the drawing); x positions as they start in the basement
#  * П caps Ск at the wall top wrap the wall thickness -> in elevation a vertical leg (L = lap) at each extreme bar
#  * note per zone only where the positions change (analog: 2;3 / 4;5 / 6;7)
import json, math, sys
import gx, colsheet as C
sys.path.insert(0, 'arm'); import wall_zones as WZ

SX, SY = 889400.0, 455939.0
def W(x, y): return [SX + x, SY + y]
AX1 = 9810.0
L = [15147, 19697, 23747, 26897, 30047, 33197, 36347, 39497]
SLAB = 250.0
PIECES = [(125, 1225), (5875, 7725), (12325, 14175), (18825, 19925)]
ENDS = [(False, True), (True, True), (True, True), (True, False)]
LIRA = [(0, 1225), (5875, 7725), (12325, 14175), (18825, 20050)]
D = WZ.design('y', 0, LIRA, ENDS)
EDGE = 450.0
LAP = lambda d: int(math.ceil(61 * d / 10.0) * 10)
GAP = lambda lap: int(round(0.3 * lap, -1))
TOPC = 30.0                                            # bar end below the wall top

ops = []
def add(**k): ops.append(k); return k
R = C.listwin(SX, SY, 59400, 42000)
EL = lambda r: 9000 < r['x0'] < 31500 and r['y0'] > 13000
er = [r['h'] for r in R if r['t'] in ('LINE', 'LWPOLYLINE') and EL(r) and r['lay'].lower().startswith('диам')]   # analog bars + all earlier runs
er += [r['h'] for r in R if r['t'] == 'SPDSNOTEPOSITION' and r['y0'] > 14800 and r['x0'] < 40000]
m_ = gx.tagmap(); TPLH = {m_['WT_DH'].upper(), m_['WT_DV'].upper()}
er += [r['h'] for r in R if r['t'] == 'DIMENSION' and r['x0'] > 7400 and r['y1'] > 12500 and r['h'].upper() not in TPLH]
TDIM, TLAP = 'WT_DH', 'WT_DV'
add(t='erase', h=er)
print('erase', len(er))

def zones(i, s):
    a, b = PIECES[i]; z = D[i]; el, er_ = ENDS[i]
    out = []
    lo, hi = a + 50, b - 50
    if el and z['L'][s]: out.append(('L', a + 50, a + EDGE, z['L'][s], 100)); lo = a + EDGE + 100
    if er_ and z['R'][s]: out.append(('R', b - EDGE, b - 50, z['R'][s], 100)); hi = b - EDGE - 100
    md, ms = z['M'][s] if z['M'][s] else (12, 200)
    n = max(1, int((hi - lo) // ms)); out.append(('M', lo, lo + n * ms, md, ms))
    return out
def zd(i, s, kind):
    for z in zones(i, s):
        if z[0] == kind: return z[3]
    return None
def lap_at(i, s, kind):
    """lap length at the top of storey s (s<6) for the zone kind"""
    d = zd(i, s, kind); dn = zd(i, s + 1, kind) or d
    return LAP(max(d, dn))

POS = {}; BARS = []
def pos_of(d, Lb):
    k = (d, Lb)
    if k not in POS: POS[k] = len(POS) + 1
    return POS[k]
NOTE = dict(scale=100, ts=2.5, style='ГОСТ 2.304', arrow='oblique', layer='Размеры')
last = {}; CLAMP = set(); NY = {}; CH = []
DIAG = {(round(r['sp'][0][0]), round(r['sp'][0][1])): (r['sp'][1], r['sp'][2]) for r in R if r['t'] == 'LWPOLYLINE' and len(r['sp']) == 3 and r['y0'] > 14000}
AXES = [9810, 16610, 23060, 29860]
for s in range(7):
    yb = L[s]; yt = L[s + 1]
    DX = 20 * (s % 2)
    for i in range(4):
        zs = zones(i, s)
        base0 = {z[0]: (z[1], z[2]) for z in zones(i, 0)}
        for kind, x0, x1, d, st in zs:
            if kind in base0: x0, x1 = base0[kind]
            # A: slab top -> top slab + lap ; B: (prev lap + gap) above slab -> top slab + lap + gap + lap
            lp_dn = lap_at(i, s - 1, kind) if s > 0 else LAP(d)
            bA = yb; bB = yb + lp_dn + GAP(lp_dn)
            if s < 6:
                lp = lap_at(i, s, kind); tA = yt + lp; tB = yt + 2 * lp + GAP(lp)
            else:
                tA = tB = yt - TOPC
            key = (i, kind)
            if tB > L[7] - TOPC: tB = L[7] - TOPC; CLAMP.add(key)       # long staggered lap would pass the wall top
            hasB = not (s == 6 and key in CLAMP)
            LA = int(round(tA - bA, -1)); LB = int(round(tB - bB, -1))
            pA = pos_of(d, LA); pB = pos_of(d, LB) if hasB else None
            nb = int(round((x1 - x0) / st)) + 1
            nA = (nb + 1) // 2 if hasB else nb
            BARS.append(dict(pos=pA, d=d, L=LA, n=2 * nA))
            if hasB: BARS.append(dict(pos=pB, d=d, L=LB, n=2 * (nb - nA)))
            lay = 'диам%d' % d
            add(t='pl', p=[W(AX1 + x0 + DX, bA), W(AX1 + x0 + DX, tA)], layer=lay, lw=40)
            if hasB: add(t='pl', p=[W(AX1 + x1 + DX, bB), W(AX1 + x1 + DX, tB)], layer=lay, lw=40)
            else: add(t='pl', p=[W(AX1 + x1 + DX, bA), W(AX1 + x1 + DX, tA)], layer=lay, lw=40)
            if last.get(key) != (pA, pB, d, st):
                last[key] = (pA, pB, d, st)
                # texts right of the steep part of the opening diagonal and below its flat part (diagonal: b,yb -> b+~950,yb+2180 -> a_next,yt-250)
                ks = [z[0] for z in zs]
                ox = AX1 + PIECES[i][1] + (((1700 if i == 2 else 1600) if len(ks) == 3 else 1500) if i < 3 else 400)
                dg = DIAG.get((round(AX1 + PIECES[i][1]), round(yb)))
                if dg:                                                       # flat part of the diagonal above the texts
                    (mx, my), (ex, ey) = dg; U = my + (ox - mx) / (ex - mx) * (ey - my) - 400
                else: U = yt - SLAB - 450
                Lo = yb + 420
                n_ = len(ks); sp_ = max(780, min(900, (U - Lo) / max(1, n_ - 1))) if n_ > 1 else 0
                top = max(U, Lo + (n_ - 1) * sp_)                             # never closer than 780 (two text lines + gap)
                ymid = (top - ks.index(kind) * sp_) if n_ > 1 else (U + Lo) / 2
                lab = ('%d' % pA) if pB in (None, pA) else ('%d;%d' % (pA, pB))
                NY.setdefault(i, []).append((ymid, ox + 180 * (len(lab) + 5) + 150))      # shelf y, approx. shelf right end
                add(t='note', l1='%s(%%%%C%d)' % (lab, d), l2='ш.%d' % st, origin=W(ox, ymid),
                    targets=[W(AX1 + x0 + DX, ymid), W(AX1 + x1 + DX, ymid)], **NOTE)
        # staggered lap chain on the left of the piece: lap | gap | lap
        if s < 6:
            lp = max(lap_at(i, s, z[0]) for z in zs); g = GAP(lp)
            xa = AX1 + min(z[1] for z in zones(i, 0)) + DX; xd = AX1 + (PIECES[i][0] if i else -125) - 350      # analog: chain ~700 outside the wall face, ext. lines from the bar
            ys = [yt, yt + lp, yt + lp + g, yt + 2 * lp + g]
            nk = 3 if ys[3] <= L[7] - TOPC else 1                       # B lap passes the wall top -> B bar runs to the top, only A lap
            for k in range(nk):
                kw = dict(t='dim', h=TLAP, p1=W(xa, ys[k]), p2=W(xa, ys[k + 1]), dl=W(xd, (ys[k] + ys[k + 1]) / 2), rot=math.pi / 2, txt='')
                if k == 1: kw['tx'] = (i, xd - 260, ys)                          # short gap: text beside the chain (analog 220|730), placed after the notes
                CH.append(kw)
for kw in CH:                                                       # gap text: clear of the neighbour piece's notes (their shelves end near this chain)
    if 'tx' in kw:
        i, x, ys = kw['tx']; ny = NY.get(i - 1, [])
        for xx, y in ((x, (ys[1] + ys[2]) / 2), (x - 260, (ys[2] + ys[3]) / 2), (x - 260, max((ys[0] + ys[1]) / 2, ys[0] + 600))):   # beside a lap: one column further out than its text
            if all(abs(y - v) > 650 or xe < xx - 200 for v, xe in ny): break
        kw['tx'] = W(xx, y)
    add(**kw)
# ---- П caps (Ск) at the wall top: vertical legs at the extreme bars, drawn 20 mm off the top-storey bars ----
CAPS = {}; CDX = 20 * ((6 + 1) % 2)
for i in range(4):
    zs = zones(i, 6)
    base0 = {z[0]: (z[1], z[2]) for z in zones(i, 0)}
    tg = []; nums = []
    for kind, x0, x1, d, st in zs:
        if kind in base0: x0, x1 = base0[kind]
        if d not in CAPS: CAPS[d] = len(CAPS) + 1
        yt = L[7] - TOPC; leg = LAP(d)
        for x in (x0, x1):
            add(t='pl', p=[W(AX1 + x + CDX, yt), W(AX1 + x + CDX, yt - leg)], layer='диам%d' % d, lw=40)
        nb = int(round((x1 - x0) / st)) + 1
        BARS.append(dict(pos='Ск%d' % CAPS[d], d=d, L=2 * leg + 170, n=nb))
        tg += [W(AX1 + x0 + CDX, L[7] - SLAB - 80), W(AX1 + x1 + CDX, L[7] - SLAB - 80)]; nums.append(CAPS[d])
    ox = AX1 + PIECES[i][0] + (400 if i in (0, 3) else -300)          # pieces 2,3 have an axis inside: shelf to the left
    add(t='note', l1='Ск' + ';'.join(str(n) for n in sorted(set(nums))), l2='', origin=W(ox, L[7] + 450), targets=tg, **NOTE)
# ---- bottom chain of bar positions (basement) ----
for i in range(4):
    for (kind, x0, x1, d, st) in zones(i, 0):
        n_ = round((x1 - x0) / st); txt = ('%dх%d' % (st, n_)) if n_ > 1 else ''
        tw = 110 * len(txt) / 2 + 150
        tx = {'L': AX1 + x0 - tw, 'R': AX1 + x1 + tw, 'M': AX1 + (x0 + x1) / 2}[kind]
        if kind == 'M':                                                  # centre if it fits, else beside the zone; never on an axis
            for c in (AX1 + (x0 + x1) / 2, AX1 + x1 + tw, AX1 + x0 - tw):
                fits = c != AX1 + (x0 + x1) / 2 or (x1 - x0) > 2 * tw
                if fits and not any(abs(c - a) < tw - 100 for a in AXES): tx = c; break
        ty = 13334 if kind != 'M' else 12634
        add(t='dim', h=TDIM, p1=W(AX1 + x0, L[0]), p2=W(AX1 + x1, L[0]), dl=W(AX1 + (x0 + x1) / 2, ty), rot=0, txt=txt, tx=W(tx, ty + 60))
add(t='dimtx', h='11F2FF', at=W(5461, 28700))
add(t='save')
json.dump(dict(CAPS={str(k): v for k, v in CAPS.items()}, POS={'%d_%d' % k: v for k, v in POS.items()}, BARS=BARS), open('w/sm1_vert.json', 'w'))
json.dump(ops, open('ops/w52.json', 'w'), ensure_ascii=False)
print(len(ops), 'positions', len(POS))
for (d, Lb), p in sorted(POS.items(), key=lambda kv: kv[1]): print(p, 'Ø%d' % d, 'L', Lb, 'n', sum(b['n'] for b in BARS if b['pos'] == p))
if '--run' in sys.argv: print(gx.run(ops, 'w52')[-400:])
