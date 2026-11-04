# -*- coding: utf-8 -*-
# ЛК-2 / ЛК-3: bring to the ЛК-1.1 style (sheet 7 from ЛК-1.1, OD layout, notes, marks), rename ЛК-3
import json, sys, ezdxf

S = r"C:\Users\Admin\AppData\Local\Temp\claude\D---------\b6e176ea-26b4-4762-a290-80708f71b8b2\scratchpad"
SRC11 = S + r"\lk\lk1.1.dwg"
s7 = json.load(open("lk/s7.json"))
d11 = ezdxf.readfile("lk/lk1.1.dxf")
P11 = d11.entitydb.get("577515").text.split("\\P")
T17 = d11.entitydb.get("577517").text

def od(album, d):
    p = d.entitydb.get("577515").text.split("\\P")
    out = list(P11)
    out[1], out[15], out[17] = p[1], p[15], p[17]
    if album == "3":
        out = [x.replace("ЛК-2", "ЛК-3") for x in out]
        out[15] = ("\\pq*;Навес над наружной лестницей ЛК-3 - отдельно стоящее одноэтажное стальное сооружение размерами в плане "
                   "6,7х1,4 м по осям стоек (габарит покрытия 7,2х2,0 м), расположенное вдоль оси К у осей 10/1-11 (привязки - см. листы 3, 4). "
                   "Низ стоек - отм. +0,340, низ ферм - отм. +2,340, верх покрытия - отм. +2,860.")
        out[17] = out[17].replace("(12 шт., два ряда на расстоянии 1,5 м, шаг 1,83 м)", "(10 шт., два ряда на расстоянии 1,4 м, шаг 1,675 м)").replace("(6 шт.)", "(5 шт.)")
        assert "10 шт." in out[17] and "5 шт." in out[17], out[17]
    return "\\P".join(out)

def ops_for(album):
    d = ezdxf.readfile(f"lk/lk{album}.dxf")
    ops = [{"t": "maprst"}]
    # sheet 7: erase everything inside except the format frame, import ЛК-1.1 sheet 7
    ops.append({"t": "erase", "h": s7[album]["h"]})
    ops.append({"t": "import", "file": SRC11, "h": s7["1.1"]["h"], "base": [0, 0], "to": [0, 0], "pre": "S7:"})
    # sheet 1: OD in two columns like ЛК-1.1
    ops.append({"t": "mtpos", "h": "577515", "s": od(album, d)})
    ops.append({"t": "mtpos", "h": "577517", "s": T17, "at": [2364951.4, -1714646.4], "w": 17695.2})
    ops.append({"t": "erase", "h": ["577519", "57751B", "57751D"]})
    # sheet notes (sheets 4, 5, 6) at the ЛК-1.1 place and height
    notes = json.load(open("lk/notes.json", encoding="utf-8"))
    for sh in ("4", "5", "6"):
        ref = notes["1.1"][sh][0]; tg = notes[album][sh][0]
        ops.append({"t": "mtpos", "h": tg["h"], "at": ref["ins"], "w": ref["w"], "th": ref["h_"], "att": ref["att"]})
    # sheet 4: Ст1 callouts 2.0 like ЛК-1.1
    ops.append({"t": "notesize", "win": [2439363, -1756170, 2454213, -1735151], "names": ["Ст1"], "size": 2.0})
    if album == "2":
        # СВ1 in the middle bay of the bracing plan (dashed, mark СВ1), knot 6/7, sheet 5 knots with sheet 7, П1 marks, sheet 6 axes 1:40
        ops.append({"t": "lt", "h": "584E80", "v": "HIDDEN", "ltscale": 400})
        ops.append({"t": "noteset", "win": [2447400, -1744900, 2448000, -1744450], "from": "РС1", "to": "СВ1"})
        ops.append({"t": "import", "file": SRC11, "h": ["581882"], "base": [0, 0], "to": [9, 375], "pre": "K6:"})
        for h in ["57E787", "57E788", "57E789", "57E78A", "581838"]:
            ops.append({"t": "mcset", "h": h, "set": {"Note": "7"}})
        cols = {2458552: 2458558, 2460899: 2461075, 2462906: 2463227, 2464968: 2465438}
        grp = {2458552: ["5740CA", "5740CB", "5740CC", "5740CD", "5740CE"], 2460899: ["5740C5", "5740C6", "5740C7", "5740C8", "5740C9"],
               2462906: ["5740BB", "5740BC", "5740BD", "5740BE", "5740BF"], 2464968: ["5740C0", "5740C1", "5740C2", "5740C3", "5740C4"]}
        for x0, hs in grp.items():
            ops.append({"t": "import", "file": SRC11, "h": hs, "base": [x0, 0], "to": [cols[x0], -253], "pre": "P1:"})
        ops.append({"t": "objpropset", "h": ["585A5B", "585A5C", "585A85", "585A86"], "name": "Scale", "value": 40, "num": True})
    if album == "3":
        ops.append({"t": "settext", "h": "588AAB", "s": "\\pxqc;{\\fGOST Common|b0|i1|c204|p34;Лестница ЛК-3}"})
        ops.append({"t": "settext", "h": "588B3D", "s": "{\\fISOCPEUR|b0|i1|c204|p34;Лестница ЛК-3}"})
        ops.append({"t": "settext", "h": "588B55", "s": "{\\fISOCPEUR|b0|i1|c204|p34;Лестница ЛК-3}"})
    ops.append({"t": "regen"})
    return ops

for a in ("2", "3"):
    ops = ops_for(a)
    json.dump(ops, open(f"mc/ops_lk{a}.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(a, len(ops))
