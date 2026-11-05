import ezdxf, json, sys
from ezdxf import bbox
W = {"4.1": [-646953.1, -1749172.3, -617253.1, -1728172.3]}
def ents(doc, win, margin=0):
    x0, y0, x1, y1 = win
    out = []
    cache = bbox.Cache()
    for e in doc.modelspace():
        try:
            b = bbox.extents([e], cache=cache)
        except Exception:
            continue
        if not b.has_data: continue
        if b.extmin.x >= x0 - margin and b.extmax.x <= x1 + margin and b.extmin.y >= y0 - margin and b.extmax.y <= y1 + margin:
            out.append((e, b))
    return out
