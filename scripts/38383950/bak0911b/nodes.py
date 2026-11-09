# Завод В109 Цех Блок 1 — rolled-section nodes (sheets 15–17 of the album): output beamnodes.tsv for b109_12_beam_nodes.cs.
# Lines (mm):  BOX g x0 y0 z0 x1 y1 z1 | BOLT g px py pz dx dy dz dia grip | WELD g ox oy oz ax ay az bx by bz dx dy dz kf len
# g = node group (one DirectShape set per group). Same geometry rules as gen.py (imported).
import math, os
import gen
from gen import AX, R, H, BW, ztop
OUT = os.path.join(gen.HERE, 'beamnodes.tsv')
TF = {'50Ш2': 17.5, '60Ш2': 21, '60Ш3': 25, '40Ш2': 16, '40Ш1': 14, '20Ш1': 9, '30Б1': 8.5, '40Б1': 9.5, '45Ш1': 18, '70Б1': 15.5, '25Б1': 8}
TW = {'50Ш2': 14.5, '60Ш2': 16, '60Ш3': 18, '40Ш2': 10, '40Ш1': 9.5, '20Ш1': 6, '30Б1': 5.8, '40Б1': 7, '45Ш1': 11, '70Б1': 12, '25Б1': 5}
RR = {'50Ш2': 26, '60Ш2': 28, '60Ш3': 28, '40Ш2': 22, '40Ш1': 22, '20Ш1': 13, '30Б1': 15, '40Б1': 20, '45Ш1': 24, '70Б1': 24, '25Б1': 12}
L = []
WEBSIGN = float(open(os.path.join(gen.HERE, '_websign.txt')).read()) if os.path.exists(os.path.join(gen.HERE, '_websign.txt')) else 1.0   # +1: channel web on +Y
def f(v): return '%.2f' % v
def box(g, a, b): L.append(['BOX', g] + [f(min(a[i], b[i])) for i in range(3)] + [f(max(a[i], b[i])) for i in range(3)])
def plt(g, o, eu, ev, u0, v0, u1, v1, t): L.append(['PLT', g] + [f(v) for v in o] + [f(v) for v in eu] + [f(v) for v in ev] + [f(u0), f(v0), f(u1), f(v1), f(t)])
def bolt(g, p, d, dia, grip): L.append(['BOLT', g] + [f(v) for v in p] + [f(v) for v in d] + [str(dia), f(grip)])
def weld(g, o, a, b, d, kf, ln): L.append(['WELD', g] + [f(v) for v in o] + [f(v) for v in a] + [f(v) for v in b] + [f(v) for v in d] + [f(kf), f(ln)])
def add(p, v, k=1.0): return [p[i] + v[i] * k for i in range(3)]
def clearI(prof, zc): h, t, r = H[prof], TF[prof], RR[prof]; return (zc - h / 2 + t + r, zc + h / 2 - t - r)
# ---- fin plate −10: beam end e (centroid), u unit (axis-aligned, towards the support), n web normal; off = web half (or tube half width);
#      dist = end → support face; zr = (z0, z1) allowed band; bolts М16 at 50 from the end, through the web (grip tw+10) or the whole tube (grip b+10)
def fin(g, e, u, n, off, dist, zr, web, tube_b=0):
    z0, z1 = zr[0] + 10, zr[1] - 10
    hf = z1 - z0
    if hf < 40: return
    zc = (z0 + z1) / 2
    a = add(add(e, u, -100), n, off); b = add(add(e, u, dist - 0.3), n, off + 10)
    box(g, [a[0], a[1], z0], [b[0], b[1], z1])
    s = add(add(e, u, dist - 0.3), n, off); s2 = add(s, n, 10)
    m = [-u[0], -u[1], -u[2]]
    kf = min(6, dist - 1.5)                       # the bead stays off the beam end
    weld(g, [s[0], s[1], z0], [-n[0], -n[1], -n[2]], m, [0, 0, 1], kf, hf)
    weld(g, [s2[0], s2[1], z0], n, m, [0, 0, 1], kf, hf)
    nb = max(1, min(4, int((hf - 40) // 70) + 1))
    sp = 70
    for k in range(nb):
        zb = zc + (k - (nb - 1) / 2) * sp
        if tube_b: c = add(add(e, u, -50), n, -tube_b / 2); grip = tube_b + 10
        else: c = add(add(e, u, -50), n, -web / 2); grip = web + 10
        bolt(g, [c[0], c[1], zb], n, 16, grip)
# ---- column stiffeners −14 between the flanges at level z, on the web side(s) sx (±1 along X); skip the band y −1…+20 (gussets / fins)
def colstiff(g, x, y, z, prof, sides, t=14):
    hf, tf, tw, r = H[prof] / 2, TF[prof], TW[prof], RR[prof]
    yi = hf - tf - r
    for sx in sides:
        xa, xb = x + sx * tw / 2, x + sx * 150
        for ya, yb in ((y - yi, y - 8), (y + 22, y + yi)):
            box(g, [xa, ya, z - t / 2], [xb, yb, z + t / 2])
            weld(g, [xa, ya, z + t / 2], [sx, 0, 0], [0, 0, 1], [0, 1, 0], 6, yb - ya)
def colprof(x, y): return '60Ш3' if (abs(y - 60000) < 1 and 72000 - 1 <= x <= 90000 + 1) else '60Ш2'
# ================= columns К1 / К2: cap −14, truss chord / БП2 fins (узлы 6–8), stiffeners
for i, x in enumerate(AX):
    for r in 'AEHM':
        y = R[r]; pr = colprof(x, y); hf = H[pr] / 2; top = (14490 if r in 'AM' else 15097) - 14
        g = 'Оголовок К ' + str(int(x)) + ' ' + r
        box(g, [x - 150, y - hf, top], [x + 150, y + hf, top + 14])
        for sx in (-1, 1): weld(g, [x - 150 if sx < 0 else x + 150, y - hf, top], [sx, 0, 0], [0, 0, 1], [0, 1, 0], 6, 2 * hf) if False else None
        weld(g, [x - 150, y - hf, top], [0, -1, 0], [0, 0, -1], [1, 0, 0], 4, 300); weld(g, [x - 150, y + hf, top], [0, 1, 0], [0, 0, -1], [1, 0, 0], 4, 300)
        # members along Y landing on the flange outer faces
        sides = []
        if 1 <= i <= 26:                                     # ФФ1 top chord
            if r == 'A': sides.append((1, '20Ш1'))
            if r == 'M': sides.append((-1, '20Ш1'))
            if r == 'E': sides.append((-1, '20Ш1'))
            if r == 'H': sides.append((1, '20Ш1'))
        if r == 'E': sides.append((1, '40Б1'))               # БП2 E–H on all axes
        if r == 'H': sides.append((-1, '40Б1'))
        if i in (0, 27):                                     # БП1 on axes 1 / 28
            if r == 'A': sides.append((1, '30Б1'))
            if r == 'E': sides.append((-1, '30Б1'))
            if r == 'H': sides.append((1, '30Б1'))
            if r == 'M': sides.append((-1, '30Б1'))
        for sy, mp in sides:
            yf = y + sy * hf; st = {'20Ш1': 312.0, '40Б1': 314.5, '30Б1': 309.5}[mp]; yend = y + sy * st; zc = ztop(yend) - H[mp] / 2
            gg = 'Узел ' + mp + ' к колонне ' + str(int(x)) + ' ' + r + ' ' + str(sy)
            fin(gg, [x, yend, zc], [0, -sy, 0], [1, 0, 0], TW[mp] / 2, st - hf, clearI(mp, zc), TW[mp])
            colstiff(gg, x, y, ztop(yf) - H[mp] + TF[mp] / 2, pr, (-1, 1))
# ================= КН consoles (узел 9): shop welds to the flange, column stiffeners; БМ1 bearing stiffeners + bolts М20 to the console
for r, off in (('A', 750), ('E', -750), ('H', 750), ('M', -750)):
    y = R[r]; sy = 1 if off > 0 else -1; yb = y + off
    for i, x in enumerate(AX):
        pr = colprof(x, y); hf = H[pr] / 2; g = 'Узел 9 КН ' + str(int(x)) + ' ' + r
        zt, zbm = 10340.0, 10340.0 - H['40Ш1']
        yf = y + sy * (hf + 1)
        for z in (zt, zbm): weld(g, [x - 150, yf, z], [0, sy, 0], [0, 0, 1 if z == zt else -1], [1, 0, 0], 8, 300)
        for sx in (-1, 1): weld(g, [x + sx * TW['40Ш1'] / 2, yf, zbm + TF['40Ш1'] + RR['40Ш1']], [sx, 0, 0], [0, sy, 0], [0, 0, 1], 6, H['40Ш1'] - 2 * TF['40Ш1'] - 2 * RR['40Ш1'])
        colstiff(g, x, y, zt - TF['40Ш1'] / 2, pr, (-1, 1)); colstiff(g, x, y, zbm + TF['40Ш1'] / 2, pr, (-1, 1))
        # БМ1 ends over the console (pieces end at x ± 1): bearing ribs −14 both sides of the web, bolts М20 2 per end
        for sx in (-1, 1):
            xe = x + sx * 1
            if (sx < 0 and i == 0) or (sx > 0 and i == 27): continue
            for s2 in (-1, 1):
                box(g, [xe + sx * 6, yb + s2 * 3, 10350], [xe + sx * 20, yb + s2 * 95, 10990])
                weld(g, [xe + sx * 6, yb + s2 * 3, 10350], [0, s2, 0], [0, 0, 1], [sx, 0, 0], 5, 14) if False else None
                bolt(g, [xe + sx * 60, yb + s2 * 60, 10340 - TF['40Ш1']], [0, 0, 1], 20, TF['40Ш1'] + 10)
# ================= БП2 ridge splice (two pieces at y 30000), one plate −10 on the +X side of the web, 2 × 3 bolts
for x in AX:
    zc = ztop(30000) - H['40Б1'] / 2; z0, z1 = clearI('40Б1', zc); z0 += 15; z1 -= 15
    g = 'Стык БП2 ' + str(int(x))
    box(g, [x + 3.5, 29995 - 200, z0], [x + 13.5, 30005 + 200, z1])
    for yy in (29995 - 60, 30005 + 60):
        for k in range(3): bolt(g, [x - 3.5, yy, (z0 + z1) / 2 + (k - 1) * 80], [1, 0, 0], 16, 17)
# ================= СФ caps −20 + 4 bolts through the beam bottom flange (БП1 / БП2)
for x in (0.0, 162000.0):
    for r in 'BCDFGIKL':
        y = R[r]; mp = '40Б1' if r in 'FG' else '30Б1'; zt = ztop(y) - H[mp] - 24
        g = 'Оголовок СФ ' + str(int(x)) + ' ' + r
        box(g, [x - 195, y - 150, zt], [x + 195, y + 150, zt + 20])
        weld(g, [x - 195, y - 150, zt], [-1, 0, 0], [0, 0, -1], [0, 1, 0], 6, 300); weld(g, [x + 195, y - 150, zt], [1, 0, 0], [0, 0, -1], [0, 1, 0], 6, 300)
        for bx in (-45, 45):
            for by in (-60, 60): bolt(g, [x + bx, y + by, zt], [0, 0, 1], 16, 20 + 4 + TF[mp])
# ================= Р2 □100x3 ends on the bottom chord side faces: fillet welds round the end
for c, u in gen.P2_ENDS:
    g = 'Узел Р2 ' + str(int(c[0])) + ' ' + str(int(c[1]))
    for a, dvec, out in (([0, -50, -50], [0, 1, 0], [0, 0, -1]), ([0, -50, 50], [0, 1, 0], [0, 0, 1]), ([0, -50, -50], [0, 0, 1], [0, -1, 0]), ([0, 50, -50], [0, 0, 1], [0, 1, 0])):
        weld(g, add(c, a), out, [-u[0], 0, 0], dvec, 4, 100)
# ================= ФФ1 lattice welded straight to the chords: fillet welds round the footprint of every cut end
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
for k, e in enumerate(gen.TRUSS_ENDS):
    U = e['u']; Wv = [1, 0, 0]; Vv = gen.nrm(cross(U, Wv)); p, m, b = e['p'], e['m'], e['b']; hb = b / 2
    corners = []
    for sv, sw in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        o = [p[i] + Vv[i] * sv * hb + Wv[i] * sw * hb for i in range(3)]
        t = dot([p[i] - o[i] for i in range(3)], m) / dot(U, m)
        corners.append([o[i] + U[i] * t for i in range(3)])
    cen = [sum(c[i] for c in corners) / 4 for i in range(3)]
    g = 'шов решётки ФФ1 ' + str(int(p[0])) + ' ' + str(k)
    for q in range(4):
        a, bq = corners[q], corners[(q + 1) % 4]; dv = [bq[i] - a[i] for i in range(3)]; ln = math.sqrt(dot(dv, dv)); dv = [c / ln for c in dv]
        mid = [(a[i] + bq[i]) / 2 - cen[i] for i in range(3)]
        out = [mid[i] - dv[i] * dot(mid, dv) - m[i] * dot(mid, m) for i in range(3)]; out = gen.nrm(out)
        weld(g, [a[i] - m[i] * 0.7 + out[i] * 1.0 for i in range(3)], out, [-c for c in U], dv, 4, ln)
# bottom chord tube ends: cap −6 outside the end, square to the chord
for (x, y, z, sgn) in gen.CHORD_ENDS:
    g = 'Заглушка НП ' + str(int(x)) + ' ' + str(int(y))
    dvec = gen.nrm([0, sgn, gen.dz(y) * sgn]); ev = gen.nrm(cross(dvec, [1, 0, 0])); eu = cross(ev, dvec)
    plt(g, [x, y, z], eu, ev, -60, -60, 60, 60, 6)
# ================= purlins: 2 bolts М16 per piece end through the bottom flange and the support flange (узел 2, 3-3)
for k in range(21):
    y = 3000.0 * k
    for i, x in enumerate(AX):
        if k in (0, 8, 12, 20): sup, tsup = 'cap', 14
        elif 8 < k < 12: sup, tsup = 'БП2', TF['40Б1']
        elif i in (0, 27): sup, tsup = 'БП1', TF['30Б1']
        else: sup, tsup = 'ВП', TF['20Ш1']
        zb = 14490.0 if k in (0, 20) else 15097.0 if k in (8, 12) else ztop(y)
        g = 'Пр1 опора ' + str(int(x)) + ' ' + str(int(y))
        for sx in (-1, 1):
            if (sx < 0 and i == 0) or (sx > 0 and i == 27): continue
            for by in (WEBSIGN * -5, WEBSIGN * -30):
                bolt(g, [x + sx * 50, y + by, zb - tsup], [0, 0, 1], 16, tsup + 10.5)
# ================= площадка +4.000 / +7.600 (ЛИРА): fins on every beam end
X = lambda a: AX[a - 1]
for lev in (4000.0, 7600.0):
    ylines = gen.YL[lev]; pl = 'Площадка %d ' % lev
    cz = lambda pr: lev - H[pr] / 2
    for x, mk, pr in ylines:
        pc = colprof(x, 60000); hfc = H[pc] / 2
        fin(pl + mk + ' ' + str(int(x)) + ' К3', [x, 50197, cz(pr)], [0, -1, 0], [1, 0, 0], TW[pr] / 2, 16, clearI(pr, cz(pr)), TW[pr])
        fin(pl + mk + ' ' + str(int(x)) + ' К', [x, 60000 - hfc - 10, cz(pr)], [0, 1, 0], [1, 0, 0], TW[pr] / 2, 10, clearI(pr, cz(pr)), TW[pr])
    for j in range(len(ylines) - 1):
        (xa, ma, pa), (xb, mb, pb) = ylines[j], ylines[j + 1]
        for xe, sx in ((xa, 1), (xb, -1)):
            fin(pl + 'Б1-К3 ' + str(int(xe)) + ' ' + str(sx), [xe + sx * 197, 50000, cz('25Б1')], [-sx, 0, 0], [0, 1, 0], TW['25Б1'] / 2, 10, clearI('25Б1', cz('25Б1')), TW['25Б1'])
            pr = colprof(xe, 60000); g = pl + 'Б1-К ' + str(int(xe)) + ' ' + str(sx)
            fin(g, [xe + sx * 160, 60000, cz('25Б1')], [-sx, 0, 0], [0, 1, 0], TW['25Б1'] / 2, 160 - TW[pr] / 2, clearI('25Б1', cz('25Б1')), TW['25Б1'])
            for dzz in (H['25Б1'] / 2 - TF['25Б1'] / 2, -(H['25Б1'] / 2 - TF['25Б1'] / 2)): colstiff(g, xe, 60000, cz('25Б1') + dzz, pr, (sx,))
        for y in (52500.0, 55000.0, 57500.0):
            for xe, sx, ps in ((xa, 1, pa), (xb, -1, pb)):
                band = clearI('30Б1', cz('30Б1')); sb_ = clearI(ps, cz(ps)); band = (max(band[0], sb_[0]), min(band[1], sb_[1]))
                fin(pl + 'Б2 ' + str(int(xe)) + ' ' + str(int(y)) + ' ' + str(sx), [xe + sx * (BW[ps] / 2 + 10), y, cz('30Б1')], [-sx, 0, 0], [0, 1, 0], TW['30Б1'] / 2, BW[ps] / 2 + 10 - TW[ps] / 2, band, TW['30Б1'])
# ================= caps on the tube posts К3 (−10), СФ1 (−10)
for ax in range(13, 20):
    x = AX[ax - 1]; zt = (7600.0 if ax <= 16 else 4000.0) - 10
    box('Оголовок К3 ' + str(ax), [x - 187, 50000 - 181, zt], [x + 187, 50000 + 181, zt + 10])
    weld('Оголовок К3 ' + str(ax), [x - 187, 50000 - 181, zt], [-1, 0, 0], [0, 0, -1], [0, 1, 0], 6, 362)
for r in 'HIKLM':
    y = R[r]; box('Оголовок СФ1 ' + r, [-7100, y - 100, 5690], [-6900, y + 100, 5700]); weld('Оголовок СФ1 ' + r, [-7100, y - 100, 5690], [-1, 0, 0], [0, 0, -1], [0, 1, 0], 5, 200)
with open(OUT, 'w', encoding='utf-8') as fo:
    for l in L: fo.write('\t'.join(l) + '\n')
from collections import Counter
print(len(L), Counter(l[0] for l in L), len(set(l[1] for l in L)), 'groups')
