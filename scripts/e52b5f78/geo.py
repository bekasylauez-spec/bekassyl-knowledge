import ezdxf,sys,json,pickle
from collections import Counter
d=ezdxf.readfile("dx/abk.dxf")
vp=json.load(open("dx/abk_vp.json",encoding='utf-8'))
ms=d.modelspace()
def win(n): return [v for v in vp[n] if v[4]>1][0]
def inw(p,w): return w[0]<=p[0]<=w[2] and w[1]<=p[1]<=w[3]
for n in ['1.3','3.1','5.1','1.4']:
    w=win(n); print('=====',n,w)
    cc=Counter(); pl=[]
    for e in ms:
        t=e.dxftype()
        try:
            if t=='CIRCLE':
                c=e.dxf.center
                if inw(c,w): cc[(e.dxf.layer,round(e.dxf.radius))]+=1
            elif t=='LWPOLYLINE':
                pts=[(p[0],p[1]) for p in e.get_points()]
                if not inw(pts[0],w): continue
                a=0;per=0
                m=len(pts)
                for i in range(m if e.closed else m-1):
                    x1,y1=pts[i];x2,y2=pts[(i+1)%m]
                    a+=x1*y2-x2*y1; per+=((x2-x1)**2+(y2-y1)**2)**.5
                xs=[p[0] for p in pts];ys=[p[1] for p in pts]
                pl.append((e.dxf.layer,e.closed,m,round(abs(a)/2e6,2),round(per),round(max(xs)-min(xs)),round(max(ys)-min(ys)),e.dxf.handle,round(min(xs)-w[0]),round(min(ys)-w[1])))
            elif t=='INSERT':
                if inw(e.dxf.insert,w): cc[('INS',e.dxf.name,e.dxf.layer)]+=1
            elif t=='ACAD_PROXY_ENTITY': pass
        except Exception as ex: pass
    for k,v in sorted(cc.items(),key=lambda x:-x[1])[:25]: print('  ',k,v)
    g=Counter((p[0],p[1],p[2],p[3],p[4],p[5],p[6]) for p in pl)
    for k,v in sorted(g.items(),key=lambda x:-x[0][3])[:40]: print('  PL',k,'x',v)
