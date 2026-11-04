# -*- coding: utf-8 -*-
# list model-space entity kinds visible in one layout's viewport (type/class, layer, linetype, lineweight, ltscale)
import collections, sys
import ezdxf
from ezdxf import bbox

d = ezdxf.readfile(sys.argv[1]); LAY = sys.argv[2]
import json; PC = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}
classes = {}
for c in d.classes:
    classes[len(classes)] = c.dxf.name
vp = None
for lay in d.layouts:
    if lay.name == LAY:
        for v in lay.query("VIEWPORT"):
            if v.dxf.get("id", 2) != 1 and v.dxf.view_height:
                vp = v
s = vp.dxf.height / vp.dxf.view_height; c = vp.dxf.view_center_point; w = vp.dxf.width / s; h = vp.dxf.view_height
X0, Y0, X1, Y1 = c.x - w / 2, c.y - h / 2, c.x + w / 2, c.y + h / 2
lts = {l.dxf.name: l.dxf.linetype for l in d.layers}
cnt = collections.Counter(); ex = {}
for e in d.modelspace():
    try:
        cc = bbox.extents([e]).center
    except Exception:
        continue
    if not (X0 <= cc.x <= X1 and Y0 <= cc.y <= Y1):
        continue
    t = e.dxftype()
    if t == "ACAD_PROXY_ENTITY":
        t = "PROXY:" + PC.get(e.dxf.handle, "?")
    lt = e.dxf.get("linetype", "BYLAYER")
    k = (t, e.dxf.layer, lt if lt.upper() != "BYLAYER" else "BL:" + str(lts.get(e.dxf.layer)), e.dxf.get("lineweight", -1), round(e.dxf.get("ltscale", 1), 1))
    cnt[k] += 1; ex.setdefault(k, e.dxf.handle)
for k, n in sorted(cnt.items(), key=lambda x: -x[1]):
    print(n, k, ex[k])
