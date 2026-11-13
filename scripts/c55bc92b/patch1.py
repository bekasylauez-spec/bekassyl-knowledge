# -*- coding: utf-8 -*-
# gen.py v1 -> v2, part 1 (every change explicit)
P = r'D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто\gen.py'
src = open(r'D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто\_v1\gen.py', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global src
    assert src.count(old) == cnt, (src.count(old), old[:80])
    src = src.replace(old, new)

# ---- header
rep("""# РМЦ КМ каркас: ЛИРА (model.json) -> members.tsv (Revit placement lines, mm) + lira_map.tsv
# Правила: D:\\РАБОЧКА\\От Маке\\РМЦ\\_жүйе\\КМ_геометрия.md (2-4 бөлім) + паспорт 3.4. Барлық "болжам" жолдары ASSUME_* белгілерімен.""",
"""# РМЦ КМ каркас (v2, 13.11.2026): ЛИРА (model.json) -> members.tsv (Revit placement lines, mm) + lira_map.tsv
# Правила: D:\\РАБОЧКА\\От Маке\\РМЦ\\_жүйе\\КМ_геометрия.md (2-4 бөлім) + паспорт 3.4 + УЗЕЛ ПАСПОРТТАРЫ (_авто\\spec\\*.md, «Модельдеушіге» / «Модель түзетуі»).
# Әр өзгеріс frame_changes.md кестесінде (қай паспорт, қай жол). v1 = _v1\\gen.py. Барлық "болжам" жолдары ASSUME_* белгілерімен.""")

# ---- constants
rep("Z_COL_TOP_AG = 8287.0\nZ_COL_TOP_D = 9145.0\nZ_ANTRESOL_TOP = 3800.0      # +2800+1000",
    "Z_COL_TOP_AG = 8286.0        # uzel_01: К1 басы +8,286 (ригель табаны +8,311 − оголовок 25)\nZ_COL_TOP_D = 9293.0         # uzel_02: К1 (D) Λ-кесу шыңы +9,293 (ригель табаны +9,318 − оголовок 25)\nZ_ANTRESOL_TOP = 3886.0      # uzel_20: К2 антресоль білігі +3,886 (оголовок −14 → +3,900)")
rep("YA_COL = COL_H1 / 2          # A колонна центрі 266",
    "YA_COL = COL_H1 / 2          # A колонна центрі 266\nZ_R1_UPPER = 8641.6          # uzel_07/12: жоғарғы Р1 осі +8,641,6 (паспорттағы нақты сан)")

# ---- rafter geometry (new bottom profile, uzel_01/03/04/02)
rep("""def h_raf(y):
    d = dist_edge(y)
    if d <= 6000: return 690.0 - 240.0 * d / 6000.0
    if d <= 12500: return 450.0
    return 450.0 + 100.0 * (d - 12500.0) / 5500.0
def bot_raf(y): return top_raf(y) - h_raf(y)""",
"""def bot_raf(y):
    # ригель табаны (мм): d = ең жақын A/G осінен қашықтық. uzel_01: Б1 табаны горизонталь +8,311 (d 0…600), вут +8,818-ге дейін (d 6000);
    # 6000…12500 h 450 (Б1 6000…6600, Б2); Б3: h 450 → 550 (табан +9,143 → +9,318, uzel_02)
    d = dist_edge(y)
    if d <= 600.0: return 8311.0
    if d <= 6000.0: return 8311.0 + (8818.0 - 8311.0) * (d - 600.0) / 5400.0
    if d <= 12500.0: return top_raf(y) - 450.0
    return 9143.0 + (9318.0 - 9143.0) * (d - 12500.0) / 5500.0
def h_raf(y): return top_raf(y) - bot_raf(y)""")

# ---- FOOT with column info
rep("""        add(mk, 'C', (x, y, Z_COL_BASE), (x, y, top), 'col', orient='Y', rodids=ids); FOOT.append((x - 150.0, x + 150.0, y - 266.0, y + 266.0))""",
    """        add(mk, 'C', (x, y, Z_COL_BASE), (x, y, top), 'col', orient='Y', rodids=ids); FOOT.append((x - 150.0, x + 150.0, y - 266.0, y + 266.0, mk, 'Y', x, y, 4.0))""")
rep("""        if zt > 4.0:   # торец: ригель табанына дейін (колонна ізі бойынша ең төменгі нүкте, ригельге кірмеу үшін)
            top = min(bot_raf(y - hy), bot_raf(y + hy)); orient = 'X'""",
    """        if zt > 4.0:   # торец: ригель табаны (колонна осінде) − оголовок 20 (uzel_19: К2 +8,798, К3 +9,098); еңіспен кесу — узел бөлшегі (жазық үсті)
            top = bot_raf(y) - 20.0; orient = 'X'""")
rep("""        add(mk, 'C', (x, y, Z_COL_BASE), (x, y, top), 'col', orient=orient, rodids=ids, note='torets' if zt > 4 else 'antresol'); FOOT.append((x - hx, x + hx, y - hy, y + hy))""",
    """        add(mk, 'C', (x, y, Z_COL_BASE), (x, y, top), 'col', orient=orient, rodids=ids, note='torets' if zt > 4 else 'antresol'); FOOT.append((x - hx, x + hx, y - hy, y + hy, mk, orient, x, y, 2.5 if mk == 'К3' else 5.0))""")

# ---- rafters: new junction 6600, ridge ends 17990/18010; rods keep the LIRA stiffness ranges
rep("""        for mk, s, (ya, yb) in (('Б1', 15, (0, 6000)), ('Б2', 16, (6000, 12500)), ('Б3', 17, (12500, 18000))):
            if half == 'A': y1, y2 = ya, yb
            else: y1, y2 = 36000 - ya, 36000 - yb
            lo, hi = sorted((y1 / 1000.0, y2 / 1000.0))""",
"""        # (марка, ЛИРА жесткость, ЛИРА стержень диапазоны (иелік), модельдегі ұштары): Б1 0…6600 (uzel_03), Б2 6600…12500, Б3 12500…17990 / 18010…23500 (uzel_02, жота пластинасы 20)
        for mk, s, (ya, yb), (ma, mb) in (('Б1', 15, (0, 6000), (0.0, 6600.0)), ('Б2', 16, (6000, 12500), (6600.0, 12500.0)), ('Б3', 17, (12500, 18000), (12500.0, 17990.0))):
            if half == 'A': y1, y2 = ma, mb
            else: y1, y2 = 36000 - ma, 36000 - mb
            lo, hi = sorted(((ya if half == 'A' else 36000 - ya) / 1000.0, (yb if half == 'A' else 36000 - yb) / 1000.0))""")

# ---- ПБ1 ends +-10 (uzel_05)
rep("""    x1, x2 = XM(min(r['p'][0], r['q'][0])), XM(max(r['p'][0], r['q'][0]))
    add('ПБ1', 'B', (x1, y, 5200.0 + 786.0), (x2, y, 5200.0 + 786.0), 'pb', zj='T', rodids=[r['i']])""",
"""    x1, x2 = XM(min(r['p'][0], r['q'][0])) + 10.0, XM(max(r['p'][0], r['q'][0])) - 10.0     # uzel_05: ПБ ұштары рама осінен ±10 (саңылау 20)
    add('ПБ1', 'B', (x1, y, 5200.0 + 786.0), (x2, y, 5200.0 + 786.0), 'pb', zj='T', rodids=[r['i']])""")

# ---- Б4 / Б5 ends
rep("""def foot_at(x, y):
    for (x0, x1, y0, y1) in FOOT:
        if x0 - 1 <= x <= x1 + 1 and y0 - 1 <= y <= y1 + 1: return (x0, x1, y0, y1)
    return None""",
"""def foot_at(x, y):
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
        return (cy + tw2 + GAP_B4) if lower else (cy - tw2 - GAP_B4)""")
rep("""        left = Fa[1] if Fa else xa; right = Fb[0] if Fb else xb
        add('Б4', 'B', (left, y, ZB), (right, y, ZB), 'b4', zj='T', rodids=[r['i']], note='X')""",
"""        left = b4_end(Fa, 'X', True) if Fa else xa; right = b4_end(Fb, 'X', False) if Fb else xb
        add('Б4', 'B', (left, y, ZB), (right, y, ZB), 'b4', zj='T', rodids=[r['i']], note='X')""")
rep("""    add('Б4', 'B', (x, Fa[3] if Fa else ys[0], ZB), (x, Fb[2] if Fb else ys[1], ZB), 'b4', zj='T', rodids=ids, note='Y')""",
"""    add('Б4', 'B', (x, b4_end(Fa, 'Y', True) if Fa else ys[0], ZB), (x, b4_end(Fb, 'Y', False) if Fb else ys[1], ZB), 'b4', zj='T', rodids=ids, note='Y')""")
rep("""for r in by_s[23]:   # Б5 X бойымен: көлденең Б4 полкасына дейін (125)
    y = r['p'][1] * 1000.0; xa, xb = sorted((XM(r['p'][0]), XM(r['q'][0])))
    add('Б5', 'B', (xa + 125.0, y, ZB), (xb - 125.0, y, ZB), 'b5', zj='T', rodids=[r['i']], note='X')""",
"""for r in by_s[23]:   # Б5 X бойымен: Б4 стенкасынан 20 (uzel_18: Б5 ұшы рама осінен 23; белдеулер 140-қа дейін ойылады — ойық Б5 семейство ұшында)
    y = r['p'][1] * 1000.0; xa, xb = sorted((XM(r['p'][0]), XM(r['q'][0])))
    L5 = (xb - 23.0) - (xa + 23.0)
    add('Б5', 'B', (xa + 23.0, y, ZB), (xb - 23.0, y, ZB), 'b5_%d' % round(L5), zj='T', rodids=[r['i']], note='X')""")

# ---- purlins (uzel_16)
rep("""for r in by_s[8]:
    yl = round(r['p'][1], 3); y = yl * 1000.0
    x1, x2 = XM(min(r['p'][0], r['q'][0])), XM(max(r['p'][0], r['q'][0]))""",
"""for r in by_s[8]:
    yl = round(r['p'][1], 3); y = yl * 1000.0
    if abs(yl) < 1e-6: y = YA_COL                 # uzel_16: карниз прогоны колонна осі үстінде y = 266 (G: 35 734)
    elif abs(yl - 36) < 1e-6: y = YG_COL
    xl0, xl1 = min(r['p'][0], r['q'][0]), max(r['p'][0], r['q'][0])
    x1, x2 = XM(xl0) + 100.0, XM(xl1) - 100.0     # тіректе әр жағынан 100 (саңылау 200)
    if abs(xl0) < 1e-6: x1 = XM(xl0) - 250.0      # торецтен шығыс 250 (x −100)
    if abs(xl1 - 60) < 1e-6: x2 = XM(xl1) + 250.0 # (x 60 100)""")

open(P, 'w', encoding='utf-8').write(src)
print('part 1 written')
