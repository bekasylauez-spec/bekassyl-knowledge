# -*- coding: utf-8 -*-
# Recount of the Навес 1 Рампа steel spec from the drawing geometry (v2.dwg, 26.10.2026)
import math, json

# section 1-1 (sheet 7) chord axes, model units = mm
NP = (2524194.0, -1729526.0, 17104.5)   # НП1 axis arc
VP = (2524263.0, -1729423.0, 17503.3)   # ВП1 axis arc
XM, XL = 2531826.0, 2524526.0           # column axes М / Л

def z(arc, s):
    cx, cy, r = arc; x = XM - s
    return cy + math.sqrt(r * r - (x - cx) ** 2)

def depth(s):
    return z(VP, s) - z(NP, s)

# kg/m by GOST 30245 (R = 2t)
def kgm(b, h, t):
    A = 2 * t * (b + h - 2 * t) - (4 - math.pi) * 3 * t * t
    return round(A * 7.85e-3, 2)

W = {"140x100x4": kgm(140, 100, 4), "80x3": kgm(80, 80, 3), "60x2.5": kgm(60, 60, 2.5), "50x2.5": kgm(50, 50, 2.5)}

items = []   # (group, mark, section, n, unit_len_m or plate dims, total_len/area, kg per m / m2, note)
def tube(g, mark, sec, n, L, note):
    items.append(dict(g=g, mark=mark, sec="Тр.□" + sec.replace("x", "×"), key=sec, n=n, unit="%.3f м" % L, tot=round(n * L, 2), w=W[sec], kind="m", note=note))
def tube_sum(g, mark, sec, n, expr, tot, note):
    items.append(dict(g=g, mark=mark, sec="Тр.□" + sec.replace("x", "×"), key=sec, n=n, unit=expr, tot=round(tot, 2), w=W[sec], kind="m", note=note))
def plate(g, mark, t, n, a, b, note, area=None):
    ar = area if area is not None else a * b / 1e6
    items.append(dict(g=g, mark=mark, sec="-%d" % t, key="t%d" % t, n=n, unit=("%d×%d" % (a, b)) if area is None else "%d/%d×%d" % a if False else ("%d×%d" % (a, b)), tot=round(n * ar, 4), w=round(t * 7.85, 1), kind="m2", note=note))

# ---- Стойки
tube("Стойки", "К1 (ряд Л)", "140x100x4", 11, 3.170, "разрезы 1-1, 2-2: +0,870...+4,040")
tube("Стойки", "К1 (ряд М)", "140x100x4", 11, 1.940, "разрезы 1-1, 2-2: +0,870...+2,810")
tube("Стойки", "К2", "80x3", 5, 1.160, "разрез 1-1: +0,870...+2,030")
tube_sum("Стойки", "Пк1", "80x3", 22, "11×0.816+11×0.877", 11 * 0.816 + 11 * 0.877, "подкосы у рядов Л и М, разрезы 1-1, 2-2")
plate("Стойки", "Оголовок К1 (Л)", 10, 11, 200, 160, "узлы 3, 10")
plate("Стойки", "Оголовок К1 (М)", 10, 11, 220, 160, "узел 6")
plate("Стойки", "Оголовок К2", 10, 5, 130, 100, "узел 7")
items.append(dict(g="Стойки", mark="Ребро базы К1", sec="-8", key="t8", n=44, unit="(70+20)/2×150", tot=round(44 * 0.00675, 4), w=62.8, kind="m2", note="узел 1, по 2 шт. на К1"))

# ---- Фермы
tube("Фермы", "ВП1+НП1 Ф1", "80x3", 5, 10.100 + 8.170, "геом. схема, лист 10 (ВП1 до К2)")
tube("Фермы", "ВП1+НП1 Ф2", "80x3", 6, 8.430 + 8.170, "геом. схема, лист 10")
lat1 = 9.913 + (0.506 + 0.516 + 0.516 + 0.516 + 0.516) + 0.501
lat2 = 9.906 + (0.506 + 0.516 + 0.516 + 0.516 + 0.516) + 0.501
tube("Фермы", "Р1 Ф1", "50x2.5", 5, lat1, "11 раскосов + 5 стоек + торец")
tube("Фермы", "Р1 Ф2", "50x2.5", 6, lat2, "11 раскосов + 5 стоек + торец")
plate("Фермы", "Заглушка поясов", 4, 33, 80, 80, "22 у консоли + 6 ВП1 Ф2 + 5 ВП1 Ф1")

# ---- Связи вертикальные
d1 = math.hypot(2.400, 1.430); d2 = math.hypot(2.400, 3.170)
tube("Связи верт.", "СВ1", "50x2.5", 4, d1, "ряд М, 2 пролёта × 2, √(2.4²+1.43²)")
tube("Связи верт.", "СВ2", "50x2.5", 4, d2, "ряд Л, 2 пролёта × 2, √(2.4²+3.17²)")
sv3 = 0
rows_sv3 = [0.0, 3650.0, 7300.0, 7980.0]
parts = []
for s in rows_sv3:
    dd = depth(s) / 1000.0 if s < 7900 else 0.501
    L = 2.4 + 2 * math.hypot(1.2, dd); parts.append(L); sv3 += 2 * L
tube_sum("Связи верт.", "СВ3", "50x2.5", 8, "2.4+2×√(1.2²+h²)", sv3, "4 ряда × 2 пролёта (разрезы 3-3, 4-4)")

# ---- Связи горизонтальные и распорки
def sg(dx, s1, s2):
    return math.sqrt((dx / 1000) ** 2 + ((s2 - s1) / 1000) ** 2 + ((z(NP, s2) - z(NP, s1)) / 1000) ** 2)
sgl = []
sgl += [sg(1950, 0, 2100), sg(1950, 5200, 7300)]
for _ in range(3): sgl += [sg(2400, 0, 2100), sg(2400, 5200, 7300)]
for _ in range(2): sgl += [sg(2400, 0, 2100), sg(2400, 2100, 3650), sg(2400, 3650, 5200), sg(2400, 5200, 7300), sg(2400, 7300, 7980)]
for _ in range(4): sgl += [sg(2500, 0, 2100), sg(2500, 5200, 7300)]
tube_sum("Связи гориз.", "СГ1", "50x2.5", len(sgl), "по осям с уклоном пояса", sum(sgl), "лист 5: 26 шт.")
tube_sum("Связи гориз.", "РС1", "50x2.5", 36, "5×9.15+4×10.0", 5 * 9.15 + 4 * 10.0, "лист 5: 20 шт. в осях 1-3, 16 шт. в осях 3/1-5")
plate("Связи гориз.", "Фасонка", 10, 2, 160, 200, "узел 8 (ферма в оси 3, ряды М и Л)")

# ---- Прогоны
tube_sum("Прогоны", "П1", "60x2.5", 26, "14×9.15+12×14.80", 14 * 9.15 + 12 * 14.80, "лист 6")
plate("Прогоны", "Заглушка П1", 4, 28, 60, 60, "торцы прогонов")

# ---- Закладные
plate("Закладные", "Зд-1", 18, 22, 250, 280, "узел 1 (раздел КЖ)")
plate("Закладные", "Зд-2", 12, 5, 180, 180, "узел 2 (раздел КЖ)")

for it in items:
    it["mass"] = round(it["tot"] * it["w"] / 1000.0, 4)

groups = ["Стойки", "Фермы", "Связи верт.", "Связи гориз.", "Прогоны", "Закладные"]
tot = 0
for g in groups:
    gs = [i for i in items if i["g"] == g]
    s = sum(i["mass"] for i in gs); tot += s
    print("==", g, round(s, 3))
    for i in gs:
        print("   %-18s %-12s n=%-3d %-24s tot=%-9s w=%-6s m=%.4f  %s" % (i["mark"], i["sec"], i["n"], i["unit"], i["tot"], i["w"], i["mass"], i["note"]))
print("TOTAL", round(tot, 3))
print("weights", W, "SV3 rows", [round(p, 3) for p in parts], "depths", [round(depth(s)) for s in rows_sv3])
print("SG1", [round(x, 3) for x in sgl])
json.dump(dict(items=items, groups=groups, W=W), open("w/calc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
