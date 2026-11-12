# -*- coding: utf-8 -*-
"""analog.dxf -> per-entity summary (pickle) for oformlenie passport."""
import ezdxf, pickle, sys
from ezdxf import bbox
doc = ezdxf.readfile(r'D:\_claude_work\otst\src\analog.dxf')
msp = doc.modelspace()
cache = bbox.Cache()
rows = []
for e in msp:
    t = e.dxftype()
    d = dict(h=e.dxf.handle, t=t, layer=e.dxf.get('layer', ''), lt=e.dxf.get('linetype', 'BYLAYER'),
             lts=e.dxf.get('ltscale', 1.0), lw=e.dxf.get('lineweight', -1), col=e.dxf.get('color', 256))
    try:
        b = bbox.extents([e], cache=cache)
        if b.has_data: d['bb'] = (b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y)
    except Exception:
        pass
    try:
        if t == 'MTEXT':
            d.update(txt=e.text, ht=e.dxf.char_height, st=e.dxf.style, ins=tuple(e.dxf.insert)[:2], att=e.dxf.attachment_point, w=e.dxf.get('width', 0))
        elif t == 'TEXT':
            d.update(txt=e.dxf.text, ht=e.dxf.height, st=e.dxf.style, ins=tuple(e.dxf.insert)[:2])
        elif t == 'DIMENSION':
            ov = e.dim_style_overrides() if hasattr(e, 'dim_style_overrides') else {}
            d.update(ds=e.dxf.dimstyle, txt=e.dxf.get('text', ''), dt=e.dimtype, meas=e.dxf.get('actual_measurement', None))
            try:
                ov = e.override()
                d['dimlfac'] = ov.get('dimlfac', None); d['dimscale'] = ov.get('dimscale', None); d['dimtxt'] = ov.get('dimtxt', None)
            except Exception:
                pass
            d['p1'] = tuple(e.dxf.get('defpoint2', (0, 0)))[:2]; d['p2'] = tuple(e.dxf.get('defpoint3', (0, 0)))[:2]
        elif t == 'HATCH':
            d.update(pat=e.dxf.pattern_name, psc=e.dxf.get('pattern_scale', 1), pang=e.dxf.get('pattern_angle', 0))
        elif t == 'INSERT':
            d.update(blk=e.dxf.name, ins=tuple(e.dxf.insert)[:2], sx=e.dxf.get('xscale', 1))
        elif t in ('LWPOLYLINE',):
            d.update(np=len(e), cw=e.dxf.get('const_width', 0))
        elif t == 'CIRCLE':
            d.update(c=tuple(e.dxf.center)[:2], r=e.dxf.radius)
        elif t == 'ACAD_TABLE':
            d.update(nr=e.dxf.get('n_rows', 0), nc=e.dxf.get('n_cols', 0))
    except Exception as ex:
        d['err'] = str(ex)
    rows.append(d)
pickle.dump(rows, open(sys.argv[1], 'wb'))
lay = {}
for L in doc.layers:
    lay[L.dxf.name] = (L.dxf.get('lineweight', -3), L.dxf.get('linetype', ''), L.dxf.get('color', 7))
pickle.dump(lay, open(sys.argv[1] + '.lay', 'wb'))
ds = {}
for s in doc.dimstyles:
    ds[s.dxf.name] = {k: s.dxf.get(k) for k in ('dimscale', 'dimlfac', 'dimtxt', 'dimtxsty', 'dimasz', 'dimblk', 'dimexo', 'dimexe', 'dimgap', 'dimclrd', 'dimtad')}
pickle.dump(ds, open(sys.argv[1] + '.ds', 'wb'))
st = {s.dxf.name: (s.dxf.font, s.dxf.get('width', 1)) for s in doc.styles}
pickle.dump(st, open(sys.argv[1] + '.st', 'wb'))
print(len(rows))
