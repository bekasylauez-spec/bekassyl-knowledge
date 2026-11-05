import json,math,numpy as np,sys,pickle
from matplotlib.path import Path
from scipy import ndimage
from shapely.geometry import LineString, box
from shapely.prepared import prep
import geom
S=geom.S
DIAS=[10,12,14,16,18,20,22,25]
def asd(d,s=200): return math.pi*d*d/4/100/(s/1000)  # cm2/m
BASE=asd(10)
H=100
def raster(z):
    D=json.load(open(S+r'\as.json'))[z]
    sl=geom.slab(z); x0,y0,x1,y1=sl['outer'].bounds
    nx=int((x1-x0)/H)+1; ny=int((y1-y0)/H)+1
    A=np.zeros((4,ny,nx)); M=np.zeros((ny,nx),bool)
    X,Y=np.meshgrid(x0+(np.arange(nx)+0.5)*H, y0+(np.arange(ny)+0.5)*H)
    P=np.c_[X.ravel(),Y.ravel()]
    for d in D:
        pts=[(p[0]*1000,p[1]*1000) for p in d['p']]
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        i0=max(0,int((min(xs)-x0)/H)-1); i1=min(nx,int((max(xs)-x0)/H)+2); j0=max(0,int((min(ys)-y0)/H)-1); j1=min(ny,int((max(ys)-y0)/H)+2)
        sub=np.c_[X[j0:j1,i0:i1].ravel(),Y[j0:j1,i0:i1].ravel()]
        m=Path(pts).contains_points(sub).reshape(j1-j0,i1-i0)
        for k in range(4): A[k,j0:j1,i0:i1][m]=np.maximum(A[k,j0:j1,i0:i1][m],d['a'][k])
    # extend values to the slab edge strip (250 beyond LIRA mesh) by nearest
    g=prep(sl['geom'])
    from shapely.geometry import Point
    Ms=np.array([g.contains(Point(p)) for p in P]).reshape(ny,nx)
    filled=A[0]+A[1]+A[2]+A[3]>0
    idx=ndimage.distance_transform_edt(~filled,return_distances=False,return_indices=True)
    for k in range(4): A[k]=A[k][idx[0],idx[1]]*Ms
    return dict(A=A,M=Ms,x0=x0,y0=y0,nx=nx,ny=ny,sl=sl)
def lines_for(z,dirn,base=False):
    ax=sorted(geom.AXY.values()) if dirn=='X' else sorted(v for k,v in geom.AXX.items() if k!='14')
    if z=='4.5':
        ax=[0,9000] if dirn=='X' else [12000,18000,24000,30000]
    out=[]
    for a,b in zip(ax[:-1],ax[1:]):
        st=300 if base else 400
        v=a+st
        while v<=b-st+1: out.append(v); v+=200
    return out
def segs_on_slab(z,dirn,c,sl,cover=25):
    if dirn=='X': L=LineString([(sl['outer'].bounds[0]-10,c),(sl['outer'].bounds[2]+10,c)])
    else: L=LineString([(c,sl['outer'].bounds[1]-10),(c,sl['outer'].bounds[3]+10)])
    I=L.intersection(sl['geom'])
    # remove portions inside parallel beams (+50)
    for b in sl['beams']:
        w=b[2]-b[0]; h=b[3]-b[1]
        par=(w>h) if dirn=='X' else (h>w)
        if par and min(w,h)<=700: I=I.difference(box(b[0]-50,b[1]-50,b[2]+50,b[3]+50).intersection(box(b[0]-5e4,b[1]-50,b[2]+5e4,b[3]+50) if dirn=='X' else box(b[0]-50,b[1]-5e4,b[2]+50,b[3]+5e4)).buffer(0) if False else box(b[0]-50,b[1]-50,b[2]+50,b[3]+50))
    res=[]
    gs=[I] if I.geom_type=='LineString' else list(getattr(I,'geoms',[]))
    for g in gs:
        if g.is_empty or g.length<300: continue
        cs=[p[0] if dirn=='X' else p[1] for p in g.coords]
        res.append((min(cs)+cover,max(cs)-cover))
    return res
def design(z,face):
    R=RAS[z]; A=R['A'][face]; dirn='X' if face in(0,1) else 'Y'
    # As_avg across the bar over ~2 plates (500 mm)
    As=ndimage.uniform_filter1d(A, size=5, axis=0 if dirn=='X' else 1)
    sl=R['sl']; zones_lines=[]
    for c in lines_for(z,dirn):
        segs=segs_on_slab(z,dirn,c,sl)
        if dirn=='X':
            j=int((c-R['y0'])/H); prof=As[j,:]; coord=R['x0']+(np.arange(R['nx'])+0.5)*H
        else:
            i=int((c-R['x0'])/H); prof=As[:,i]; coord=R['y0']+(np.arange(R['ny'])+0.5)*H
        add=prof-BASE
        for (s,e) in segs:
            m=(coord>=s)&(coord<=e)&(add>0.12)
            if not m.any(): continue
            # runs
            idx=np.where(m)[0]; runs=[]; st=idx[0]; pv=idx[0]
            for q in idx[1:]:
                if q-pv>6: runs.append((st,pv)); st=q
                pv=q
            runs.append((st,pv))
            for a,b in runs:
                need=add[a:b+1].max()
                d=next((dd for dd in DIAS if asd(dd)>=need-0.1),25)
                la=math.ceil(40*d/50)*50
                rs=coord[a]-H/2-la; re=coord[b]+H/2+la
                L=re-rs; L2=math.ceil(L/300)*300; ex=(L2-L)/2; rs-=ex; re+=ex
                if rs<s: re=min(e,re+(s-rs)); rs=s
                if re>e: rs=max(s,rs-(re-e)); re=e
                zones_lines.append(dict(c=c,s=rs,e=re,d=d,need=need,area=(b-a+1)*H*200/1e6,seg=(s,e)))
    return zones_lines
def group(z,face,ls):
    dirn='X' if face in(0,1) else 'Y'
    ls=sorted(ls,key=lambda q:(q['c'],q['s'])); zones=[]
    for q in ls:
        best=None
        for Z in zones:
            if abs(Z['cs'][-1]-q['c'])==200 and min(Z['e'],q['e'])-max(Z['s'],q['s'])>0.5*min(Z['e']-Z['s'],q['e']-q['s']) and Z['seg']==q['seg'] and Z['last']!=q['c']:
                best=Z; break
            if abs(Z['cs'][-1]-q['c'])==200 and min(Z['e'],q['e'])-max(Z['s'],q['s'])>0.5*min(Z['e']-Z['s'],q['e']-q['s']) and Z['last']!=q['c']:
                # different slab segment (crossing hole) -> only if union fits both segments
                pass
        if best:
            best['cs'].append(q['c']); best['s']=min(best['s'],q['s']); best['e']=max(best['e'],q['e']); best['d']=max(best['d'],q['d']); best['need']=max(best['need'],q['need']); best['area']+=q['area']; best['last']=q['c']
        else:
            zones.append(dict(cs=[q['c']],s=q['s'],e=q['e'],d=q['d'],need=q['need'],area=q['area'],seg=q['seg'],last=q['c']))
    return zones
def fit(z,face,Z):
    """make all bars of a zone the same [s,e], valid on every line; round to 300"""
    dirn='X' if face in(0,1) else 'Y'; sl=RAS[z]['sl']
    L=Z['e']-Z['s']; L2=math.ceil(L/300)*300; ex=(L2-L)/2; s=Z['s']-ex; e=Z['e']+ex
    for c in Z['cs']:
        for (a,b) in segs_on_slab(z,dirn,c,sl):
            if a-1<=Z['s'] and Z['e']<=b+1:
                if s<a: e=min(b,e+(a-s)); s=a
                if e>b: s=max(a,s-(e-b)); e=b
    Z['s'],Z['e']=round(s),round(e); Z['L']=int(round((Z['e']-Z['s'])/10)*10)
    ok=True
    for c in Z['cs']:
        if not any(a-1<=Z['s'] and Z['e']<=b+1 for a,b in segs_on_slab(z,dirn,c,sl)): ok=False
    Z['ok']=ok; return Z
RAS={}
if __name__=='__main__':
    res={}
    for z in ('7.0','4.5'):
        RAS[z]=raster(z); res[z]={}
        for f in range(4):
            ls=design(z,f); zs=group(z,f,ls)
            zs=[fit(z,f,Z) for Z in zs]
            keep=[Z for Z in zs if not (Z['area']<1.0 and Z['need']<1.3)]
            res[z][f]=keep
            print(z,f,'lines',len(ls),'zones',len(zs),'keep',len(keep),'bad',sum(not Z['ok'] for Z in keep),'maxd',max([Z['d'] for Z in keep] or [0]))
    pickle.dump((res,{z:{k:v for k,v in RAS[z].items() if k!='sl'} for z in RAS}),open(S+r'\design.pkl','wb'))
