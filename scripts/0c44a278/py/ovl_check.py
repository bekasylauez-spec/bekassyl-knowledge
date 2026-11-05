import ezdxf,sys,math,collections
from ezdxf import bbox
from shapely.geometry import box, LineString
from shapely.strtree import STRtree
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
win=list(map(float,sys.argv[2:6]))
def tbox(e):
    t=e.dxftype()
    try:
        if t=='TEXT':
            s=e.dxf.text; h=e.dxf.height; w=0.85*h*len(s)*e.dxf.get('width',1)
            p=e.dxf.insert if e.dxf.halign==0 and e.dxf.valign==0 else e.dxf.get('align_point',e.dxf.insert)
            a=math.radians(e.dxf.rotation)
            hal=e.dxf.halign; dx={0:0,1:-w/2,2:-w,4:-w/2}.get(hal,0); dy={0:0,1:0,2:-h/2,3:-h}.get(e.dxf.valign,0)
            pts=[(dx,dy),(dx+w,dy),(dx+w,dy+h),(dx,dy+h)]
            return [ (p.x+x*math.cos(a)-y*math.sin(a), p.y+x*math.sin(a)+y*math.cos(a)) for x,y in pts], s
        if t=='MTEXT':
            b=bbox.extents([e],fast=False); return [(b.extmin.x,b.extmin.y),(b.extmax.x,b.extmin.y),(b.extmax.x,b.extmax.y),(b.extmin.x,b.extmax.y)], e.plain_text()[:20]
    except Exception as ex: return None
    return None
T=[]; L=[]
for e in m:
    try: b=bbox.extents([e],fast=True)
    except: continue
    if not b.has_data or b.extmax.x<win[0] or b.extmin.x>win[2] or b.extmax.y<win[1] or b.extmin.y>win[3]: continue
    t=e.dxftype()
    if t in('TEXT','MTEXT'):
        r=tbox(e)
        if r: T.append((r[0],r[1],e.dxf.handle))
    elif t=='DIMENSION':
        for v in e.virtual_entities():
            if v.dxftype() in('TEXT','MTEXT'):
                r=tbox(v)
                if r: T.append((r[0],r[1],e.dxf.handle))
    elif t=='MULTILEADER':
        for v in e.virtual_entities():
            if v.dxftype() in('TEXT','MTEXT'):
                r=tbox(v)
                if r: T.append((r[0],r[1],e.dxf.handle))
    if t=='LINE' and e.dxf.layer.startswith('ф'):
        L.append((LineString([e.dxf.start[:2],e.dxf.end[:2]]),e.dxf.handle))
from shapely.geometry import Polygon
P=[Polygon(q[0]).buffer(-15) for q in T]
n=0; out=[]
for i in range(len(P)):
    for j in range(i+1,len(P)):
        if T[i][2]==T[j][2]: continue
        if P[i].intersects(P[j]): n+=1; out.append(('TT',T[i][1],T[j][1],round(P[i].centroid.x),round(P[i].centroid.y)))
nl=0
for i,p in enumerate(P):
    for ls,h in L:
        if p.intersects(ls): nl+=1; out.append(('TL',T[i][1],h,round(p.centroid.x),round(p.centroid.y))); break
print('texts',len(T),'text/text',n,'text/bar',nl)
for o in out[:int(sys.argv[6]) if len(sys.argv)>6 else 40]: print(o)
