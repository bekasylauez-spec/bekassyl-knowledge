import json,math,numpy as np,pickle
from scipy import ndimage
import geom, design as D0
S=geom.S
DIAS=D0.DIAS; asd=D0.asd; BASE=D0.BASE; H=100
def need_d(v): return next((dd for dd in DIAS if asd(dd)>=v-0.1),25)
def build(z,face,RAS):
    R=RAS[z]; dirn='X' if face in(0,1) else 'Y'; sl=R['sl']
    A=R['A'][face]
    As=ndimage.uniform_filter1d(A,size=5,axis=0 if dirn=='X' else 1)
    add=(As-BASE)*R['M']
    m=add>0.12
    m=ndimage.binary_closing(m,structure=np.ones((5,5)))&R['M'] | m
    lab,n=ndimage.label(m,structure=np.ones((3,3)))
    lines=D0.lines_for(z,dirn)
    zones=[]
    for k in range(1,n+1):
        jj,ii=np.where(lab==k)
        vals=add[jj,ii]; area=len(jj)*H*H/1e6; peak=vals.max()
        if area<1.0 and peak<1.3: continue
        xs=R['x0']+ii*H; ys=R['y0']+jj*H
        # Ø by the 0.25 m2 most loaded (ignore single-cell singularity)
        sv=np.sort(vals)[::-1]; nk=max(1,int(0.10e6/(H*H))); dneed=need_d(sv[min(nk,len(sv))-1])
        dmax=need_d(peak)
        d=dmax if (sv>=asd(dneed)+0.1).sum()*H*H/1e6>=0.06 else dneed
        d=max(d,10)
        la=math.ceil(40*d/50)*50
        if dirn=='X': a0,a1=xs.min(),xs.max()+H; c0,c1=ys.min(),ys.max()+H
        else: a0,a1=ys.min(),ys.max()+H; c0,c1=xs.min(),xs.max()+H
        S0,E0=a0-la,a1+la
        L=E0-S0; L2=math.ceil(L/300)*300; S0-=(L2-L)/2; E0+=(L2-L)/2
        cl=[c for c in lines if c0-200<=c<=c1+200]
        if not cl:
            cl=[min(lines,key=lambda c:abs(c-(c0+c1)/2))]
        for c in cl:
            for (s,e) in D0.segs_on_slab(z,dirn,c,sl):
                lo,hi=max(s,S0),min(e,E0)
                if hi-lo<300: continue
                # required part must touch this segment
                if min(hi,a1)-max(lo,a0)<=0: continue
                # restore length if clipped at one end
                Lw=E0-S0
                if lo>S0: hi=min(e,lo+Lw)
                if hi<E0: lo=max(s,hi-Lw)
                zones.append(dict(c=c,s=round(lo),e=round(hi),d=d,comp=(z,face,k),need=peak,area=area))
    return zones
def regroup(lst):
    # lines with identical s,e,d consecutive (step 200) -> zone
    lst=sorted(lst,key=lambda q:(q['s'],q['e'],q['d'],q['c']))
    Z=[]
    for q in lst:
        if Z and Z[-1]['s']==q['s'] and Z[-1]['e']==q['e'] and Z[-1]['d']==q['d'] and q['c']-Z[-1]['cs'][-1]==200:
            Z[-1]['cs'].append(q['c']); Z[-1]['need']=max(Z[-1]['need'],q['need'])
        else: Z.append(dict(cs=[q['c']],s=q['s'],e=q['e'],d=q['d'],need=q['need']))
    return Z
def resolve(lines):
    # per line: overlapping segments of different zones on one line -> merge into one bar (max d)
    by={}
    for q in lines: by.setdefault(q['c'],[]).append(q)
    out=[]
    for c,L in by.items():
        L.sort(key=lambda q:q['s']); cur=None
        for q in L:
            if cur and q['s']<cur['e']+50:
                cur['e']=max(cur['e'],q['e']); cur['d']=max(cur['d'],q['d']); cur['need']=max(cur['need'],q['need'])
            else:
                if cur: out.append(cur)
                cur=dict(q)
        out.append(cur)
    for q in out:
        L=q['e']-q['s']; 
        if L%300: q['e']=q['s']+math.ceil(L/300)*300  # keep multiple of 300 (may need clip)
    return out
if __name__=='__main__':
    res={}; RAS={}
    for z in ('7.0','4.5'):
        RAS[z]=D0.raster(z); D0.RAS[z]=RAS[z]; res[z]={}
        for f in range(4):
            ln=build(z,f,RAS)
            ln=resolve(ln)
            # clip back to slab after the 300 rounding
            dirn='X' if f<2 else 'Y'
            for q in ln:
                for (s,e) in D0.segs_on_slab(z,dirn,q['c'],RAS[z]['sl']):
                    if s-1<=q['s']<=e+1:
                        if q['e']>e: sh=q['e']-e; q['e']=e; q['s']=max(s,q['s']-sh)
            Z=regroup(ln)
            for zz in Z: zz['L']=int(zz['e']-zz['s'])
            res[z][f]=Z
            print(z,f,'zones',len(Z),'single',sum(len(q['cs'])<2 for q in Z),'maxd',max([q['d'] for q in Z] or [0]),'Lmax',max([q['L'] for q in Z] or [0]))
    pickle.dump((res,{z:{k:v for k,v in RAS[z].items() if k!='sl'} for z in RAS}),open(S+r'\design.pkl','wb'))
