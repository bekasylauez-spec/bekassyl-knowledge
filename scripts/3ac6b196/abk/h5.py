import ezdxf, sys
from ezdxf import bbox
d = ezdxf.readfile(sys.argv[1]); m = d.modelspace()
for lay in ('S-FNDN', 'S-COLS', 'S-BEAM', 'S-STRS', 'A-ROOF', 'S-GRID'):
    for e in m:
        if e.dxf.layer != lay: continue
        b = bbox.extents([e])
        print(lay, e.dxftype(), getattr(e.dxf, 'name', ''), [round(v) for v in (b.extmin.x, b.extmin.y - 14259, b.extmax.x, b.extmax.y - 14259)])
