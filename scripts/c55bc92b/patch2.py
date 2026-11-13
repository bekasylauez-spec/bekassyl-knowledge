# -*- coding: utf-8 -*-
# gen.py v2, part 2: Р1/Р2/Р3, СВ1-5, ГС1/2 (құбыр ұштары, жазықтықтар, X-крест бөлінуі) — uzel_07…15, baza_B2
P = r'D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто\gen.py'
src = open(P, encoding='utf-8').read()
a = src.index('# ============ РАСПОРКАЛАР ============')
b = src.index('# ---------- шығару ----------')
new = r'''# ============ РАСПОРКАЛАР ============
# Жазықтықтар (паспорт, бүкіл жоба): вертикаль связь осі A 266 / D 17 986 / G 35 734; төменгі Р1 осі = связь + 28 (uzel_08/12); жоғарғы Р1 = колонна осі + 22 (uzel_07/12); Р2 = 18 014 (uzel_13)
Y_SV = {0.0: 266.0, 18.0: 17986.0, 36.0: 35734.0}
def y_sv(yl): return Y_SV[round(yl, 3)]
for r in by_s[9]:
    zl = round(r['p'][2], 3); yl = round(r['p'][1], 3)
    x1, x2 = XM(r['p'][0]), XM(r['q'][0]); x1, x2 = min(x1, x2), max(x1, x2)
    if abs(zl - 5.0) < 1e-6:
        z = Z_STRUT; y = y_sv(yl) + 28.0; cut = COL_H / 2          # төменгі Р1: ұшы колонна осінен 150 (uzel_08: «құбыр ұшы x = 150»)
    else:
        z = Z_R1_UPPER; y = YC(yl) + 22.0; cut = 254.0             # жоғарғы Р1: ұшы 254 (uzel_07 / 12а), осі +8,641,6
    p, q = clip_line((x1, y, z), (x2, y, z), cut, cut)
    add('Р1', 'B', tuple(p), tuple(q), 'tube', rodids=[r['i']], note='z%.1f' % zl)
for r in by_s[10]:
    y = 18014.0; z = neu_raf(18000.0)                                # Р2 осі жота пластинасының +Y бетінде (uzel_13), z = ригель осі +9,593
    x1, x2 = sorted((XM(r['p'][0]), XM(r['q'][0])))
    p, q = clip_line((x1, y, z), (x2, y, z), 325.0, 325.0)           # құбыр ұшы рама осінен 325 (uzel_02/07/13)
    add('Р2', 'B', tuple(p), tuple(q), 'tube', rodids=[r['i']])
for r in by_s[11]:
    y = round(r['p'][1], 3) * 1000.0; z = neu_raf(y)
    cut = 254.0 if (abs(y - 6000.0) < 1 or abs(y - 30000.0) < 1) else 269.0   # B/F 254, C/E 269 (uzel_14, 15)
    x1, x2 = sorted((XM(r['p'][0]), XM(r['q'][0])))
    p, q = clip_line((x1, y, z), (x2, y, z), cut, cut)
    add('Р3', 'B', tuple(p), tuple(q), 'tube', rodids=[r['i']])

# ============ ВЕРТИКАЛЬ СВЯЗЬ ============
# құбыр ұштары (паспорттағы «құбыр ұшы»), колонна осінен аралыққа қарай жергілікті (x, z): (торец аралығы?) -> (төменгі ұш, жоғарғы ұш)
SV_END = {
    ('СВ1', True): ((293.1, 6192.5), (278.3, 8425.0)),     # uzel_08 (8) / uzel_07 (1–2, 10–11)
    ('СВ1', False): ((298.9, 6191.7), (274.7, 8429.4)),    # uzel_08 (8а, 8б) / uzel_07 (4–5, 7–8)
    ('СВ2', True): ((231.7, 6203.6), (330.9, 9301.2)),
    ('СВ2', False): ((233.2, 6201.1), (328.7, 9307.3)),
    ('СВ3', False): ((166.1, 1476.9), (197.9, 5781.8)),    # baza_B2 (Б2) / uzel_08 (8а)
    ('СВ4', False): ((166.3, 1416.1), (728.5, 3446.2)),    # baza_B2 (Б2а) / uzel_11
    ('СВ5', False): ((783.2, 4022.6), (327.1, 5811.8)),    # uzel_11 / uzel_08 (8б)
}
# кесілген диагональ жартыларының ұшы қиылыстан (заглушка беті), осьпен r (uzel_09)
SV_R = {('СВ1', True): 234.0, ('СВ1', False): 239.0, ('СВ2', True): 180.0, ('СВ2', False): 184.0, ('СВ3', False): 147.0, ('СВ4', False): 247.0, ('СВ5', False): 265.0}
def line_isect(p1, q1, p2, q2, ia=0, ib=2):
    """екі кесіндінің (ia, ib координаталар) қиылысы: параметр t (1-ші бойынша) қайтарады"""
    d1 = (q1[ia] - p1[ia], q1[ib] - p1[ib]); d2 = (q2[ia] - p2[ia], q2[ib] - p2[ib])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    t = ((p2[ia] - p1[ia]) * d2[1] - (p2[ib] - p1[ib]) * d2[0]) / den
    return t
def split_rods(ids, rodmap, la, lb, t_cross):
    """ЛИРА стержендерін (ұштары la→lb) қиылыс параметрі бойынша екі жартыға бөледі"""
    g1, g2 = [], []
    L2 = sum((lb[k] - la[k]) ** 2 for k in range(3))
    for i in ids:
        r = rodmap[i]; m = [(r['p'][k] + r['q'][k]) / 2 - la[k] for k in range(3)]
        t = sum(m[k] * (lb[k] - la[k]) for k in range(3)) / L2
        (g1 if t < t_cross else g2).append(i)
    return g1, g2
byid12 = {r['i']: r for r in by_s[12]}
sv = []   # chains
for ids, a_, b_ in merge_chains(by_s[12]):
    if a_[2] > b_[2]: a_, b_ = b_, a_        # a - төменгі
    zl_lo, zl_hi = round(a_[2], 3), round(b_[2], 3)
    plane_y = round(a_[1], 3)
    if abs(zl_hi - 7.9) < 1e-6 or abs(zl_hi - 8.9) < 1e-6: mk = 'СВ1' if abs(zl_hi - 7.9) < 1e-6 else 'СВ2'
    else: mk = {(0.35, 5.0): 'СВ3', (0.35, 2.8): 'СВ4', (2.8, 5.0): 'СВ5'}[(zl_lo, zl_hi)]
    tor = any(abs(v) < 1e-6 or abs(v - 60) < 1e-6 for v in (a_[0], b_[0]))
    xa, xb = XM(a_[0]), XM(b_[0]); sg = 1.0 if xb > xa else -1.0
    (xl, zlw), (xh, zhg) = SV_END[(mk, tor)]
    Y = y_sv(plane_y)
    p = (xa + sg * xl, Y, zlw); q = (xb - sg * xh, Y, zhg)
    sv.append(dict(mk=mk, tor=tor, p=p, q=q, ids=ids, la=a_, lb=b_, sg=sg, key=(mk, plane_y, round(min(xa, xb)), round(max(xa, xb)))))
grp = collections.defaultdict(list)
for c in sv: grp[c['key']].append(c)
for key, cs in sorted(grp.items(), key=lambda kv: kv[0]):
    assert len(cs) == 2, ('СВ X-крест жұбы емес', key, len(cs))
    solid = [c for c in cs if c['sg'] > 0][0]; cut = [c for c in cs if c['sg'] < 0][0]    # тұтас: төменгі түйіні −X колоннада (x өскен сайын көтерілетін, uzel_09)
    t = line_isect(solid['p'], solid['q'], cut['p'], cut['q'])
    C = tuple(solid['p'][k] + t * (solid['q'][k] - solid['p'][k]) for k in range(3))
    L = math.sqrt(sum((cut['q'][k] - cut['p'][k]) ** 2 for k in range(3))); u = tuple((cut['q'][k] - cut['p'][k]) / L for k in range(3))
    rr = SV_R[(cut['mk'], cut['tor'])]
    tc = math.sqrt(sum((C[k] - cut['p'][k]) ** 2 for k in range(3))) / L
    g1, g2 = split_rods(cut['ids'], byid12, cut['la'], cut['lb'], tc)
    solid['pieces'] = [(solid['p'], solid['q'], solid['ids'], 'тұтас')]
    c1 = tuple(C[k] - rr * u[k] for k in range(3)); c2 = tuple(C[k] + rr * u[k] for k in range(3))
    cut['pieces'] = [(cut['p'], c1, g1, 'кесілген-1'), (c2, cut['q'], g2, 'кесілген-2')]
for c in sv:
    for pp, qq, ids_, tag in c['pieces']:
        add(c['mk'], 'B', tuple(pp), tuple(qq), 'tube', rodids=ids_, extra='uzel_09 ' + tag)

# ============ ГОРИЗОНТАЛЬ СВЯЗЬ ГС1 / ГС2 ============
byid13 = {r['i']: r for r in by_s[13]}
def gs_wp_y(yl, oyl):
    y3 = round(yl, 3)
    if y3 == 0.0: return 532.0                                       # карниз: колонна ішкі беті (uzel_15б)
    if y3 == 36.0: return 35468.0
    if y3 == 18.0: return 17734.0 if oyl < 18 else 18266.0          # жота: колонна полкасының сыртқы беті (uzel_15в)
    return y3 * 1000.0
def hyp(x, y): return math.sqrt(x * x + y * y)
def gs_s(yl, oyl):
    de = min(yl, 36 - yl); od = min(oyl, 36 - oyl)                   # құбыр ұшы WP-тен (uzel_15 «құбыр ұшы» нүктелерінің модулі)
    if de < 1e-6: return hyp(258.0, 235.1)                           # карниз (15б)
    if abs(de - 6) < 1e-6: return hyp(258.0, 235.1) if od < de else hyp(253.9, 253.9)   # 15: −y (42,34°) / +y (45°)
    if abs(de - 12) < 1e-6: return hyp(268.0, 268.0) if od < de else hyp(270.4, 258.4)  # 15а: 45° / жотаға 43,70°
    return hyp(306.5, 292.9)                                         # жота (15в)
GS_R = {0: 96.0, 6: 90.0, 12: 93.0}                                  # 15г: кесілген жартылардың ұшы қиылыстан (панель d = 0, 6, 12 м)
gs = []
for ids, a_, b_ in merge_chains(by_s[13]):
    long_ = abs(abs(b_[1] - a_[1]) - 12) < 1e-6
    if long_:   # ГС2 (ұзын раскос, 2 аралық) ригельден өтпейді: аралық рама осінде бөлінеді (КМ_ҚАТЕЛЕР #13, ранг Б1 > трубка)
        if a_[0] > b_[0]: a_, b_ = b_, a_
        pm = ((a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2, 0)
        parts = [(a_, pm, [i for i in ids if max(byid13[i]['p'][0], byid13[i]['q'][0]) <= pm[0] + 1e-6]), (pm, b_, [i for i in ids if min(byid13[i]['p'][0], byid13[i]['q'][0]) >= pm[0] - 1e-6])]
    else: parts = [(a_, b_, ids)]
    for aa, bb, sg_ in parts:
        if aa[0] > bb[0]: aa, bb = bb, aa
        ya_l, yb_l = aa[1], bb[1]
        wa = gs_wp_y(ya_l, yb_l); wb = gs_wp_y(yb_l, ya_l)
        pa = (XM(aa[0]), wa, neu_raf(wa) - 1.0); pb = (XM(bb[0]), wb, neu_raf(wb) - 1.0)     # ГС осі = гусет үсті + 3 = ригель осі − 1 (uzel_15)
        gs.append(dict(mk='ГС2' if long_ else 'ГС1', pa=pa, pb=pb, ya=ya_l, yb=yb_l, xa=aa[0], xb=bb[0], ids=list(sg_), la=aa, lb=bb))
def gs_ends(g):
    pa, pb = g['pa'], g['pb']; L2 = hyp(pb[0] - pa[0], pb[1] - pa[1]); u = ((pb[0] - pa[0]) / L2, (pb[1] - pa[1]) / L2)
    sa, sb_ = gs_s(g['ya'], g['yb']), gs_s(g['yb'], g['ya'])
    def at(s): return (pa[0] + u[0] * s, pa[1] + u[1] * s, pa[2] + (pb[2] - pa[2]) * s / L2)
    return at(sa), at(L2 - sb_)
for g in gs: g['p'], g['q'] = gs_ends(g)
gk = collections.defaultdict(list)
for g in gs: gk[(g['mk'], round(g['xa'], 3), round(g['xb'], 3), round(min(g['ya'], g['yb']), 3), round(max(g['ya'], g['yb']), 3))].append(g)
for key, gl in sorted(gk.items(), key=lambda kv: kv[0]):
    if len(gl) == 1:
        g = gl[0]; g['pieces'] = [(g['p'], g['q'], g['ids'], '')]; continue
    assert len(gl) == 2, ('ГС X-крест', key)
    gmean = (key[3] + key[4]) / 2.0
    rising = [g for g in gl if g['yb'] > g['ya']][0]; falling = [g for g in gl if g['yb'] < g['ya']][0]     # жоспарда x өскен сайын y өсетін = rising
    solid, cut = (rising, falling) if gmean < 18 else (falling, rising)          # G жартысында айналы (uzel_15г)
    t = line_isect(solid['pa'], solid['pb'], cut['pa'], cut['pb'], 0, 1)
    C = tuple(solid['pa'][k] + t * (solid['pb'][k] - solid['pa'][k]) for k in range(3))
    # кесілген диагональ: ұшы p → C − r·u, C + r·u → q (жоспар бойымен өлшенген r)
    pa, pb = cut['pa'], cut['pb']; L2 = hyp(pb[0] - pa[0], pb[1] - pa[1]); u2 = ((pb[0] - pa[0]) / L2, (pb[1] - pa[1]) / L2)
    tcut = hyp(C[0] - pa[0], C[1] - pa[1]) / L2
    rr = GS_R[int(round(min(min(key[3], 36 - key[3]), min(key[4], 36 - key[4]))))]
    def at(s): return (pa[0] + u2[0] * s, pa[1] + u2[1] * s, pa[2] + (pb[2] - pa[2]) * s / L2)
    s_c = tcut * L2
    c1 = at(s_c - rr); c2 = at(s_c + rr)
    g1, g2 = split_rods(cut['ids'], byid13, cut['la'], cut['lb'], tcut)
    solid['pieces'] = [(solid['p'], solid['q'], solid['ids'], 'тұтас')]
    cut['pieces'] = [(cut['p'], c1, g1, 'кесілген-1'), (c2, cut['q'], g2, 'кесілген-2')]
for g in gs:
    for pp, qq, ids_, tag in g['pieces']:
        pp2, qq2 = (pp, qq) if pp[0] <= qq[0] else (qq, pp)
        add(g['mk'], 'B', tuple(pp2), tuple(qq2), 'tube', rodids=ids_, extra=('uzel_15г ' + tag) if tag else '')

'''
src = src[:a] + new + src[b:]
open(P, 'w', encoding='utf-8').write(src)
print('part 2 written')
