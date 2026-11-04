import ezdxf,sys
from ezdxf import bbox
f=sys.argv[2]; x0,y0,x1,y1=[float(v) for v in sys.argv[3].split(',')]
d=ezdxf.readfile(sys.argv[1]+'/ar/'+f+'.dxf'); m=d.modelspace()
def r(p): return (round(p[0],1),round(p[1],1))
for e in m:
    t=e.dxftype()
    if t=='LINE':
        a,b=e.dxf.start,e.dxf.end
        if x0<=min(a[0],b[0]) and max(a[0],b[0])<=x1 and y0<=min(a[1],b[1]) and max(a[1],b[1])<=y1:
            print('L',e.dxf.layer,r(a),r(b))
    elif t in('HATCH','INSERT','LWPOLYLINE'):
        try:
            bb=bbox.extents([e])
            if bb.has_data and x0<=bb.extmin[0] and bb.extmax[0]<=x1 and y0<=bb.extmin[1] and bb.extmax[1]<=y1:
                print(t,e.dxf.layer,getattr(e.dxf,'name','')[:50],r(bb.extmin),r(bb.extmax), getattr(e.dxf,'pattern_name',''))
        except Exception as ex: pass
