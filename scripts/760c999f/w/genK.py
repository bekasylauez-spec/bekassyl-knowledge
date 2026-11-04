# ops for 4-storey 4. Колонна: 5-storey style (notes on every sheet, fixed overlay table, typos)
import json, re
ops = []
X0 = [-101983, -51283, -583, 50117, 100817, 151517, 202217]       # frame left x of the 7 column sheets
# notes: Км-1 note moved to the 5-storey place, then copied to the other six sheets
ops.append({"t": "props", "h": "35C36", "x": X0[0] + 4643, "y": 458458, "w": 6526})
ops.append({"t": "clone", "h": "35C36", "d": [[x - X0[0], 0] for x in X0[1:]]})
# overlay table «Таблица размеров накладок» (order matches node A: Н1-Ø32, Н2-Ø28, Н3-Ø25)
rows = [["Н1", "32", "320", "2.01"], ["Н2", "28", "280", "1.35"], ["Н3", "25", "250", "0.96"], ["Н4", "22", "220", "0.66"], ["Н5", "20", "200", "0.49"]]
for h in ["1AB4EC", "1F358E", "1F35BF", "1F885C", "202752", "214167", "238223"]:
    cells = [[0, 0, "Таблица размеров накладок"], [2, 1, "мм."]]
    for i, r in enumerate(rows):
        for c, v in enumerate(r):
            cells.append([3 + i, c, v])
    ops.append({"t": "cells", "h": h, "cells": cells})
# stamp name of sheet Км-7 said «Колонна Км-6»
ops.append({"t": "text", "h": "237BC3", "v": "Колонна Км-7"})
# drawing titles Км-1, Км-2 like the other sheets (layer Размеры, 175)
for h in ["35C33", "1BE1EB"]:
    ops.append({"t": "props", "h": h, "layer": "Размеры", "th": 175})
# «данные лист» -> «данный лист» in the spec tables
cur = None
fix = {}
for line in open("k4.tables.txt", encoding="utf-8-sig"):
    m = re.match(r"TABLE (\w+)", line)
    if m:
        cur = m.group(1); continue
    m = re.match(r"\s+R(\d+) h=[^|]*\|(.*)", line)
    if m and "данные лист" in m.group(2):
        cols = m.group(2).split("|")
        for c, v in enumerate(cols):
            if v.strip() == "данные лист":
                fix.setdefault(cur, []).append([int(m.group(1)), c, "данный лист"])
for h, cells in fix.items():
    ops.append({"t": "cells", "h": h, "cells": cells})
json.dump(ops, open("opsK1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(ops), {h: len(c) for h, c in fix.items()})
