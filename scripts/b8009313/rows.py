import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8")
import ezdxf,collections
from ezdxf.proxygraphic import ProxyGraphic
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
axes=[]
for e in m.query('ACAD_PROXY_ENTITY'):
    try: vs=list(ProxyGraphic(e.proxy_graphic,d).virtual_entities())
    except: continue
    tx=[v.dxf.text for v in vs if v.dxftype()=='TEXT']; cs=[v for v in vs if v.dxftype()=='CIRCLE']
    if len(tx)==1 and cs and len(tx[0])<=4 :
        ls=[v for v in vs if v.dxftype() in('LINE','LWPOLYLINE','POLYLINE')]
        pts=[]
        for v in ls:
            if v.dxftype()=='LINE': pts+=[v.dxf.start,v.dxf.end]
            elif v.dxftype()=='LWPOLYLINE': pts+=[ezdxf.math.Vec3(p[0],p[1]) for p in v.get_points()]
            else: pts+=[q.dxf.location for q in v.vertices]
        xs=[p.x for p in pts];ys=[p.y for p in pts]
        if not xs: continue
        horiz=(max(xs)-min(xs))>(max(ys)-min(ys))
        axes.append((tx[0],horiz,min(xs),max(xs),min(ys),max(ys),e.dxf.handle))
for a in axes: print('AX',a[0],'H' if a[1] else 'V',[round(v,1) for v in a[2:6]],a[6])
cols=collections.defaultdict(list)
for e in m.query('INSERT'):
    if e.dxf.layer=='Несущие колонны':
        cols[round(e.dxf.insert.y)].append(round(e.dxf.insert.x,1))
for y in sorted(cols): print('COLROW y',y,len(cols[y]),min(cols[y]),max(cols[y]))
xs=collections.defaultdict(list)
for e in m.query('INSERT'):
    if e.dxf.layer=='Несущие колонны': xs[int(e.dxf.insert.x//14850)].append(round(e.dxf.insert.x,1))
for k in sorted(xs): print('COLX', sorted(set(xs[k])))
