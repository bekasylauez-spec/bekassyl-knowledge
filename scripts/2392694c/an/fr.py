import ezdxf, sys
from ezdxf import bbox
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
print(d.header.get('$EXTMIN'), d.header.get('$EXTMAX'))
# AR_STAMP texts = sheet titles; find stamp geometry extents near each
ts=[(e.dxf.insert.x,e.dxf.insert.y,(e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text)) for e in m.query('TEXT MTEXT[layer=="AR_STAMP"]')]
for e in m.query('*[layer=="AR_STAMP"]'):
    pass
items=[e for e in m.query('LINE LWPOLYLINE INSERT[layer=="AR_STAMP"]')]
print(len(items))
import collections
for x,y,t in sorted(ts):
    if len(t)>25:
        bb=bbox.extents([e for e in items if abs(bbox.extents([e]).center.x-x)<12000 and abs(bbox.extents([e]).center.y-y)<8000])
        print(round(x),round(y),bb.extmin.round(0) if bb.has_data else None, bb.extmax.round(0) if bb.has_data else None, t[:60])
