# -*- coding: utf-8 -*-
# ЛК albums: spec update (ЛК-3) + framed table «Расчёт массы металла по элементам» above sheet 2 (as in Рампа)
import json, sys

T = "5771E3"
SQ = "Тр. {\\fBankGothic Md BT|b0|i0|c0|p34;0}"
A = {
    "1.1": dict(nc=12, nt=6, svd=0.98, svh=1.66, rs=(14, 1.66), sg=(20, 1.07), pr=9.0, np_=10, lp=1.64, le=1.34, pk=119, rows="2 ряда по 6, шаг 1,7 м"),
    "1.2": dict(nc=12, nt=6, svd=0.98, svh=1.66, rs=(14, 1.66), sg=(20, 1.07), pr=9.0, np_=10, lp=1.64, le=1.34, pk=119, rows="2 ряда по 6, шаг 1,7 м"),
    "2": dict(nc=12, nt=6, svd=1.03, svh=1.79, rs=(14, 1.79), sg=(20, 1.14), pr=9.65, np_=10, lp=1.77, le=1.44, pk=129, rows="2 ряда по 6, шаг 1,83 м"),
    "3": dict(nc=10, nt=5, svd=0.97, svh=1.64, rs=(11, 1.64), sg=(16, 1.06), pr=7.2, np_=8, lp=1.62, le=1.34, pk=97, rows="2 ряда по 5, шаг 1,675 м"),
}

def f2(v): return ("%.2f" % v).rstrip("0").rstrip(".") if v != int(v) else "%.1f" % v

def build(al):
    a = A[al]; ops = []
    if al == "3":
        f = [[3, 4, "=(6.71*%d*2.0*0.001)" % a["nc"]],
             [4, 5, "=(2.82*%d*(2.20+2.00+2.21)*0.001)" % a["nt"]],
             [4, 6, "=(2.82*(2*%.2f+%.2f)*0.001)" % (a["svd"], a["svh"])],
             [4, 7, "=(2.82*(%d*%.2f+%d*%.2f)*0.001)" % (a["rs"][0], a["rs"][1], a["sg"][0], a["sg"][1])],
             [4, 8, "=(2.82*5*%s*0.001)" % f2(a["pr"])],
             [7, 9, "=(2.31*(%d*2*%.2f+2*%.2f)*0.001)" % (a["np_"], a["lp"], a["le"])],
             [8, 9, "=(0.68*%d*0.96*0.001)" % a["pk"]],
             [12, 4, "=(8*7.85*0.001*(0.09*0.09*%d))" % a["nc"]]]
        ops.append({"t": "formula", "h": T, "th": 187.5, "c": f})
    G = [  # group, mark, section, n, unit text, total expr, kg/m (m2), fmt kind, note
        ("Стойки", "Ст1", SQ + "60×4", a["nc"], "2.000", "=(%d*2.0)" % a["nc"], 6.71, "m", "отм. +0,340...+2,340, лист 4"),
        ("Стойки", "Оголовок Ст1", "-8", a["nc"], "90×90", "=(%d*0.09*0.09)" % a["nc"], 62.8, "m2", "узел 2, лист 7"),
        ("Фермы", "ВП1", SQ + "40×2.5", a["nt"], "2.200", "=(%d*2.20)" % a["nt"], 2.82, "m", "лист 7, дуга по оси"),
        ("Фермы", "НП1", SQ + "40×2.5", a["nt"], "2.000", "=(%d*2.00)" % a["nt"], 2.82, "m", "лист 7"),
        ("Фермы", "Р1", SQ + "40×2.5", a["nt"], "2.210", "=(%d*2.21)" % a["nt"], 2.82, "m", "лист 7: 0,44 + 2×0,36 + 2×0,53"),
        ("Связи вертикальные", "СВ1 раскосы", SQ + "40×2.5", 2, "%.2f" % a["svd"], "=(2*%.2f)" % a["svd"], 2.82, "m", "лист 5, в среднем пролёте"),
        ("Связи вертикальные", "СВ1 пояс", SQ + "40×2.5", 1, "%.2f" % a["svh"], "=(1*%.2f)" % a["svh"], 2.82, "m", "лист 5"),
        ("Связи горизонт. и распорки", "РС1", SQ + "40×2.5", a["rs"][0], "%.2f" % a["rs"][1], "=(%d*%.2f)" % a["rs"], 2.82, "m", "лист 4, в свету между фермами"),
        ("Связи горизонт. и распорки", "СГ1", SQ + "40×2.5", a["sg"][0], "%.2f" % a["sg"][1], "=(%d*%.2f)" % a["sg"], 2.82, "m", "лист 4, по 4 в пролёте"),
        ("Прогоны", "Пр1", SQ + "40×2.5", 5, "%.2f" % a["pr"], "=(5*%s)" % f2(a["pr"]), 2.82, "m", "лист 5, 5 рядов"),
        ("Ограждение", "Перекладина", "Тр. Ø40×2.5", 2 * a["np_"] + 2, "%.2f / %.2f" % (a["lp"], a["le"]), "=(%d*2*%.2f+2*%.2f)" % (a["np_"], a["lp"], a["le"]), 2.31, "m", "лист 8: %d панелей + торец" % a["np_"]),
        ("Ограждение", "Штакетник", "Тр. Ø20×1.5", a["pk"], "0.960", "=(%d*0.96)" % a["pk"], 0.68, "m", "лист 8, шаг 150 мм"),
    ]
    colw = [1900, 1900, 2000, 800, 2200, 1700, 1500, 1350, 1500, 4025]
    th = 150
    rowh = [550, 700]
    cells = [[0, 0, "Расчёт массы металла по элементам (к технической спецификации)", 187.5],
             [1, 0, "Группа"], [1, 1, "Марка"], [1, 2, "Сечение"], [1, 3, "Кол., шт."],
             [1, 4, "Длина ед., м /\\Pразмер, мм"], [1, 5, "Общ. длина, м/\\Pплощадь, м²"],
             [1, 6, "Масса 1 м /\\P1 м², кг"], [1, 7, "Масса, т"], [1, 8, "Итого по\\Pгруппе, т"], [1, 9, "Примечание"]]
    merge = [[0, 0, 0, 9]]; fcells = []; left = []; grow = {}; gt = []
    r = 2; order = []
    for g in G:
        if g[0] not in order: order.append(g[0])
    for gname in order:
        r0 = r
        for g in [x for x in G if x[0] == gname]:
            _, mark, sec, n, unit, expr, w, kind, note = g
            rowh.append(350)
            cells += [[r, 1, mark], [r, 2, sec], [r, 3, str(n)], [r, 4, unit], [r, 9, " " + note]]
            left.append([r, 9])
            fcells.append([r, 5, expr, "%lu2%pr2" if kind == "m" else "%lu2%pr4"])
            fcells.append([r, 6, "=(%s)" % (("%.2f" % w) if kind == "m" else ("%.1f" % w)), "%lu2%pr2" if kind == "m" else "%lu2%pr1"])
            fcells.append([r, 7, "=(F%d*G%d*0.001)" % (r + 1, r + 1), "%lu2%pr3"])
            r += 1
        r1 = r - 1; grow[gname] = (r0, r1)
        cells.append([r0, 0, gname]); merge += [[r0, 0, r1, 0], [r0, 8, r1, 8]]
        fcells.append([r0, 8, "=(Sum(H%d:H%d))" % (r0 + 1, r1 + 1), "%lu2%pr3"]); gt.append("I%d" % (r0 + 1))
    rowh.append(450)
    cells.append([r, 0, "Всего масса металла, т"]); merge.append([r, 0, r, 6])
    fcells.append([r, 7, "=(Sum(H3:H%d))" % r, "%lu2%pr3"]); fcells.append([r, 8, "=(%s)" % "+".join(gt), "%lu2%pr3"])
    nrow = r + 1
    bord = []
    for rr in range(nrow):
        for c in range(10):
            T_ = B_ = 30
            for (a0, b0) in grow.values():
                if a0 <= rr <= b0: T_ = 30 if rr == a0 else 5; B_ = 30 if rr == b0 else 5
            bord.append([rr, c, T_, B_, 30, 30])
    H = sum(rowh)
    ybot = -1724651 + 600
    x0 = 2403738 + 200; y0 = ybot + 200 + H
    ops.append({"t": "newtable", "h1": T, "pos": [x0, y0], "colw": colw, "rowh": rowh, "th": th, "cells": cells,
                "merge": merge, "fcells": fcells, "bord": bord, "left": left})
    ops.append({"t": "rect", "win": [x0 - 200, ybot, x0 + sum(colw) + 200, y0 + 200], "layer": "KOHTYP", "lw": 50})
    ops.append({"t": "evalfields"})
    ops.append({"t": "dumptable", "h": T})
    return ops

for al in A:
    json.dump(build(al), open("lk/ops_calc%s.json" % al, "w", encoding="utf-8"), ensure_ascii=False)
print("ok")
