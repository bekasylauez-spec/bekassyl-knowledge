import ezdxf,sys
from ezdxf import bbox
sys.stdout.reconfigure(encoding='utf-8')
doc=ezdxf.readfile(sys.argv[1]); msp=doc.modelspace()
res=[]
for e in msp.query('ACAD_PROXY_ENTITY INSERT LWPOLYLINE'):
    try: b=bbox.extents([e])
    except Exception: continue
    if not b.has_data: continue
    w,h=b.size.x,b.size.y
    if w>2000 and h>2000 and w<200000:
        res.append((round(b.extmin.x),round(b.extmin.y),round(w),round(h),e.dxftype(),e.dxf.layer, (e.dxf.name if e.dxftype()=='INSERT' else '')))
for r in sorted(set(res),key=lambda r:(-r[1],r[0])): print(r)
