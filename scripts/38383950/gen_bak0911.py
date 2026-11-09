# Завод В109 Цех Блок 1 — КМ frame for Revit. Sections: LIRA В_109_v3_КМ.lir (user 08.11.2026: «сечениелерді лирадан ал»; element stiffness
# v → LIRA type v+1, checked on Р1 □100x5, СВ □160x5 / □100x5, БМ1, К3 короб). Truss ФФ1 as the Tekla sheet «Ферма ФФ1» made from the same LIRA:
# ВП 20Ш1, НП □120x5, Р1 □120x5 (support diagonals), Р2 □100x3, chord axes 2100 apart, lattice welded straight to the chords (no gussets).
# Layout / levels: album «… (Цех Блок 1, ЛИРА).dwg» + roof slope agreed with the user (+14.490 → +15.240).
# Output members.tsv (mm), one line per member:
#   C  type  fam  profile  x y zb  x y zt  depthDir(X|Y)        — column (fam Ic / Tc)
#   B  type  fam  profile  x1 y1 z1  x2 y2 z2  roll(deg)          — beam on its centroid line (Ib / Tb / Cb channel); fam W = top-surface line
# and cuts.tsv: member row, end (0/1), plane point, plane normal pointing into the chord (the void side) — the lattice ends are cut on the chord faces.
# Origin: axis 1 × axis A, X along 1→28, Y along A→M, z = elevation (±0.000). type = «mark[ part]», the mark is the first word.
import math, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'members.tsv'); OUTC = os.path.join(HERE, 'cuts.tsv')
AX = [6000.0 * i for i in range(28)]                      # axes 1..28
R = dict(A=0, B=6000, C=12000, D=18000, E=24000, F=27000, G=33000, H=36000, I=42000, K=48000, L=54000, M=60000)
H = {'60Ш2': 589, '60Ш3': 597, '40Ш2': 390, '40Ш1': 388, '20Ш1': 193, '30Б1': 296, '40Б1': 392, '45Ш1': 440, '70Б1': 691, '25Б1': 248, '50Ш2': 489, '27П': 270}
BW = {'60Ш2': 300, '60Ш3': 300, '40Ш2': 300, '40Ш1': 300, '20Ш1': 150, '30Б1': 140, '40Б1': 165, '45Ш1': 300, '70Б1': 260, '25Б1': 124, '50Ш2': 300, '27П': 95}
S = 750.0 / 29705.5          # roof: top of chords +14.490 at the A/M column faces (294.5 from the axis) → +15.240 at the ridge (30000)
def ztop(y):
    yy = y if y <= 30000 else 60000 - y
    return 14490 + S * (yy - 294.5)
def dz(y): return S if y < 30000 else -S              # slope of the roof along +Y
rows = []; cuts = []; TRUSS_ENDS = []; P2_ENDS = []; CHORD_ENDS = []
def C(t, fam, prof, x, y, zb, zt, d): rows.append(['C', t, fam, prof, x, y, zb, x, y, zt, d])
def B(t, fam, prof, a, b, roll=0.0): rows.append(['B', t, fam, prof, a[0], a[1], a[2], b[0], b[1], b[2], roll]); return len(rows) - 1
def unit(a, b):
    v = [b[i] - a[i] for i in range(3)]; l = math.sqrt(sum(c * c for c in v)); return [c / l for c in v], l
def trim(a, b, ta, tb):
    u, l = unit(a, b); return [a[i] + u[i] * ta for i in range(3)], [b[i] - u[i] * tb for i in range(3)]
def apex(bw, th):            # axis trim at a node shared by two tubes (plane angle th to the joined member): the pair stays apart
    return max((bw / 2 / math.sin(th) + 5) / math.cos(th), bw / 2 / math.tan(th) + 10)
def nrm(v): l = math.sqrt(sum(c * c for c in v)); return [c / l for c in v]
ZB = -260.0                  # К1/К2/К3 bottom = top of the base plate −40 on the foundation top −0.300 (СФ, СФ1: plate −20 → −0.280)
# ---------------- columns: К1 60Ш2 rows A, E, H, M (К2 60Ш3 on M, axes 13–16), web along Y (frame plane)
for i, x in enumerate(AX):
    for r in 'AEHM':
        y = R[r]; ax = i + 1
        k2 = r == 'M' and 13 <= ax <= 16
        top = (14490 if r in 'AM' else 15097) - 14        # under the cap −14: A/M cap top = chord top at the face; E/H = БП2 top at the face
        C('К2' if k2 else 'К1', 'Ic', '60Ш3' if k2 else '60Ш2', x, y, ZB, top, 'Y')
# СФ 40Ш2 on axes 1 / 28 (web along X), top under БП1 (30Б1) / БП2 (40Б1): cap −20 + 4
for x in (0.0, 162000.0):
    for r in 'BCDFGIKL':
        y = R[r]; beam = '40Б1' if r in 'FG' else '30Б1'
        C('СФ', 'Ic', '40Ш2', x, y, ZB - 20, ztop(y) - H[beam] - 24, 'X')
# СФ1 □200x6 at x −7000 (ЛИРА nodes −0.300 … +5.700), cap −10
for r in 'HIKLM': C('СФ1', 'Tc', '□200x6', -7000.0, R[r], ZB - 20, 5700.0 - 10, 'X')
# К3 «короб составной» (ЛИРА 20) at y 50000, axes 13–19 (13–16 to +7.600, 17–19 to +4.000), cap −10
for ax in range(13, 20): C('К3', 'Tc', '□374x362x12', AX[ax - 1], 50000.0, ZB, (7600.0 if ax <= 16 else 4000.0) - 10, 'X')
# ---------------- vertical bracing rows A, E, H, M, bays 9-10 / 19-20: ЛИРА 11 □160x5 (−0.300…+10.340), 12 □100x5 (above +10.340); struts Р1 ЛИРА 10 □100x5
hs = 50.0
for r in 'AEHM':
    y = R[r]
    for i in range(2, 25):                                 # Р1 at +10.340, bays 3-4 … 25-26
        B('Р1', 'Tb', '□100x5', [AX[i] + 160, y, 10340], [AX[i + 1] - 160, y, 10340])
    for i in (8, 18):
        xa, xb = AX[i] + 150, AX[i + 1] - 150; xm = (AX[i] + AX[i + 1]) / 2
        B('Р1', 'Tb', '□100x5', [AX[i] + 160, y, 5020], [AX[i + 1] - 160, y, 5020])
        top = 14490 if r in 'AM' else 15097
        tiers = [('СВ1', '□160x5', 0.0, 5020 - hs), ('СВ1', '□160x5', 10340 - hs - 10, 5020 + hs), ('СВ2' if r in 'AM' else 'СВ3', '□100x5', top - 400, 10340 + hs)]
        for mark, prof, zc, zm in tiers:
            bw = 160 if prof == '□160x5' else 100
            for xc in (xa, xb):
                a, b = [xc, y, zc], [xm, y, zm]
                th = math.atan2(abs(zc - zm), abs(xm - xc))
                tc = bw / 2 * max(math.tan(th), 1 / math.tan(th)) + 10            # end corner clear of the column flange face
                pa, pb = trim(a, b, tc, apex(bw, th))
                B(mark, 'Tb', prof, pa, pb)
# ---------------- crane beams БМ1 (ЛИРА 8, welded I 660, top-surface line) at 750 from the rows on the consoles КН 40Ш1 (ЛИРА 9) +10.340
hk = H['40Ш1'] / 2
for r, off in (('A', 750), ('E', -750), ('H', 750), ('M', -750)):
    y = R[r] + off
    for i in range(27): B('БМ1', 'W', 'I660 250-200', [AX[i] + (1 if i else 0), y, 11000], [AX[i + 1] - (1 if i < 26 else 0), y, 11000])
    sgn = 1 if off > 0 else -1
    for i, x in enumerate(AX):
        hf = 298.5 if (r == 'M' and 13 <= i + 1 <= 16) else 294.5
        B('КН', 'Ib', '40Ш1', [x, R[r] + sgn * (hf + 1), 10340 - hk], [x, R[r] + sgn * 950, 10340 - hk])
# ---------------- roof: trusses ФФ1 (axes 2–27, spans A–E and H–M), Tekla «Ферма ФФ1»
TC = lambda y: ztop(y) - H['20Ш1'] / 2                    # top chord axis
BC = lambda y: TC(y) - 2100                                # bottom chord axis (□120x5)
def truss(x, y0, sgn):
    Y = lambda d: y0 + sgn * d
    B('ФФ1 ВП', 'Ib', '20Ш1', [x, Y(312.0), TC(Y(312.0))], [x, Y(23688.0), TC(Y(23688.0))])
    ib = B('ФФ1 НП', 'Tb', '□120x5', [x, Y(1250.0), BC(Y(1250.0))], [x, Y(22750.0), BC(Y(22750.0))])
    CHORD_ENDS.append((x, Y(1250.0), BC(Y(1250.0)), -sgn)); CHORD_ENDS.append((x, Y(22750.0), BC(Y(22750.0)), sgn))
    # nodes (distance from the outer row): top at the chord underside, bottom on the chord top face
    chain = [('T', None)] + sum([[('B', 1498.5 + 3000 * k)] + ([('T', 3000.0 * (k + 1))] if k < 7 else []) for k in range(8)], []) + [('T', None)]
    nd = len(chain) - 1
    zT = lambda yy: ztop(yy) - H['20Ш1']                   # top chord underside
    zB = lambda yy: BC(yy) + 60                            # bottom chord top face
    for j in range(nd):
        na, nb = chain[j], chain[j + 1]
        big = j < 2 or j >= nd - 2
        prof, bw = ('□120x5', 120) if big else ('□100x3', 100)
        da = na[1] if na[1] is not None else (nb[1] - 1100); db = nb[1] if nb[1] is not None else (na[1] + 1100)
        th = math.atan2(2100 - 96.5 - 60, abs(db - da))
        foot = bw / 2 / math.sin(th)
        def cpt(n, d, other):
            if n[1] is None:                                   # end top node at the column: clear of the chord start (312 + 15)
                dd = 312 + 15 + foot if other > d else 24000 - 312 - 15 - foot
            else:
                dd = n[1] + (1 if other > d else -1) * (foot + 10)          # K-joint gap 20 between the two footprints
            yy = Y(dd); return [x, yy, zT(yy) if n[0] == 'T' else zB(yy)], n[0]
        (pa, ka), (pb, kb) = cpt(na, da, db), cpt(nb, db, da)
        u, l = unit(pa, pb)
        ea = [pa[i] - u[i] * 150 for i in range(3)]; eb = [pb[i] + u[i] * 150 for i in range(3)]   # 150 into the chords, cut by voids
        k = B('ФФ1 Р1' if big else 'ФФ1 Р2', 'Tb', prof, ea, eb)
        for end, p, kind, uu in ((0, pa, ka, [-c for c in u]), (1, pb, kb, u)):
            m = nrm([0, -dz(p[1]), 1]) if kind == 'T' else nrm([0, dz(p[1]), -1])      # into the chord
            q = [p[i] - m[i] * 0.3 for i in range(3)]                                   # 0.3 short of the chord face
            cuts.append([k, end] + q + m)
            TRUSS_ENDS.append(dict(p=q, u=uu, m=m, b=bw, kind=kind))
for i in range(1, 27):
    truss(AX[i], 0.0, 1); truss(AX[i], 60000.0, -1)
# БП2 40Б1 (ЛИРА 3) E–H on all axes (two pieces meeting at the ridge), БП1 30Б1 (ЛИРА 4) on axes 1 / 28 between the posts (over the СФ tops)
for x in AX:
    for ya, yb in ((24314.5, 29995.0), (30005.0, 35685.5)):
        B('БП2', 'Ib', '40Б1', [x, ya, ztop(ya) - H['40Б1'] / 2], [x, yb, ztop(yb) - H['40Б1'] / 2])
for x in (0.0, 162000.0):
    for seg in ('ABCDE', 'HIKLM'):
        for j in range(4):
            ra, rb = seg[j], seg[j + 1]
            ya = R[ra] + (309.5 if ra in 'AEHM' else 0.5)
            yb = R[rb] - (309.5 if rb in 'AEHM' else 0.5)
            B('БП1', 'Ib', '30Б1', [x, ya, ztop(ya) - H['30Б1'] / 2], [x, yb, ztop(yb) - H['30Б1'] / 2])
# Р2 □100x3 (ЛИРА 6) struts on the bottom chords, coaxial with them, y 3050 / 21050 / 38950 / 56950, axes 3–26, ends 0.3 off the chord side faces
for y in (3050.0, 21050.0, 38950.0, 56950.0):
    z = BC(y)
    for i in range(2, 25):
        B('Р2', 'Tb', '□100x3', [AX[i] + 60.3, y, z], [AX[i + 1] - 60.3, y, z])
        P2_ENDS.append(([AX[i] + 60.3, y, z], [-1, 0, 0])); P2_ENDS.append(([AX[i + 1] - 60.3, y, z], [1, 0, 0]))
# purlins Пр1 [27П (ЛИРА 18) every 3000, one piece per bay, bottom flange on the roof (square to it); over the rows A/E/H/M on the column caps
for k in range(21):
    y = 3000.0 * k
    zb = ztop(y)
    if k in (0, 20): zb = 14490.0
    if k in (8, 12): zb = 15097.0
    roll = 0.0 if k in (0, 8, 10, 12, 20) else math.degrees(math.atan(S)) * (1 if y < 30000 else -1)
    ny, nz = -math.sin(math.radians(roll)), math.cos(math.radians(roll))
    cy, cz = y + ny * H['27П'] / 2, zb + nz * H['27П'] / 2
    for i in range(27): B('Пр1', 'Cb', '27П', [AX[i] + (1 if i else 0), cy, cz], [AX[i + 1] - (1 if i < 26 else 0), cy, cz], roll)
# ГС1 □100x3 (ЛИРА 7) from sheet 8 (corner of a 6000 × 3000 panel → middle of the opposite purlin), centre 62 under the roof
gs = json.load(open(os.path.join(HERE, 'gs1.json')))
def gtrim(x, y):
    if abs(x % 6000) < 1 or abs(x % 6000 - 6000) < 1:        # at a truss / БП1 / БП2 line: clear of its flange
        if any(abs(y - r) < 1 for r in (0, 24000, 36000, 60000)):
            return (294.5 + 10 + 50 * 0.7071) / 0.7071          # node over a column (row A/E/H/M): out of the column top
        if 24000 < y < 36000: bw = BW['40Б1']
        elif abs(x) < 1 or abs(x - 162000) < 1: bw = BW['30Б1']
        else: bw = BW['20Ш1']
        return (bw / 2 + 10 + 50 * 0.7071) / 0.7071
    return (50 / 0.7071 + 5) / 0.7071                          # under the purlin middle, where two meet
for (xa, ya, xb, yb) in gs:
    a, b = [xa, ya, ztop(ya) - 62], [xb, yb, ztop(yb) - 62]
    pa, pb = trim(a, b, gtrim(xa, ya), gtrim(xb, yb))
    B('ГС1', 'Tb', '□100x3', pa, pb)
# ---------------- площадка +4.000 (axes 13–19) / +7.600 (13–16), y 50000 … 60000, tops flush with the level (ЛИРА)
#  Y-lines (50000 → 60000): Б4 70Б1 (ЛИРА 13) at x 78 / 84 (/ 96 / 102), Б7 45Ш1 (ЛИРА 16) at the edges 72 / 108 (+4.000) and 72 / 90 (+7.600),
#  Б3 50Ш2 (ЛИРА 21) at x 90 (+4.000); X-lines: Б1 25Б1 (ЛИРА 17) on y 50000 / 60000, Б2 30Б1 (ЛИРА 14) on y 52500 / 55000 / 57500 between the Y-lines.
#  ЛИРА 15 «Плита по проф.» (the 833-grid) is the deck, not steel — not modelled.
X = lambda ax: AX[ax - 1]
YL = {}
for lev, axs in ((4000.0, list(range(13, 20))), (7600.0, list(range(13, 17)))):
    x0, x1 = X(axs[0]), X(axs[-1])
    hz = lambda p: lev - H[p] / 2
    ylines = [(X(a), 'Б7', '45Ш1') if X(a) in (x0, x1) else (X(a), 'Б3', '50Ш2') if X(a) == 90000.0 else (X(a), 'Б4', '70Б1') for a in axs]
    YL[lev] = ylines
    for x, mk, pr in ylines:
        hfc = 298.5 if 72000 - 1 <= x <= 90000 + 1 else 294.5
        B(mk, 'Ib', pr, [x, 50000 + 197, hz(pr)], [x, 60000 - hfc - 10, hz(pr)])
    for j in range(len(axs) - 1):
        xa, xb = X(axs[j]), X(axs[j + 1])
        B('Б1', 'Ib', '25Б1', [xa + 197, 50000, hz('25Б1')], [xb - 197, 50000, hz('25Б1')])
        B('Б1', 'Ib', '25Б1', [xa + 160, 60000, hz('25Б1')], [xb - 160, 60000, hz('25Б1')])
        pa = ylines[j][2]; pb = ylines[j + 1][2]
        for y in (52500.0, 55000.0, 57500.0):
            B('Б2', 'Ib', '30Б1', [xa + BW[pa] / 2 + 10, y, hz('30Б1')], [xb - BW[pb] / 2 - 10, y, hz('30Б1')])
with open(OUT, 'w', encoding='utf-8') as f:
    for r in rows: f.write('\t'.join(str(round(v, 2)) if isinstance(v, float) else str(v) for v in r) + '\n')
with open(OUTC, 'w', encoding='utf-8') as f:
    for c in cuts: f.write('\t'.join(str(c[0]) if i == 0 else str(c[1]) if i == 1 else '%.4f' % c[i] for i in range(len(c))) + '\n')
if __name__ == '__main__':
    from collections import Counter
    print(len(rows), dict(Counter(r[1] for r in rows)), 'cuts', len(cuts))
