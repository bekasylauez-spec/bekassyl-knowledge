# -*- coding: utf-8 -*-
# frame_changes.md кестесінің әр жолына МОДЕЛЬДЕН өлшенген мән + ✓/✗. Кіріс: model_dump.tsv (Revit геометриясы), measure.tsv (тік сызықпен кесу), _v1\model_dump.tsv.
# Күтілетін сандар — ПАСПОРТТАРДАН қолмен жазылған (gen.py-ға тәуелсіз). Шығыс: frame_changes_check.md, _roof_plane.txt
import math, collections, os
H = os.path.dirname(os.path.abspath(__file__))
def f(x): return float(x.replace(',', '.')) if x not in ('', None) else None
D = {}
for l in open(os.path.join(H, 'model_dump.tsv'), encoding='utf-8'):
    t = l.rstrip('\n').split('\t')
    D[t[2]] = dict(mark=t[1], p=tuple(f(x) for x in t[5:8]), q=tuple(f(x) for x in t[8:11]), bb=tuple(f(x) for x in t[11:17]), vol=f(t[17]), ends=t[18] if len(t) > 18 else '')
def by(mk): return [d for d in D.values() if d['mark'] == mk]
FR = [150.0] + [6000.0 * i for i in range(1, 10)] + [59850.0]
def near(v, arr): return min(arr, key=lambda a: abs(a - v))
rows = []   # (№, тақырып, күтілетін, өлшенген, ok, ескерту)
def add(n, title, exp, meas, ok, note=''): rows.append((n, title, exp, meas, ok, note))
def rng(vals): return '%.2f' % vals[0] if min(vals) == max(vals) else '%.2f…%.2f' % (min(vals), max(vals))
def within(vals, target, tol): return all(abs(v - target) <= tol for v in vals)
# ---- колонналар
k1 = by('К1'); ag = [d['bb'][5] for d in k1 if abs((d['bb'][1] + d['bb'][4]) / 2 - 266) < 1 or abs((d['bb'][1] + d['bb'][4]) / 2 - 35734) < 1]
dd = [d['bb'][5] for d in k1 if abs((d['bb'][1] + d['bb'][4]) / 2 - 18000) < 1]
add(1, 'К1 A/G басы (z max, bbox геометриядан)', '8286', '%s (n=%d)' % (rng(ag), len(ag)), within(ag, 8286, 0.05) and len(ag) == 22)
add(2, 'К1 D басы', '9293', '%s (n=%d)' % (rng(dd), len(dd)), within(dd, 9293, 0.05) and len(dd) == 11, 'жазық үсті (Λ-кесу — узел бөлшегі)')
k2 = by('К2'); k2t = [d['bb'][5] for d in k2 if (d['bb'][3] - d['bb'][0]) > 400]; k2a = [d['bb'][5] for d in k2 if (d['bb'][3] - d['bb'][0]) < 400]
add(3, 'К2 торец басы', '8798', '%s (n=%d)' % (rng(k2t), len(k2t)), within(k2t, 8798, 0.05) and len(k2t) == 4, 'жазық үсті (еңіспен кесу — узел бөлшегі)')
k3 = [d['bb'][5] for d in by('К3')]
add(4, 'К3 торец басы', '9098', '%s (n=%d)' % (rng(k3), len(k3)), within(k3, 9098, 0.05) and len(k3) == 4)
add(5, 'К2 антресоль басы', '3886', '%s (n=%d)' % (rng(k2a), len(k2a)), within(k2a, 3886, 0.05) and len(k2a) == 12)
# ---- ригель: тік сызықпен кесу (measure.tsv)
M = {}
for l in open(os.path.join(H, 'measure.tsv'), encoding='utf-8'):
    t = l.rstrip('\n').split('\t')
    if len(t) < 4 or t[3] == '-': continue
    segs = [tuple(float(v.replace(',', '.')) for v in s.strip().split('..')) for s in t[3].split('|')]
    M[(t[0], round(f(t[1])), round(f(t[2]), 1))] = (min(s[0] for s in segs), max(s[1] for s in segs))
def bot(mark, x, y): return M[(mark, x, y)][0]
b1 = by('Б1'); b1a = [d for d in b1 if d['p'][1] < 18000]; b1g = [d for d in b1 if d['p'][1] > 18000]
ok6 = all(abs(bot('Б1-54', 150, y) - 8311.0) <= 0.05 for y in (0.5, 100.0, 300.0, 600.0)) and abs(bot('Б1-54', 150, 3000.0) - (8311 + 507 * 2400 / 5400)) <= 0.1 and abs(bot('Б1-54', 150, 6000.0) - 8818.0) <= 0.1 and abs(bot('Б1-54', 150, 6599.5) - 8848.0) <= 0.1
ok6 = ok6 and all(abs(bot('Б1-57', 150, y) - e) <= 0.1 for y, e in ((35999.5, 8311.0), (35700.0, 8311.0), (35400.0, 8311.0), (30000.0, 8818.0), (29400.5, 8848.0)))
add(6, 'Б1 табаны (z, тік сызықпен кесу; A және G)', 'y 0.5/100/300/600: 8311; y 3000: 8536.33; 6000: 8818; 6599.5: 8848', 'A: %s; G: %s' % (', '.join('y%s=%.2f' % (str(y).rstrip('0').rstrip('.'), bot('Б1-54', 150, y)) for y in (0.5, 100.0, 300.0, 600.0, 3000.0, 6000.0, 6599.5)), ', '.join('y%s=%.2f' % (str(y).rstrip('0').rstrip('.'), bot('Б1-57', 150, y)) for y in (35999.5, 35700.0, 35400.0, 30000.0, 29400.5))), ok6, 'ұшы тік: y=0.5-те төменгі белдеу бар (қиғаш ұшта болмас еді)')
ya = sorted(set((round(d['bb'][1], 1), round(d['bb'][4], 1)) for d in b1a)); yg = sorted(set((round(d['bb'][1], 1), round(d['bb'][4], 1)) for d in b1g))
b2 = by('Б2'); b2a = [d for d in b2 if d['p'][1] < 18000]; b2g = [d for d in b2 if d['p'][1] > 18000]
sa = sorted(set((round(d['bb'][1], 1), round(d['bb'][4], 1)) for d in b2a)); sg = sorted(set((round(d['bb'][1], 1), round(d['bb'][4], 1)) for d in b2g))
add(7, 'Б1 / Б2 түйісуі (геометрия bbox y)', 'Б1 0…6600, Б2 6600…12500; G: 29400…36000, 23500…29400', 'Б1 A %s (n=%d), G %s (n=%d); Б2 A %s, G %s' % (ya, len(b1a), yg, len(b1g), sa, sg), ya == [(0.0, 6600.0)] and yg == [(29400.0, 36000.0)] and sa == [(6600.0, 12500.0)] and sg == [(23500.0, 29400.0)] and len(b1a) == len(b1g) == 11)
ok8 = abs(bot('Б2-55', 150, 6600.5) - 8848.0) <= 0.1 and abs(bot('Б2-55', 150, 12499.5) - 9143.0) <= 0.1 and abs(bot('Б2-55', 150, 9000.0) - 8968.0) <= 0.1
add(8, 'Б2 табаны (тік кесу)', 'y 6600.5: 8848; 9000: 8968; 12499.5: 9143 (ұштары тік)', 'y6600.5=%.2f; 9000=%.2f; 12499.5=%.2f' % (bot('Б2-55', 150, 6600.5), bot('Б2-55', 150, 9000.0), bot('Б2-55', 150, 12499.5)), ok8)
b3 = by('Б3'); b3a = [d for d in b3 if d['p'][1] < 23000 and d['p'][1] > 12000 and d['q'][1] > 17000 and d['q'][1] < 18000]; b3g = [d for d in b3 if d['q'][1] > 18000 and d['q'][1] < 19000]
ra = sorted(set(round(d['bb'][4], 1) for d in b3a)); rg = sorted(set(round(d['bb'][1], 1) for d in b3g))
ok9 = ra == [17990.0] and rg == [18010.0] and len(b3a) == len(b3g) == 11 and abs(bot('Б3-56', 150, 17989.5) - 9317.67) <= 0.1 and abs(bot('Б3-59', 150, 18010.5) - 9317.67) <= 0.1 and abs(bot('Б3-56', 150, 12500.5) - 9143.0) <= 0.1 and abs(bot('Б3-56', 150, 15000.0) - (9143 + 175 * 2500 / 5500)) <= 0.1
add(9, 'Б3 жотада (геометрия y max / min; табан)', 'A жағы ұшы y=17990, G жағы y=18010; табан 17989.5: 9317.67; 12500.5: 9143; 15000: 9222.5', 'A ymax %s (n=%d), G ymin %s (n=%d); табан %.2f / %.2f / %.2f / %.2f' % (ra, len(b3a), rg, len(b3g), bot('Б3-56', 150, 17989.5), bot('Б3-59', 150, 18010.5), bot('Б3-56', 150, 12500.5), bot('Б3-56', 150, 15000.0)), ok9, 'бір отправочная марка Б3 12,5…23,5 м = 2 дана (жота пластинасы 20 — узел бөлшегі)')
# ---- Р1 / Р2 / Р3
def rel_ends(d):   # (|p.x − рама|, |q.x − рама|)
    return abs(d['p'][0] - near(d['p'][0], FR)), abs(d['q'][0] - near(d['q'][0], FR))
r1 = by('Р1'); lo = [d for d in r1 if abs(d['p'][2] - 6000) < 0.1]; up = [d for d in r1 if abs(d['p'][2] - 6000) >= 0.1]
yl = collections.Counter(round(d['p'][1], 1) for d in lo); yu = collections.Counter(round(d['p'][1], 1) for d in up)
okl = dict(yl) == {294.0: 10, 18014.0: 10, 35762.0: 10} and all(abs(a - 150) < 0.06 and abs(b - 150) < 0.06 for a, b in map(rel_ends, lo))
add(10, 'Р1 төменгі (+6000): Y, ұштары', 'Y 294 / 18014 / 35762 (10-нан); ұшы рама осінен 150', 'Y %s; ұштары %s' % (dict(sorted(yl.items())), rng([x for d in lo for x in rel_ends(d)])), okl)
zu = [d['p'][2] for d in up]
oku = dict(yu) == {288.0: 10, 35756.0: 10} and all(abs(a - 254) < 0.06 and abs(b - 254) < 0.06 for a, b in map(rel_ends, up)) and within(zu, 8641.6, 0.05)
add(11, 'Р1 жоғарғы: Y, ұштары, z', 'Y 288 / 35756; ұшы 254; z 8641.6', 'Y %s; ұштары %s; z %s' % (dict(sorted(yu.items())), rng([x for d in up for x in rel_ends(d)]), rng(zu)), oku)
r2 = by('Р2')
ok12 = len(r2) == 10 and all(abs(d['p'][1] - 18014) < 0.01 and abs(d['p'][2] - 9593) < 0.05 for d in r2) and all(abs(a - 325) < 0.06 and abs(b - 325) < 0.06 for a, b in map(rel_ends, r2))
add(12, 'Р2: Y, z, ұштары', 'Y 18014; z 9593; ұшы 325', 'Y %s; z %s; ұштары %s (n=%d)' % (rng([d['p'][1] for d in r2]), rng([d['p'][2] for d in r2]), rng([x for d in r2 for x in rel_ends(d)]), len(r2)), ok12, 'v1: 175')
r3 = by('Р3'); okk = True; txt = []
for yy, e, zz in ((6000, 254, 9043), (30000, 254, 9043), (12000, 269, 9343), (24000, 269, 9343)):
    sel = [d for d in r3 if abs(d['p'][1] - yy) < 0.1]; ee = [x for d in sel for x in rel_ends(d)]
    txt.append('y%d: n=%d ұш %s z %s' % (yy, len(sel), rng(ee), rng([d['p'][2] for d in sel]))); okk = okk and len(sel) > 0 and within(ee, e, 0.06) and within([d['p'][2] for d in sel], zz, 0.05)
add(13, 'Р3: ұштары, z', 'B/F (y 6000/30000): 254, z 9043; C/E (12000/24000): 269, z 9343', '; '.join(txt) + ' (n=%d)' % len(r3), okk and len(r3) == 28, 'v1: 140')
# ---- СВ
SVE = {'СВ1': [(293.1, 6192.5), (278.3, 8425.0), (298.9, 6191.7), (274.7, 8429.4)], 'СВ2': [(231.7, 6203.6), (330.9, 9301.2), (233.2, 6201.1), (328.7, 9307.3)],
       'СВ3': [(166.1, 1476.9), (197.9, 5781.8)], 'СВ4': [(166.3, 1416.1), (728.5, 3446.2)], 'СВ5': [(783.2, 4022.6), (327.1, 5811.8)]}
COLS = FR
def ends_of(d): return [d['p'], d['q']]
res = {}
for mk, exp in SVE.items():
    ms = by(mk); matched = 0; tot = 0; bad = []; ys = set()
    for d in ms:
        ys.add(round(d['p'][1], 1))
        for e in ends_of(d):
            xc = near(e[0], COLS)
            if abs(e[0] - xc) > 900: continue                 # кесілген диагональдың орта ұшы — бөлек (r)
            tot += 1; loc = (abs(e[0] - xc), e[2])
            if any(abs(loc[0] - a) <= 0.06 and abs(loc[1] - b) <= 0.06 for a, b in exp): matched += 1
            else: bad.append((round(loc[0], 2), round(loc[1], 2)))
    res[mk] = (matched, tot, sorted(ys), bad[:3])
for n, mk, title in ((14, 'СВ1', 'СВ1 (A/G): ұштары (колонна осінен x; z)'), (15, 'СВ2', 'СВ2 (D)'), (16, 'СВ3', 'СВ3'), (17, 'СВ4', 'СВ4'), (18, 'СВ5', 'СВ5')):
    m_, t_, ys, bad = res[mk]; expy = {'СВ1': [266.0, 35734.0], 'СВ2': [17986.0], 'СВ3': [266.0, 17986.0], 'СВ4': [266.0, 35734.0], 'СВ5': [266.0, 35734.0]}[mk]
    add(n, title, '; '.join('(%.1f; %.1f)' % e for e in SVE[mk]) + '; жазықтық Y ' + '/'.join('%g' % y for y in expy), '%d / %d ұш сәйкес; Y = %s%s' % (m_, t_, ys, '; сәйкес емес: %s' % bad if bad else ''), m_ == t_ and t_ > 0 and ys == expy)
# ---- X-крест (СВ): кесілген диагональ жартылары
def isect2(p1, q1, p2, q2, ia=0, ib=2):
    d1 = (q1[ia] - p1[ia], q1[ib] - p1[ib]); d2 = (q2[ia] - p2[ia], q2[ib] - p2[ib]); den = d1[0] * d2[1] - d1[1] * d2[0]
    return ((p2[ia] - p1[ia]) * d2[1] - (p2[ib] - p1[ib]) * d2[0]) / den
SVR = {'СВ1': (239.0, 234.0), 'СВ2': (184.0, 180.0), 'СВ3': (147.0, 147.0), 'СВ4': (247.0, 247.0), 'СВ5': (265.0, 265.0)}
cross_ok = 0; cross_n = 0; cross_bad = []; per = collections.Counter()
for mk in SVR:
    ms = by(mk); full = []; pieces = []
    for d in ms:
        near_ends = [abs(e[0] - near(e[0], COLS)) <= 900 for e in ends_of(d)]
        (full if all(near_ends) else pieces).append(d)
    for fd in full:
        # осы тұтас диагональмен қиылысатын бөліктер (бір Y, бір аралық)
        mypieces = [d for d in pieces if abs(d['p'][1] - fd['p'][1]) < 0.1 and min(fd['p'][0], fd['q'][0]) - 800 <= min(d['p'][0], d['q'][0]) and max(d['p'][0], d['q'][0]) <= max(fd['p'][0], fd['q'][0]) + 800]
        if len(mypieces) != 2: cross_bad.append((mk, fd['p'], len(mypieces))); cross_n += 1; continue
        cross_n += 1; per[mk] += 1
        # кесілген диагональ осі: екі бөліктің сыртқы ұштарынан
        outs = []
        for d in mypieces:
            for e in ends_of(d):
                if abs(e[0] - near(e[0], COLS)) <= 900: outs.append(e)
        t = isect2(fd['p'], fd['q'], outs[0], outs[1]); C = tuple(fd['p'][k] + t * (fd['q'][k] - fd['p'][k]) for k in range(3))
        rr = []
        for d in mypieces:
            inner = [e for e in ends_of(d) if abs(e[0] - near(e[0], COLS)) > 900][0]; rr.append(math.sqrt(sum((inner[k] - C[k]) ** 2 for k in range(3))))
        tor = any(abs(near(e[0], COLS) - c) < 1 for e in outs for c in (150.0, 59850.0))
        exp = SVR[mk][1] if tor else SVR[mk][0]
        if all(abs(r_ - exp) <= 0.3 for r_ in rr): cross_ok += 1
        else: cross_bad.append((mk, round(rr[0], 1), round(rr[1], 1), exp))
add(19, 'СВ X-крест: тұтас + екі бөлікке кесілген, ұштары қиылыстан r', 'r: СВ1 239 / 234 (торец), СВ2 184 / 180, СВ3 147, СВ4 247, СВ5 265; 21 крест', '%d / %d крест сәйкес (%s)%s' % (cross_ok, cross_n, ', '.join('%s %d' % (k, v) for k, v in sorted(per.items())), '; сәйкес емес: %s' % cross_bad[:4] if cross_bad else ''), cross_ok == cross_n == 21, 'жартылар 2 дана: СВ1 24, СВ2 12, СВ3 9, СВ4 9, СВ5 9')
# ---- ГС
GSS = [math.hypot(258.0, 235.1), math.hypot(253.9, 253.9), math.hypot(268.0, 268.0), math.hypot(270.4, 258.4), math.hypot(306.5, 292.9)]
WPY = [532.0, 6000.0, 12000.0, 17734.0, 18266.0, 24000.0, 30000.0, 35468.0]
gs = by('ГС1') + by('ГС2'); okg = 0; totg = 0; badg = []; swp = collections.Counter()
for d in gs:
    for e in ends_of(d):
        xc = near(e[0], FR); wy = near(e[1], WPY); s = math.hypot(e[0] - xc, e[1] - wy)
        if s > 700: continue
        totg += 1; swp[wy] += 1
        if any(abs(s - g) <= 0.12 for g in GSS): okg += 1
        else: badg.append((round(s, 2), xc, wy))
add(20, 'ГС түйіндері (WP y) — құбыр ұштары WP-ке қатысты', 'WP y: 532 / 6000 / 12000 / 17734 / 18266 / 24000 / 30000 / 35468', 'WP бойынша ұштар: %s' % dict(sorted(swp.items())), set(swp) == set(WPY), 'v1: карниз 0 / 36000, жота 18000')
add(21, 'ГС ұштары WP-тен (жоспар бойымен)', '349.05 / 359.07 / 379.0 / 374.0 / 423.95', '%d / %d ұш сәйкес%s' % (okg, totg, '; сәйкес емес: %s' % badg[:4] if badg else ''), okg == totg and totg > 0, 'v1: WP-тен 198…247')
# ГС крест: r (жоспар) — кесілген жартылар
GSR = {0: 96.0, 6: 90.0, 12: 93.0}
gx_ok = 0; gx_n = 0; gx_bad = []
for mk in ('ГС1', 'ГС2'):
    ms = by(mk)
    for fd in ms:
        # тұтас диагональ: екі ұшы да түйіннен ≤ 700
        if not all(min(math.hypot(e[0] - near(e[0], FR), e[1] - near(e[1], WPY)) for _ in [0]) <= 700 for e in ends_of(fd)): continue
        mypieces = [d for d in ms if d is not fd and not all(math.hypot(e[0] - near(e[0], FR), e[1] - near(e[1], WPY)) <= 700 for e in ends_of(d))
                    and min(fd['p'][0], fd['q'][0]) - 400 <= min(d['p'][0], d['q'][0]) and max(d['p'][0], d['q'][0]) <= max(fd['p'][0], fd['q'][0]) + 400
                    and min(fd['p'][1], fd['q'][1]) - 400 <= min(d['p'][1], d['q'][1]) and max(d['p'][1], d['q'][1]) <= max(fd['p'][1], fd['q'][1]) + 400]
        # екі бөлік ортақ өске жатуы тиіс және тұтас диагональ қиылыс нүктесінде
        cand = []
        for a in mypieces:
            for b in mypieces:
                if a is b: continue
                # a, b бір түзуде ме
                oa = [e for e in ends_of(a) if math.hypot(e[0] - near(e[0], FR), e[1] - near(e[1], WPY)) <= 700]; ob = [e for e in ends_of(b) if math.hypot(e[0] - near(e[0], FR), e[1] - near(e[1], WPY)) <= 700]
                if not oa or not ob: continue
                if oa[0] == ob[0]: continue
                cand.append((a, b, oa[0], ob[0]))
        if not cand: continue
        a, b, ea, eb = cand[0]
        t = isect2(fd['p'], fd['q'], ea, eb, 0, 1); C = tuple(fd['p'][k] + t * (fd['q'][k] - fd['p'][k]) for k in range(3))
        ia = [e for e in ends_of(a) if e is not ea][0]; ib = [e for e in ends_of(b) if e is not eb][0]
        ra = math.hypot(ia[0] - C[0], ia[1] - C[1]); rb = math.hypot(ib[0] - C[0], ib[1] - C[1])
        LY = {532.0: 0, 6000.0: 6, 12000.0: 12, 17734.0: 18, 18266.0: 18, 24000.0: 24, 30000.0: 30, 35468.0: 36}; wy = [LY[near(ea[1], WPY)], LY[near(eb[1], WPY)]]; de = min(min(wy[0], 36 - wy[0]), min(wy[1], 36 - wy[1])); exp = GSR[int(de)]
        gx_n += 1
        if abs(ra - exp) <= 0.3 and abs(rb - exp) <= 0.3: gx_ok += 1
        else: gx_bad.append((mk, round(ra, 1), round(rb, 1), exp))
add(22, 'ГС X-крест: кесілген жартылар ұшы қиылыстан r (жоспар)', 'r: 96 (0…6 м), 90 (6…12 м), 93 (12…17,7 м); 12 крест', '%d / %d крест сәйкес%s' % (gx_ok, gx_n, '; сәйкес емес: %s' % gx_bad[:4] if gx_bad else ''), gx_ok == gx_n == 12, 'ГС1 32 (24+8), ГС2 28 (24+4)')
# ---- прогондар
pr = by('Пр1'); ok23 = True; ys_k = collections.Counter(); xs = []
for d in pr:
    A = d['p'][1] < 18000
    y_model = d['p'][1] + (5.9926 if A else -5.9926)
    if min(y_model, 36000 - y_model) < 400: ys_k[round(y_model, 1)] += 1
    x0, x1 = d['bb'][0], d['bb'][3]; fa = near(x0 + 100, FR); fb = near(x1 - 100, FR)
    e0 = fa - 250 if fa < 200 else fa + 100; e1 = fb + 250 if fb > 59800 else fb - 100
    if x0 < 0: e0 = -100.0
    xs.append((abs(x0 - e0), abs(x1 - e1)))
add(23, 'Пр1 карниз прогоны Y', '266 (A), 35734 (G); әрқайсысы 10', str(dict(sorted(ys_k.items()))), dict(ys_k) == {266.0: 10, 35734.0: 10}, 'v1: 0 / 36000')
add(24, 'Пр1 ұштары (геометрия bbox x)', 'рама осінен ±100; торецте −100 және 60100', 'max ауытқу = %.2f мм (n=%d)' % (max(max(a, b) for a, b in xs), len(pr)), max(max(a, b) for a, b in xs) <= 0.1 and len(pr) == 260, 'жалпы: бірінші/соңғы аралықта x −100…5900 және 54100…60100')
# ---- ПБ1
pb = by('ПБ1'); e_ = [(abs(d['bb'][0] - (near(d['bb'][0] - 10, FR) + 10)), abs(d['bb'][3] - (near(d['bb'][3] + 10, FR) - 10))) for d in pb]
add(25, 'ПБ1 ұштары (геометрия bbox x)', 'рама осінен ±10 (ось 1: 160; ось 11: 59840)', 'max ауытқу = %.2f мм (n=%d); мысал x %s…%s' % (max(max(a, b) for a, b in e_), len(pb), rng([min(d['bb'][0] for d in pb)]), rng([max(d['bb'][3] for d in pb)])), max(max(a, b) for a, b in e_) <= 0.1 and len(pb) == 40)
# ---- Б4 / Б5
b4 = by('Б4'); bad4 = []; cnt4 = collections.Counter()
K2A = [6000.0 * i for i in (2, 3, 4, 5)] + [6000.0 * i for i in (7, 8, 9, 10)]    # антресоль К2 осьтері (қатарға қарай): тек жуық сүзгі үшін
def exp_x_end(y, x, lo):   # Б4 X: күтілетін ұштар
    if abs(y - 266) < 1 or abs(y - 35734) < 1: return near(x, FR) + (24 if lo else -24)      # К1 стенкасы: ±24
    if x > 59000: return 59664.0 if not lo else None
    if x < 1000: return 336.0 if lo else None
    return near(x, [6000.0 * i for i in range(0, 11)]) + (25 if lo else -25)                    # К2 антресоль стенкасы ±25
for d in b4:
    if abs(d['p'][1] - d['q'][1]) < 0.1:   # X бағыт
        x0, x1 = sorted((d['p'][0], d['q'][0])); y = d['p'][1]
        for lo_, x in ((True, x0), (False, x1)):
            e = exp_x_end(y, x if lo_ else x, lo_)
            if e is None:
                e = 59664.0 if x > 59000 else 336.0
            if abs(x - e) > 0.1: bad4.append(('X', y, x, e))
            cnt4['X'] += 1
    else:
        y0, y1 = sorted((d['p'][1], d['q'][1])); x = d['p'][0]
        exp_lo = {532: 552.0, 30216: 30236.0, 30150: 30025.0}; exp_hi = {35468: 35448.0, 5784: 5764.0, 5850: 5975.0}
        # төмен ұш (y0) нысанасы: 552 (К1 A), 30236 (К2 F полка), 30025 (К2 торец F стенка); жоғары (y1): 35448, 5764, 5975
        okl_ = any(abs(y0 - v) < 0.1 for v in (552.0, 30236.0, 30025.0)); okh_ = any(abs(y1 - v) < 0.1 for v in (35448.0, 5764.0, 5975.0))
        cnt4['Y'] += 2
        if not okl_: bad4.append(('Y-lo', x, y0))
        if not okh_: bad4.append(('Y-hi', x, y1))
v1d = {}
for l in open(os.path.join(H, '_v1', 'model_dump.tsv'), encoding='utf-8'):
    t = l.rstrip('\n').split('\t'); v1d[t[2]] = t
add(26, 'Б4 X ұштары (К1 стенкасы ±24 / К2 антресоль стенкасы ±25 / К2 торец полкасы 59664, 336)', 'x ұштары: рама осінен ±24 (A/G), ±25 (B/F); 59664 / 336', '%d ұш тексерілді, сәйкес емес: %d %s' % (cnt4['X'], len([b for b in bad4 if b[0] == 'X']), [b for b in bad4 if b[0] == 'X'][:3]), cnt4['X'] > 0 and not [b for b in bad4 if b[0] == 'X'], 'v1: полка шеті ±150 / 59684 / 316')
add(29, 'Б4 Y ұштары (К1 полкасы 552 / 35448; К2 антресоль полкасы 5764 / 30236; К2 торец стенкасы 5975 / 30025)', 'y ұштары: 552, 35448, 5764, 30236, 5975, 30025', '%d ұш тексерілді, сәйкес емес: %d %s' % (cnt4['Y'], len([b for b in bad4 if b[0].startswith('Y')]), [b for b in bad4 if b[0].startswith('Y')][:3]), cnt4['Y'] > 0 and not [b for b in bad4 if b[0].startswith('Y')], 'v1: 532 / 35468 / 5784 / 30216 / 5850 / 30150')
b5 = by('Б5'); eb = []
for d in b5:
    x0, x1 = d['bb'][0], d['bb'][3]; eb.append((abs(x0 - (near(x0 - 23, FR) + 23)), abs(x1 - (near(x1 + 23, FR) - 23))))
okn = abs(M[('Б5-243', 54028, 4000.0)][0] - 3606) <= 0.05 and abs(M[('Б5-243', 54028, 4000.0)][1] - 3870) <= 0.05 and ('Б5-243', 54028, 4090.0) not in M and abs(M[('Б5-243', 54223, 4000.0)][0] - 3576) <= 0.05 and abs(M[('Б5-243', 54223, 4000.0)][1] - 3900) <= 0.05 and ('Б5-243', 54223, 4090.0) in M
add(32, 'Б5 ұштары (стенка осінен 23) және ойық', 'x: рама осінен 23; ұштан 117-ге дейін белдеу жоқ, стенка z 3606…3870', 'ұш max ауытқу %.2f мм (n=%d); Б5-243: x+5/+100 (ойық): z 3606…3870, белдеу (y=4090) жоқ; x+200: 3576…3900, белдеу бар' % (max(max(a, b) for a, b in eb), len(b5)), max(max(a, b) for a, b in eb) <= 0.1 and len(b5) == 24 and okn, 'R15 бұрыштары жоқ (тікбұрышты)')
kb = by('КБ1'); kbo = []
for d in kb:
    y0, y1 = d['bb'][1], d['bb'][4]; kbo.append((round(y0, 1), round(y1, 1)))
exp_kb = {(532.0, 1000.0), (17200.0, 17734.0), (18266.0, 18800.0), (35000.0, 35468.0)}
add(33, 'КБ1 (өзгеріс жоқ): y аралығы, үсті', '532…1000 / 17200…17734 / 18266…18800 / 35000…35468; үсті 5200', '%s; z max %s (n=%d)' % (sorted(set(kbo)), rng([d['bb'][5] for d in kb]), len(kb)), set(kbo) == exp_kb and within([d['bb'][5] for d in kb], 5200, 0.05) and len(kb) == 44)
# ---- жабын жазықтығы (прогон үсті)
roofA = []; roofG = []
for d in pr:
    e = d['ends'].split('|'); r = [x for x in e if x.startswith('roof')][0].replace('roof ', '').split('..'); lo_, hi_ = f(r[0]), f(r[1])
    (roofA if d['p'][1] < 18000 else roofG).append((lo_, hi_))
with open(os.path.join(H, '_roof_plane.txt'), 'w', encoding='utf-8') as o:
    for nm, L in (('A жартысы (y<18000)', roofA), ('G жартысы', roofG)):
        o.write('%s: n=%d, төменгі бет (жазықтықтан) %.2f…%.2f мм, ҮСТІҢГІ БЕТ %.2f…%.2f мм → ауытқу (max−min) = %.2f мм\n' % (nm, len(L), min(a for a, b in L), max(a for a, b in L), min(b for a, b in L), max(b for a, b in L), max(b for a, b in L) - min(b for a, b in L)))
    allh = [b for a, b in roofA + roofG]; o.write('БАРЛЫҒЫ: n=%d, ҮСТІҢГІ БЕТ ауытқуы (max−min) = %.2f мм (жазықтық: ригель үсті + 240, еңіс 5 %%, A/G айналы)\n' % (len(allh), max(allh) - min(allh)))
# ---- шығару
with open(os.path.join(H, 'frame_changes_check.md'), 'w', encoding='utf-8') as o:
    o.write('# frame_changes.md тексерісі — МОДЕЛЬДЕН өлшенген мәндер (13.11.2026)\n\nКөзі: Revit геометриясы (`model_dump.tsv`: геометрия төбелері; `measure.tsv`: тік сызықпен дене кесу). Күтілетін сандар паспорттардан қолмен жазылған (check_changes.py).\n\n')
    o.write('| № | Не | Паспорт бойынша | Модельден өлшенген | ✓/✗ | Ескерту |\n|---|---|---|---|---|---|\n')
    for n, title, exp, meas, ok, note in sorted(rows, key=lambda r: r[0]):
        o.write('| %d | %s | %s | %s | %s | %s |\n' % (n, title, exp, meas, '✓' if ok else '✗', note))
    o.write('\nЖолдар: %d, ✓ = %d, ✗ = %d\n' % (len(rows), sum(1 for r in rows if r[4]), sum(1 for r in rows if not r[4])))
print('rows', len(rows), 'ok', sum(1 for r in rows if r[4]), 'fail', [r[0] for r in rows if not r[4]])
