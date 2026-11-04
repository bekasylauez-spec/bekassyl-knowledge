import ezdxf, re, sys
from ezdxf import bbox
f, rx = sys.argv[1], sys.argv[2]
doc = ezdxf.readfile(f + '.dxf')
for e in doc.modelspace():
    t = e.dxftype(); txt = ''
    if t == 'TEXT': txt = e.dxf.text
    elif t == 'MTEXT': txt = e.text
    elif t == 'ACAD_PROXY_ENTITY':
        try: txt = '|'.join(v.dxf.text if v.dxftype() == 'TEXT' else v.text for v in e.virtual_entities() if v.dxftype() in ('TEXT', 'MTEXT'))
        except Exception: pass
    elif t == 'INSERT':
        txt = e.dxf.name + ':' + '|'.join(a.dxf.text for a in e.attribs)
    if re.search(rx, txt):
        try:
            b = bbox.extents([e], fast=True); pos = (round(b.extmin.x), round(b.extmin.y), round(b.extmax.x), round(b.extmax.y))
        except Exception: pos = ''
        print(e.dxf.handle, t, pos, e.dxf.layer, repr(txt[:150]))
