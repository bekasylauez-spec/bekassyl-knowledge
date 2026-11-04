import ezdxf, sys, collections
from ezdxf import bbox
for n in sys.argv[2:]:
    d=ezdxf.readfile(f'{sys.argv[1]}/{n}.dxf')
    msp=d.modelspace()
    c=collections.Counter(e.dxftype() for e in msp)
    try: b=bbox.extents(msp, fast=True)
    except Exception as ex: b=ex
    print('==',n,'INSUNITS',d.header.get('$INSUNITS'),'LTSCALE',d.header.get('$LTSCALE'),'DIMSCALE',d.header.get('$DIMSCALE'))
    print('  msp',sum(c.values()),dict(c.most_common(12)))
    print('  ext',b.extmin if hasattr(b,'extmin') else b, b.extmax if hasattr(b,'extmax') else '')
    for l in d.layouts:
        if l.name=='Model': continue
        cc=collections.Counter(e.dxftype() for e in l)
        vps=[(round(v.dxf.center.x),round(v.dxf.center.y),round(v.dxf.width),round(v.dxf.height),round(v.dxf.view_center_point.x),round(v.dxf.view_center_point.y),round(v.dxf.view_height,1)) for v in l.query('VIEWPORT')]
        print('  layout',l.name,sum(cc.values()),dict(cc.most_common(6)),'vps',vps[:5])
    ins=collections.Counter(e.dxf.name for e in msp.query('INSERT'))
    print('  inserts',ins.most_common(8))
    print('  layers',len(d.layers), 'blocks',len(d.blocks))
