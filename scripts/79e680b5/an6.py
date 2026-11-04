import ezdxf, sys
from ezdxf import bbox
doc = ezdxf.readfile(sys.argv[1])
msp = doc.modelspace()
x0, x1, y0, y1 = 1236000, 1254000, 1172000, 1174600
for e in msp:
    if e.dxf.handle == '1285AB':
        continue
    try:
        b = bbox.extents([e], fast=True)
    except Exception:
        continue
    if not b.has_data:
        continue
    if b.extmax.x < x0 or b.extmin.x > x1 or b.extmax.y < y0 or b.extmin.y > y1:
        continue
    print(e.dxftype(), e.dxf.handle, e.dxf.layer, round(b.extmin.x), round(b.extmin.y), round(b.extmax.x), round(b.extmax.y))
