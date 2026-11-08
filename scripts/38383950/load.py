import ezdxf, pickle, sys
from ezdxf import recover
doc, aud = recover.readfile('src.dxf')
msp = doc.modelspace()
L=[];T=[]
for e in msp:
    t=e.dxftype(); la=e.dxf.get('layer','')
    try:
        if t=='LINE': L.append((la,e.dxf.start.x,e.dxf.start.y,e.dxf.end.x,e.dxf.end.y))
        elif t=='LWPOLYLINE':
            pts=[(p[0],p[1]) for p in e.get_points()]
            if e.closed: pts.append(pts[0])
            for a,b in zip(pts,pts[1:]): L.append((la,a[0],a[1],b[0],b[1]))
        elif t in('TEXT','MTEXT'):
            s=e.dxf.text if t=='TEXT' else e.plain_text()
            p=e.dxf.insert; T.append((la,p.x,p.y,s))
        elif t=='INSERT':
            p=e.dxf.insert; T.append(('INS:'+e.dxf.name,p.x,p.y,e.dxf.name))
        elif t=='ACAD_PROXY_ENTITY' or t.startswith('MCS') :
            pass
    except Exception as ex: pass
lay={}
for l in doc.layouts:
    if l.name=='Model': continue
    vps=[(v.dxf.view_center_point.x,v.dxf.view_center_point.y,v.dxf.view_height,v.dxf.width,v.dxf.height) for v in l.query('VIEWPORT')]
    lay[l.name]=vps
pickle.dump((L,T,lay),open('geo.pkl','wb'))
print(len(L),len(T)); print({k:v for k,v in lay.items()})
