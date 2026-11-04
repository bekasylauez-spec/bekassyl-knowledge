# лист 4: разрез 1-1 (марши YA + нижний марш) и 2-2 (марши YB) из общего разреза пользователя; лист 5: 3-3, 4-4
import ezdxf, json, sys
from ezdxf import bbox
S = sys.argv[1]; B = chr(92); T = chr(9)
doc = ezdxf.readfile(S + '/km/live.dxf'); msp = doc.modelspace()
def grab(x0, y0, x1, y1, skip_types=(), skip=()):
    hs = []
    for e in msp:
        if e.dxftype() in skip_types or e.dxf.handle in skip: continue
        try: b = bbox.extents([e])
        except Exception: continue
        if not b.has_data: continue
        cx, cy = (b.extmin.x + b.extmax.x) / 2, (b.extmin.y + b.extmax.y) / 2
        if x0 <= cx <= x1 and y0 <= cy <= y1: hs.append(e.dxf.handle)
    return hs
note = lambda *ls: B + "pxi-3.3333,l3.3333,t3.3333;" + (B + "P").join(f"{i+1}.{T}{l}" for i, l in enumerate(ls))
YA = ["673213", "673212", "673211", "6731F8", "6731F6", "6731F4"]
YB = ["673216", "673215", "673214", "6731F7", "6731F5", "6731F3"]
GRD = ["673174", "6731F9", "673370", "673350"]
RDIM = ["673399", "673248", "673257", "673271", "673287", "673296"]
win4 = (2659000, -1747500, 2686500, -1716000)
ops = []
# --- 2-2: копия без маршей YA и нижнего марша, правее
dx2 = 5113.0
src = grab(*win4, skip_types=("SPDSFORMAT", "SPDSNOTEKNOT"), skip=("671CC3", "671CC1") + tuple(YA + GRD + RDIM))
for h in src: ops.append({"t": "clone", "h": h, "base": [0, 0], "to": [dx2, 0], "tag": "S22:" + h})
mk = [h for h in src if doc.entitydb[h].dxftype() == "SPDSLEVELMARK"]
ops.append({"t": "movegrp", "h": ["S22:" + h for h in mk], "d": [-2000, 0]})
ops.append({"t": "clone", "h": "671CC3", "base": [0, 0], "to": [dx2, 0], "tag": "S22:ttl"})
ops.append({"t": "settext", "h": "S22:ttl", "s": "Разрез 2 - 2"})
# --- 1-1: сам разрез без маршей YB и правых размеров, левее
ops.append({"t": "erase", "h": YB + RDIM})
ops.append({"t": "movewin", "win": list(win4), "d": [-9687.0, 0], "skip": ["671CBC", "671CC1"]})
ops.append({"t": "settext", "h": "671CBE", "s": "Разрезы 1 - 1; 2 - 2"})
ops.append({"t": "settext", "h": "671CC1", "s": note("Общие данные см. на листах 1.1, 1.2, спецификацию металлопроката - на листе 2.",
                                                    "Узлы 1, 2 см. на листе 6, узлы 3, 4, 5, 7 - на листе 7.",
                                                    "Отметки даны от уровня нижней площадки (0.000).")})
# --- лист 5
ops.append({"t": "settext", "h": "671FEE", "s": "Разрез 3 - 3"})
ops.append({"t": "settext", "h": "671FEC", "s": "Разрез 4 - 4"})
ops.append({"t": "settext", "h": "671FE7", "s": "Разрезы 3 - 3; 4 - 4"})
ops.append({"t": "settext", "h": "671FEA", "s": note("Общие данные см. на листах 1.1, 1.2, спецификацию металлопроката - на листе 2.",
                                                    "Разрез 3 - 3 - по стойкам у промежуточных площадок, 4 - 4 - у площадок этажей.",
                                                    "Узлы 4 - 6 см. на листе 7.")})
# --- ведомость листов, примечания плана
ops.append({"t": "tset", "h": "6714BA", "cells": [[6, 1, "Разрезы 1 - 1; 2 - 2"], [7, 1, "Разрезы 3 - 3; 4 - 4"]]})
ops.append({"t": "settext", "h": "671849", "s": note("Общие данные см. на листах 1.1, 1.2, спецификацию металлопроката - на листе 2.",
                                                    "Разрезы 1 - 1, 2 - 2 см. на листе 4, разрезы 3 - 3, 4 - 4 - на листе 5, узлы - на листах 6, 7.",
                                                    "Кронштейны К1 (узел 6) - на каждой площадке у стоек Ст1 со стороны здания.")})
json.dump(ops, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
print(len(ops), len(src))
