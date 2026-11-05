import ezdxf, sys
from ezdxf import bbox
d = ezdxf.readfile(sys.argv[1]); m = d.modelspace()
for e in m.query('HATCH'):
    if e.dxf.layer.startswith('PDF'): continue
    b = bbox.extents([e])
    print(e.dxf.layer, e.dxf.pattern_name, [round(v) for v in (b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y)], round(b.size.x), round(b.size.y))
for e in m.query('LINE[layer=="S-BEAM"] LINE[layer=="S-COLS"] LINE[layer=="S-STRS"] INSERT[layer=="S-FNDN"] LINE[layer=="A-ROOF"]'):
    if e.dxftype() == 'LINE':
        print(e.dxf.layer, [round(v) for v in (e.dxf.start.x, e.dxf.start.y, e.dxf.end.x, e.dxf.end.y)])
    else:
        b = bbox.extents([e]); print(e.dxf.layer, e.dxf.name, [round(v) for v in (b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y)])
