# -*- coding: utf-8 -*-
# Axis (dash-dot) lines: lineweight 0.05 mm and a linetype scale that makes the dashes readable on the sheet.
# For every model-space entity drawn with a dash-dot linetype, the scale is set from the viewport that shows it:
# ltscale = denominator * 20 / long dash of the pattern (long dash about 20 mm on paper, ГОСТ 2.303: 5..30 mm).
# Usage: python -X utf8 genaxes.py <dxf> <ops.json> <out.dwg> [rn]
# rn: ops for my full AutoCAD (rn.cs): linetype ACAD_ISO10W100 (ГОСТ 2.303 proportions 12/3), СПДС objects lts 1
import json, sys
import ezdxf
from ezdxf import bbox

DXF, OPS, OUT = sys.argv[1:4]
RN = len(sys.argv) > 4 and sys.argv[4] == "rn"
NEWLT, NEWDASH = "ACAD_ISO10W100", 12.0
d = ezdxf.readfile(DXF)


def is_axis(lt):
    if lt is None:
        return False
    n = lt.dxf.name.upper(); desc = (lt.dxf.get("description", "") or "").lower()
    return (n in ("CENTER", "CENTER2", "CENTERX2", "DASHDOT", "DASHDOT2", "DASHDOTX2") or n.startswith("ACAD_ISO04")
            or n.startswith("ACAD_ISO10") or "2.303 5" in n or "пунктир" in desc and "штрих" in desc)


def long_dash(lt):
    v = [t.value for t in lt.pattern_tags.tags if t.code == 49]
    return max(v) if v else 20.0


layer_lt = {l.dxf.name: l.dxf.linetype for l in d.layers}
vps = []
for lay in d.layouts:
    if lay.name == "Model":
        continue
    for v in lay.query("VIEWPORT"):
        if v.dxf.get("id", 2) == 1 or not v.dxf.view_height:
            continue
        s = v.dxf.height / v.dxf.view_height
        c = v.dxf.view_center_point; w = v.dxf.width / s; h = v.dxf.view_height
        vps.append((round(1 / s, 3), c.x - w / 2, c.y - h / 2, c.x + w / 2, c.y + h / 2, lay.name))

ops, report = [], {}
for lay in d.layouts:
    for e in lay:
        if not e.dxf.hasattr("layer"):
            continue
        name = e.dxf.get("linetype", "BYLAYER")
        if name.upper() == "BYLAYER":
            name = layer_lt.get(e.dxf.layer, "Continuous")
        lt = d.linetypes.get(name)
        if not is_axis(lt):
            continue
        op = {"t": "eprops" if RN else "props", "h": e.dxf.handle, "lw": 5}
        dash = long_dash(lt)
        if RN:
            op["ltype"] = NEWLT; dash = NEWDASH
        if RN and e.dxftype() == "ACAD_PROXY_ENTITY":
            op["lts"] = 1.0  # СПДС object multiplies the linetype by its own drawing scale
        elif lay.name == "Model":
            try:
                c = bbox.extents([e]).center; cx, cy = c.x, c.y
            except Exception:
                cx = cy = None
            den = [v[0] for v in vps if cx is not None and v[1] <= cx <= v[3] and v[2] <= cy <= v[4] and v[0] > 1.01]
            if den:
                op["lts"] = round(max(den) * (12.0 if RN else 20.0) / dash, 2)
        else:
            op["lts"] = round((12.0 if RN else 20.0) / dash, 2)
        ops.append(op)
        k = (e.dxftype(), e.dxf.layer, name, round(e.dxf.get("ltscale", 1.0), 2), e.dxf.get("lineweight", -1), op.get("lts"))
        report[k] = report.get(k, 0) + 1
for k, n in sorted(report.items(), key=lambda x: -x[1]):
    print(n, k)
if RN:
    ops = [{"t": "ltload", "names": [NEWLT]}] + ops + [{"t": "regen"}, {"t": "savedoc"}]
else:
    ops.append({"t": "save", "file": OUT})
json.dump(ops, open(OPS, "w", encoding="utf-8"), ensure_ascii=False)
print("ops", len(ops))
