import sys, ezdxf
from ezdxf import bbox
doc = ezdxf.readfile(sys.argv[1]); msp = doc.modelspace()
for e in msp.query('INSERT'):
    n = e.dxf.name
    if n.endswith('1') and len(n) == 6 or 'В109' in n or '109' in n:
        try:
            b = bbox.extents([e])
            print(n.encode('utf-8', 'replace').decode('utf-8'), round(e.dxf.insert.x), round(e.dxf.insert.y), round(e.dxf.xscale, 2), 'bbox', round(b.extmin.x), round(b.extmin.y), round(b.extmax.x), round(b.extmax.y))
        except Exception as ex:
            print(n, 'err', ex)
