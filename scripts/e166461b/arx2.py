import logging; logging.disable(logging.CRITICAL)
import ezdxf, collections, pickle, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.ops import unary_union
d=ezdxf.readfile('w/main.dxf'); m=d.modelspace()
P=[('подвал',-232964,633798),('1эт',-167260,630565),('2эт',-104342,630989),('тип',-39014,632431),('тех',25815,632810),('кровля',91588,633172)]
res={}
fig,axs=plt.subplots(2,3,figsize=(36,30)); axs=axs.ravel()
for k,(nm,x1,y1) in enumerate(P):
    polys=[]; lines=[]
    for e in m:
        if e.dxftype()!='INSERT' or e.dxf.layer!='_АР_Монолит': continue
        ix,iy=e.dxf.insert[0],e.dxf.insert[1]
        if not (x1-6000<ix<x1+27000 and y1-8000<iy<y1+36000): continue
        for v in e.virtual_entities():
            t=v.dxftype()
            if t=='LWPOLYLINE':
                p=[(a[0]-x1,a[1]-y1) for a in v.get_points('xy')]
                if v.closed and len(p)>2: polys.append(Polygon(p).buffer(0))
                else: lines.append(p)
            elif t=='HATCH':
                for path in v.paths:
                    try: pts=[(a[0]-x1,a[1]-y1) for a in path.vertices]
                    except Exception: pts=[(ed.start[0]-x1,ed.start[1]-y1) for ed in path.edges]
                    if len(pts)>2: polys.append(Polygon(pts).buffer(0))
            elif t=='LINE': lines.append([(v.dxf.start[0]-x1,v.dxf.start[1]-y1),(v.dxf.end[0]-x1,v.dxf.end[1]-y1)])
    U=unary_union(polys) if polys else None
    res[nm]=(U,lines)
    ax=axs[k]; ax.set_aspect('equal'); ax.set_title(nm)
    if U is not None:
        for g in (U.geoms if hasattr(U,'geoms') else [U]):
            ax.fill(*g.exterior.xy,color='k')
    for l in lines: ax.plot([a[0] for a in l],[a[1] for a in l],'b-',lw=.5)
    for x in [0,6800,13250,20050]: ax.axvline(x,color='r',lw=.3)
    for y in [0,5000,14750,22750,28750]: ax.axhline(y,color='r',lw=.3)
    ax.set_xlim(-3000,23000); ax.set_ylim(-4000,31000)
    print(nm, len(polys), len(lines), U.area/1e6 if U else 0)
pickle.dump(res,open('armono.pkl','wb'))
fig.tight_layout(); fig.savefig('armono.png',dpi=30)
