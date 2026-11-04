import ezdxf, sys
from ezdxf import bbox
for n in sys.argv[2:]:
    d=ezdxf.readfile(f'{sys.argv[1]}/{n}.dxf')
    l=d.layouts.get('Layout1') if n!='TOM' else None
    if l is None: continue
    ents=[e for e in l if e.dxftype()!='VIEWPORT']
    b=bbox.extents(ents, fast=True)
    print(n, [round(v,1) for v in b.extmin][:2], [round(v,1) for v in b.extmax][:2], 'lim', l.dxf_layout.dxf.get('limmin'), l.dxf_layout.dxf.get('limmax'))
