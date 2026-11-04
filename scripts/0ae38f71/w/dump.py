import ezdxf, sys
from ezdxf import bbox
doc = ezdxf.readfile(sys.argv[5] if len(sys.argv)>5 else 'live1.dxf')
msp = doc.modelspace()
X0,Y0,X1,Y1 = map(float, sys.argv[1:5])
out=[]; cache = bbox.Cache()
def lay(e):
    try: return e.dxf.layer
    except Exception: return '-'
for e in msp:
    try: b = bbox.extents([e], cache=cache, fast=True)
    except Exception: continue
    if not b.has_data: continue
    if b.extmax.x < X0 or b.extmin.x > X1 or b.extmax.y < Y0 or b.extmin.y > Y1: continue
    t=e.dxftype(); s=''
    try:
        if t=='TEXT': s=e.dxf.text
        elif t=='MTEXT': s=e.text
        elif t=='INSERT': s=e.dxf.name+' sc=%.3g'%e.dxf.xscale
        elif t=='DIMENSION': s='"%s" m=%.1f'%(e.dxf.get('text',''), e.get_measurement())
        elif t=='LWPOLYLINE': s='n=%d w=%.3g col=%s'%(len(e), e.dxf.get('const_width',0), e.dxf.get('color',256))
    except Exception as ex: s='?'
    out.append((t,e.dxf.handle,lay(e),round(b.extmin.x),round(b.extmin.y),round(b.extmax.x),round(b.extmax.y),s.replace('\n',' ')[:60]))
for o in sorted(out,key=lambda o:(o[0],o[4])): print(*o)
