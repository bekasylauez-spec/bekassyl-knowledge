import ezdxf,sys,collections
from ezdxf import bbox
d=ezdxf.readfile(sys.argv[1]); ms=d.modelspace()
OX,OY=-2121452,-272899
res=[]
def walk(ents,depth=0):
    for e in ents:
        t=e.dxftype()
        if t=='INSERT' and depth<3:
            try: walk(e.virtual_entities(),depth+1)
            except Exception: pass
        elif t in('LWPOLYLINE','HATCH','SOLID','POLYLINE'):
            bb=bbox.extents([e],fast=True)
            if not bb.has_data: continue
            w=bb.extmax.x-bb.extmin.x; h=bb.extmax.y-bb.extmin.y
            if 300<w<2000 and 300<h<2000:
                cx=(bb.extmax.x+bb.extmin.x)/2-OX; cy=(bb.extmax.y+bb.extmin.y)/2-OY
                if 50000<cx<90000 and -2000<cy<45000:
                    res.append((round(cx),round(cy),round(w),round(h),t,e.dxf.layer,e.dxf.color))
walk(ms)
for r in sorted(set(res),key=lambda r:(r[1],r[0])): print(r)
print(len(set(res)))
