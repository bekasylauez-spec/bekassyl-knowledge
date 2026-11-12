# -*- coding: utf-8 -*-
"""analog.dxf -> pickle of modelspace entity summaries: handle, type, layer, bbox, text, extra"""
import ezdxf, pickle, sys
from ezdxf import bbox as BB
doc = ezdxf.readfile(r'D:\_claude_work\otst\src\analog.dxf')
msp = doc.modelspace()
out = []
cache = BB.Cache()
for e in msp:
    t = e.dxftype()
    try:
        b = BB.extents([e], cache=cache)
        bb = (b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y) if b.has_data else None
    except Exception:
        bb = None
    txt = ''
    ex = {}
    try:
        if t == 'TEXT': txt = e.dxf.text; ex = dict(h=e.dxf.height, ins=tuple(e.dxf.insert)[:2], style=e.dxf.style, rot=e.dxf.rotation)
        elif t == 'MTEXT': txt = e.text; ex = dict(h=e.dxf.char_height, ins=tuple(e.dxf.insert)[:2], style=e.dxf.style, att=e.dxf.attachment_point, w=e.dxf.get('width'))
        elif t == 'DIMENSION': txt = e.dxf.get('text', ''); ex = dict(style=e.dxf.dimstyle, meas=e.get_measurement() if hasattr(e, 'get_measurement') else None, dt=e.dimtype)
        elif t == 'INSERT':
            txt = e.dxf.name; ex = dict(ins=tuple(e.dxf.insert)[:2], att={a.dxf.tag: a.dxf.text for a in e.attribs})
        elif t == 'HATCH': txt = e.dxf.pattern_name; ex = dict(sc=e.dxf.get('pattern_scale'))
        elif t == 'CIRCLE': ex = dict(c=tuple(e.dxf.center)[:2], r=e.dxf.radius)
        elif t == 'LWPOLYLINE': ex = dict(n=len(e), lw=e.dxf.get('const_width'))
    except Exception as er:
        ex['err'] = str(er)
    out.append(dict(h=e.dxf.handle, t=t, l=e.dxf.layer, bb=bb, txt=txt, ex=ex, lt=e.dxf.get('linetype'), lw=e.dxf.get('lineweight')))
pickle.dump(out, open(sys.argv[1], 'wb'))
print(len(out))
