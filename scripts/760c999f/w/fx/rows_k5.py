import ezdxf, pickle
from ezdxf import bbox
doc = ezdxf.readfile('k5.dxf'); rows = []
for e in doc.modelspace():
    try:
        b = bbox.extents([e], fast=True)
        if not b.has_data: continue
    except Exception: continue
    t = e.dxftype(); txt = ''
    if t == 'TEXT': txt = e.dxf.text
    elif t == 'MTEXT': txt = e.text
    elif t == 'ACAD_PROXY_ENTITY':
        try: txt = '|'.join((v.dxf.text if v.dxftype() == 'TEXT' else v.text) for v in e.virtual_entities() if v.dxftype() in ('TEXT', 'MTEXT'))
        except Exception: txt = '?'
    elif t == 'DIMENSION': txt = e.dxf.get('text', '')
    rows.append((e.dxf.handle, t, b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y, txt, e.dxf.layer))
pickle.dump(rows, open('k5rows.pkl', 'wb')); print(len(rows))
