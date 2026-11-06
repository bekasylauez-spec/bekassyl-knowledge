import ezdxf, json
from ezdxf import bbox
d=ezdxf.readfile('../dxf/sch3.dxf'); m=d.modelspace()
res={}
for k,(fx,ins) in {'2.3':(385617,168200),'2.4':(469717,252300)}.items():
    ox=145817+ins; oy=-1686243-94542
    cs=[];bs=[]
    for e in m.query('LWPOLYLINE'):
        b=bbox.extents([e])
        if not(b.extmin.x>fx-84100 and b.extmax.x<fx): continue
        r=[round(b.extmin.x-ox),round(b.extmin.y-oy),round(b.extmax.x-ox),round(b.extmax.y-oy)]
        w=e.dxf.get('const_width',0)
        if w==0 and e.closed and max(b.size.x,b.size.y)<=1500: cs.append(r)
        elif w==30: bs.append(r)
    res[k]=dict(cols=cs,beams=bs)
    print(k,len(cs),len(bs)); print(sorted(cs)[:12])
json.dump(res,open('schgeo.json','w'))
