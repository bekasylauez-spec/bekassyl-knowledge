# -*- coding: utf-8 -*-
# РМЦ КМ каркас (v3, 13.11.2026, шешімдер узел 1-4): ЛИРА (model.json) -> members.tsv (Revit placement lines, mm) + lira_map.tsv
# Правила: D:\РАБОЧКА\От Маке\РМЦ\_жүйе\КМ_геометрия.md (2-4 бөлім) + паспорт 3.4 + УЗЕЛ ПАСПОРТТАРЫ (_авто\spec\*.md, «Модельдеушіге» / «Модель түзетуі»).
# Әр өзгеріс frame_changes.md кестесінде (қай паспорт, қай жол). v1 = _v1\gen.py. Барлық "болжам" жолдары ASSUME_* белгілерімен.
# Іске қосу: python -I gen.py   (оқиды D:\_claude_work\RMC\lira\model.json, жазады осы папкаға)
import json, math, collections, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(r'D:\_claude_work\RMC\lira\model.json', encoding='utf-8'))
RODS = [r for r in M['rods']]
INCL = {8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25}
rods = [r for r in RODS if r['s'] in INCL]

# ---------- геометрия параметрлері (мм) ----------
SLOPE = 0.05                 # АР 5 %
TOP_A = 8968.0               # ригель үсті A осінде
COL_H1, COL_H = 532.0, 300.0  # К1 тереңдік (Y бойы), ені
ASSUME_TORETS_K1 = 150.0     # торец К1 колоннасы ішке (болжам, КМ_геометрия 2-бөлім)
ASSUME_TORETS_K23 = 100.0    # торец К2/К3 ішке 75..125 -> 100 (болжам)
Z_COL_BASE = 900.0
Z_COL_TOP_AG = 8286.0        # uzel_01: К1 басы +8,286 (ригель табаны +8,311 − оголовок 25)
Z_COL_TOP_D = 9293.0         # uzel_02: К1 (D) Λ-кесу шыңы +9,293 (ригель табаны +9,318 − оголовок 25)
Z_ANTRESOL_TOP = 3886.0      # uzel_20: К2 антресоль білігі +3,886 (оголовок −14 → +3,900)
Z_BEAM_TOP_OFFICE = 3900.0   # болжам
Z_KONSOL_TOP = 5200.0
Z_STRUT = 6000.0
YA_COL = COL_H1 / 2          # A колонна центрі 266
Z_R1_UPPER = 8641.6          # uzel_07/12: жоғарғы Р1 осі +8,641,6 (паспорттағы нақты сан)
YG_COL = 36000.0 - COL_H1 / 2

def XM(xl):          # ЛИРА x (м) -> модель X (мм): торец рамалары ішке ығысады
    if abs(xl) < 1e-6: return ASSUME_TORETS_K1
    if abs(xl - 60) < 1e-6: return 60000.0 - ASSUME_TORETS_K1
    return xl * 1000.0
def XM23(xl):
    if abs(xl) < 1e-6: return ASSUME_TORETS_K23
    if abs(xl - 60) < 1e-6: return 60000.0 - ASSUME_TORETS_K23
    return xl * 1000.0
def YC(yl):          # колонна жазықтығы (A/G колонналары ішке 266)
    if abs(yl) < 1e-6: return YA_COL
    if abs(yl - 36) < 1e-6: return YG_COL
    return yl * 1000.0
def dist_edge(y):    # ең жақын қабырғаға (A/G) қашықтық: rafter координатасы d
    return min(y, 36000.0 - y)
def top_raf(y):
    return TOP_A + SLOPE * dist_edge(y)
def bot_raf(y):
    # ригель табаны (мм): d = ең жақын A/G осінен қашықтық. Шешімдер 3 (v3): Б1 табаны горизонталь +8,311 y 0…684, вут 684…6000 → +8,818;
    # 6000…12500 h 450 (Б1 ұшы 6575, Б2); Б3: h 450 → 550 (табан +9,143 → +9,318, uzel_02)
    d = dist_edge(y)
    if d <= 684.0: return 8311.0
    if d <= 6000.0: return 8311.0 + (8818.0 - 8311.0) * (d - 684.0) / 5316.0
    if d <= 12500.0: return top_raf(y) - 450.0
    return 9143.0 + (9318.0 - 9143.0) * (d - 12500.0) / 5500.0
def h_raf(y): return top_raf(y) - bot_raf(y)
def neu_raf(y): return top_raf(y) - h_raf(y) / 2.0
def hw_raf(y):       # ригель полкасының жарты ені
    d = dist_edge(y)
    if d < 6000 - 1e-6: return 125.0
    if d <= 12500 + 1e-6: return 140.0
    return 175.0

members = []   # dict
FOOT = []      # колонна іздері: (x0, x1, y0, y1)
lmap = []      # (rod i, member id, note)
def add(mark, kind, p, q, fam, orient='', roll=0.0, zj='O', rodids=(), note='', extra=''):
    mid = len(members) + 1
    members.append(dict(id=mid, mark=mark, kind=kind, p=p, q=q, fam=fam, orient=orient, roll=roll, zj=zj, rods=list(rodids), note=note, extra=extra))
    for r in rodids: lmap.append((r, mid))
    return mid

def merge_chains(rs):
    """ЛИРА стерженьдерін түйін бойынша бір түзудегі жұптарға біріктіру (қарама-қарсы бағыт), тізбек қайтарады"""
    inc = collections.defaultdict(list)
    for r in rs:
        inc[r['n1']].append((r, 1)); inc[r['n2']].append((r, -1))
    def dvec(r):
        d = [r['q'][k] - r['p'][k] for k in range(3)]; L = math.sqrt(sum(c * c for c in d)); return [c / L for c in d]
    nxt = {}   # (rod i, end 'n1'/'n2') -> other rod
    for n, lst in inc.items():
        if len(lst) < 2: continue
        # direction pointing away from node
        away = []
        for r, e in lst:
            d = dvec(r); away.append((r, [c * e for c in d]))
        used = set()
        for a in range(len(away)):
            for b in range(a + 1, len(away)):
                if a in used or b in used: continue
                dot = sum(away[a][1][k] * away[b][1][k] for k in range(3))
                if dot < -0.9999:
                    ra, rb = away[a][0], away[b][0]
                    nxt.setdefault(ra['i'], []).append(rb['i']); nxt.setdefault(rb['i'], []).append(ra['i']); used.update([a, b])
    byid = {r['i']: r for r in rs}
    seen = set(); chains = []
    for r in rs:
        if r['i'] in seen: continue
        comp = []; st = [r['i']]
        while st:
            c = st.pop()
            if c in seen: continue
            seen.add(c); comp.append(c); st.extend(nxt.get(c, []))
        pts = []
        for c in comp:
            pts.append(tuple(byid[c]['p'])); pts.append(tuple(byid[c]['q']))
        # ең алыс екі нүкте
        best = None
        for a in pts:
            for b in pts:
                dd = sum((a[k] - b[k]) ** 2 for k in range(3))
                if best is None or dd > best[0]: best = (dd, a, b)
        chains.append((sorted(comp), best[1], best[2]))
    return chains

def clip_line(p, q, cp, cq):
    """сызықты ұштарынан X бойымен cp, cq мм қысқарту (Δx ≠ 0), Δx=0 болса ұзындық бойымен"""
    d = [q[k] - p[k] for k in range(3)]
    if abs(d[0]) > 1e-6:
        L = abs(d[0]); t0 = cp / L; t1 = cq / L
    else:
        L = math.sqrt(sum(c * c for c in d)); t0 = cp / L; t1 = cq / L
    return ([p[k] + d[k] * t0 for k in range(3)], [q[k] - d[k] * t1 for k in range(3)])

# ============ КОЛОННАЛАР ============
by_s = collections.defaultdict(list)
for r in rods: by_s[r['s']].append(r)
cols = collections.defaultdict(list)
for s, mk in ((19, 'К1'), (20, 'К2'), (18, 'К3')):
    for r in by_s[s]:
        cols[(mk, round(r['p'][0], 3), round(r['p'][1], 3))].append(r)
for (mk, xl, yl), rl in sorted(cols.items(), key=lambda t: (t[0][0], t[0][1], t[0][2])):
    zt = max(max(r['p'][2], r['q'][2]) for r in rl)
    ids = [r['i'] for r in rl]
    if mk == 'К1':
        x = XM(xl); y = YC(yl); top = Z_COL_TOP_D if abs(yl - 18) < 1e-6 else Z_COL_TOP_AG
        add(mk, 'C', (x, y, Z_COL_BASE), (x, y, top), 'col', orient='Y', rodids=ids); FOOT.append((x - 150.0, x + 150.0, y - 266.0, y + 266.0, mk, 'Y', x, y, 4.0))
    else:
        x = XM23(xl); y = yl * 1000.0
        hx, hy = ({'К2': (216.0, 150.0), 'К3': (212.0, 150.0)}[mk])   # X-тереңдікті (торец) колонна: жарты өлшемдер
        if zt > 4.0:   # торец: ригель табаны (колонна осінде) − оголовок 20 (uzel_19: К2 +8,798, К3 +9,098); еңіспен кесу — узел бөлшегі (жазық үсті)
            top = bot_raf(y) - 20.0; orient = 'X'
        else:          # антресоль (Y-тереңдік: x жарты 150, y жарты 216)
            top = Z_ANTRESOL_TOP; orient = 'Y'; hx, hy = 150.0, 216.0
        add(mk, 'C', (x, y, Z_COL_BASE), (x, y, top), 'col', orient=orient, rodids=ids, note='torets' if zt > 4 else 'antresol'); FOOT.append((x - hx, x + hx, y - hy, y + hy, mk, orient, x, y, 2.5 if mk == 'К3' else 5.0))

# ============ РИГЕЛЬДЕР ============
frames = sorted(set(round(r['p'][0], 3) for r in by_s[15]))
def raf_piece(mark, s, ya, yb, side):
    pass
for xl in frames:
    X = XM(xl)
    for half in ('A', 'G'):
        # (марка, ЛИРА жесткость, ЛИРА стержень диапазоны (иелік), модельдегі ұштары): шешімдер 1–2: Б1 20…6575 (торцевое ребро 0…20; фланец 6575…6600), Б2 6625…12475, Б3 12525…17990 / 18010…23475 (жота пластинасы 20; фланец 12475…12525)
        for mk, s, (ya, yb), (ma, mb) in (('Б1', 15, (0, 6000), (20.0, 6575.0)), ('Б2', 16, (6000, 12500), (6625.0, 12475.0)), ('Б3', 17, (12500, 18000), (12525.0, 17990.0))):
            if half == 'A': y1, y2 = ma, mb
            else: y1, y2 = 36000 - ma, 36000 - mb
            lo, hi = sorted(((ya if half == 'A' else 36000 - ya) / 1000.0, (yb if half == 'A' else 36000 - yb) / 1000.0))
            ids = [r['i'] for r in by_s[s] if abs(r['p'][0] - xl) < 1e-6 and abs(r['q'][0] - xl) < 1e-6 and min(r['p'][1], r['q'][1]) >= lo - 1e-6 and max(r['p'][1], r['q'][1]) <= hi + 1e-6]
            add(mk, 'B', (X, y1, top_raf(y1)), (X, y2, top_raf(y2)), 'raf_' + mk, zj='T', rodids=ids, note=half)

# ============ ПБ1, КБ1 ============
RAIL = {0.3: 800.0, 17.7: 17400.0, 18.3: 18600.0, 35.7: 35200.0}
for r in by_s[25]:
    y = RAIL[round(r['p'][1], 3)]
    x1, x2 = XM(min(r['p'][0], r['q'][0])) + 10.0, XM(max(r['p'][0], r['q'][0])) - 10.0     # uzel_05: ПБ ұштары рама осінен ±10 (саңылау 20)
    add('ПБ1', 'B', (x1, y, 5200.0 + 786.0), (x2, y, 5200.0 + 786.0), 'pb', zj='T', rodids=[r['i']])
kb = collections.defaultdict(list)
for r in by_s[21]:
    y0 = round(r['p'][1], 3); yq = r['q'][1]
    sign = 1 if (yq > y0) else -1
    # екі стержень (0.3+0.2) -> бір консоль; тізбек басы - колонна центрі
    key = (round(r['p'][0], 3), min(r['p'][1], r['q'][1]), max(r['p'][1], r['q'][1]))
    kb[(round(r['p'][0], 3), None)].append(r)
# консольдарды түйін бойынша тізбектейміз
for xl in sorted(set(round(r['p'][0], 3) for r in by_s[21])):
    rl = [r for r in by_s[21] if abs(r['p'][0] - xl) < 1e-6]
    # әр бағыт бойынша жеке тізбек: бастап колонна осінен (y=0,18,36)
    starts = [r for r in rl if round(r['p'][1], 3) in (0.0, 18.0, 36.0)]
    for r in starts:
        y0 = round(r['p'][1], 3); sign = 1 if r['q'][1] > r['p'][1] else -1
        r2 = [t for t in rl if abs(t['p'][1] - r['q'][1]) < 1e-6]
        ids = [r['i']] + [t['i'] for t in r2]
        # колонна орталығы (модель) және ішкі полка беті
        yc = YC(y0); ycol_face = yc + sign * COL_H1 / 2
        if y0 == 0.0: yend = 800.0 + 200.0
        elif y0 == 36.0: yend = 35200.0 - 200.0
        else: yend = 18000.0 + sign * (600.0 + 200.0)
        add('КБ1', 'B', (XM(xl), ycol_face, Z_KONSOL_TOP), (XM(xl), yend, Z_KONSOL_TOP), 'kb', zj='T', rodids=ids)

# ============ БАЛКАЛАР Б4 / Б5 (кеңсе жабыны) ============
# КМ_ҚАТЕЛЕР #3/#13 + ранг: К1/К2/К3 > Б4 > Б5 — төменгі рангтағы бөлшек жоғарғысының бетінде тоқтайды (ЛИРА 6 м стержені = бір бөлшек, колоннадан колоннаға)
ZB = Z_BEAM_TOP_OFFICE
def ofc(yl): return YC(yl)
def foot_at(x, y):
    for F in FOOT:
        if F[0] - 1 <= x <= F[1] + 1 and F[2] - 1 <= y <= F[3] + 1: return F
    return None
GAP_B4 = 20.0     # uzel_17: Б4 ұшы колонна бетінен 20
def b4_end(F, axis, lower):
    # F = колонна ізі + (марка, бағдар, cx, cy, стенка жарты қалыңдығы). Колонна тереңдігі (orient) бойымен келген Б4 — ПОЛКАҒА (17): сыртқы бет ± 20;
    # көлденең келсе — СТЕНКАҒА (17а): ось ± (t/2 + 20)
    x0, x1, y0, y1, mk, orient, cx, cy, tw2 = F
    if axis == 'X':
        if orient == 'X': return (x1 + GAP_B4) if lower else (x0 - GAP_B4)
        return (cx + tw2 + GAP_B4) if lower else (cx - tw2 - GAP_B4)
    else:
        if orient == 'Y': return (y1 + GAP_B4) if lower else (y0 - GAP_B4)
        return (cy + tw2 + GAP_B4) if lower else (cy - tw2 - GAP_B4)
for r in by_s[22]:
    dx = abs(r['q'][0] - r['p'][0])
    if dx > 1e-6:     # Б4 X бойымен, әр ЛИРА стержені бөлек бөлшек
        y = ofc(r['p'][1]); xa, xb = sorted((XM(r['p'][0]), XM(r['q'][0])))
        Fa = foot_at(xa, y); Fb = foot_at(xb, y)
        left = b4_end(Fa, 'X', True) if Fa else xa; right = b4_end(Fb, 'X', False) if Fb else xb
        add('Б4', 'B', (left, y, ZB), (right, y, ZB), 'b4', zj='T', rodids=[r['i']], note='X')
for ids, a_, b_ in merge_chains([r for r in by_s[22] if abs(r['q'][0] - r['p'][0]) < 1e-6]):   # Б4 Y бойымен: 3 x 2.0 м -> 6.0 м
    x = XM(a_[0]); ys = sorted([ofc(a_[1]), ofc(b_[1])])
    Fa = foot_at(x, ys[0]); Fb = foot_at(x, ys[1])
    add('Б4', 'B', (x, b4_end(Fa, 'Y', True) if Fa else ys[0], ZB), (x, b4_end(Fb, 'Y', False) if Fb else ys[1], ZB), 'b4', zj='T', rodids=ids, note='Y')
for r in by_s[23]:   # Б5 X бойымен: Б4 стенкасынан 20 (uzel_18: Б5 ұшы рама осінен 23; белдеулер 140-қа дейін ойылады — ойық Б5 семейство ұшында)
    y = r['p'][1] * 1000.0; xa, xb = sorted((XM(r['p'][0]), XM(r['q'][0])))
    L5 = (xb - 23.0) - (xa + 23.0)
    add('Б5', 'B', (xa + 23.0, y, ZB), (xb - 23.0, y, ZB), 'b5_%d' % round(L5), zj='T', rodids=[r['i']], note='X')

# ============ ПРОГОНДАР ============
for r in by_s[8]:
    yl = round(r['p'][1], 3); y = yl * 1000.0
    if abs(yl) < 1e-6: y = YA_COL                 # uzel_16: карниз прогоны колонна осі үстінде y = 266 (G: 35 734)
    elif abs(yl - 36) < 1e-6: y = YG_COL
    xl0, xl1 = min(r['p'][0], r['q'][0]), max(r['p'][0], r['q'][0])
    x1, x2 = XM(xl0) + 100.0, XM(xl1) - 100.0     # тіректе әр жағынан 100 (саңылау 200)
    if abs(xl0) < 1e-6: x1 = XM(xl0) - 250.0      # торецтен шығыс 250 (x −100)
    if abs(xl1 - 60) < 1e-6: x2 = XM(xl1) + 250.0 # (x 60 100)
    side = 'A' if y < 18000 else 'G'
    add('Пр1', 'B', (x1, y, top_raf(y)), (x2, y, top_raf(y)), 'purlin', zj='O', rodids=[r['i']], note=side, extra='slope%s' % ('+' if y < 18000 else '-'))

# ============ РАСПОРКАЛАР ============
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
def split_rods(ids, rodmap, la, lb, t_cross, dims=(0, 1, 2)):
    """ЛИРА стержендерін (ұштары la→lb) қиылыс параметрі бойынша екі жартыға бөледі (dims = қай координаталар бойынша)"""
    g1, g2 = [], []
    L2 = sum((lb[k] - la[k]) ** 2 for k in dims)
    for i in ids:
        r = rodmap[i]; m = {k: (r['p'][k] + r['q'][k]) / 2 - la[k] for k in dims}
        t = sum(m[k] * (lb[k] - la[k]) for k in dims) / L2
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
    g1, g2 = split_rods(cut['ids'], byid13, cut['la'], cut['lb'], tcut, (0, 1))
    solid['pieces'] = [(solid['p'], solid['q'], solid['ids'], 'тұтас')]
    cut['pieces'] = [(cut['p'], c1, g1, 'кесілген-1'), (c2, cut['q'], g2, 'кесілген-2')]
for g in gs:
    for pp, qq, ids_, tag in g['pieces']:
        pp2, qq2 = (pp, qq) if pp[0] <= qq[0] else (qq, pp)
        add(g['mk'], 'B', tuple(pp2), tuple(qq2), 'tube', rodids=ids_, extra=('uzel_15г ' + tag) if tag else '')

# ---------- шығару ----------
def f(v): return ('%.2f' % v).rstrip('0').rstrip('.') if abs(v) > 1e-9 else '0'
with open(os.path.join(HERE, 'members.tsv'), 'w', encoding='utf-8', newline='\n') as fo:
    for m in members:
        fo.write('\t'.join([str(m['id']), m['mark'], m['kind'], m['fam'], f(m['p'][0]), f(m['p'][1]), f(m['p'][2]), f(m['q'][0]), f(m['q'][1]), f(m['q'][2]), m['orient'], m['zj'], m['extra'], m['note'], ','.join(str(i) for i in m['rods'])]) + '\n')
with open(os.path.join(HERE, 'lira_map.tsv'), 'w', encoding='utf-8', newline='\n') as fo:
    for r, mid in lmap: fo.write('%d\t%d\n' % (r, mid))

# ---------- статистика / тексеру ----------
cnt = collections.Counter(m['mark'] for m in members)
print('members', len(members), dict(sorted(cnt.items())))
mapped = set(r for r, _ in lmap)
miss = [r['i'] for r in rods if r['i'] not in mapped]
print('LIRA rods in scope', len(rods), 'mapped', len(mapped), 'unmapped', len(miss), miss[:20])
dup = [k for k, v in collections.Counter(r for r, _ in lmap).items() if v > 1]
print('rods in >1 member', dup[:10])
L = collections.defaultdict(float)
for m in members:
    L[m['mark']] += math.sqrt(sum((m['p'][k] - m['q'][k]) ** 2 for k in range(3))) / 1000.0
print('total length m by mark', {k: round(v, 1) for k, v in sorted(L.items())})
