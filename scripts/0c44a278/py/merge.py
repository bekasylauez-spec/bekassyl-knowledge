import pickle,math
import geom, design as D0
S=geom.S
def valid(z,dirn,c,s,e):
    return any(a-1<=s and e<=b+1 for a,b in D0.segs_on_slab(z,dirn,c,D0.RAS[z]['sl']))
def allines(z,dirn,c0,c1):
    return [c for c in D0.lines_for(z,dirn) if c0<=c<=c1]
def try_merge(z,dirn,A,B):
    if abs(DI(A['d'])-DI(B['d']))>1: return None
    a0,a1=min(A['cs']),max(A['cs']); b0,b1=min(B['cs']),max(B['cs'])
    gap=max(b0-a1,a0-b1)
    if gap>1300: return None
    s=min(A['s'],B['s']); e=max(A['e'],B['e']); L=e-s
    if L>1.35*max(A['L'],B['L'])+1: return None
    if min(A['e'],B['e'])-max(A['s'],B['s'])< 0.4*min(A['L'],B['L']): return None
    L2=math.ceil(L/300)*300; e=s+L2
    cs=allines(z,dirn,min(a0,b0),max(a1,b1))
    ok=[c for c in cs if valid(z,dirn,c,s,e)]
    # lines blocked by a parallel beam are skipped; any other invalid line -> reject
    if not (set(A['cs'])|set(B['cs']))<=set(ok): return None
    return dict(cs=ok,s=s,e=e,d=max(A['d'],B['d']),need=max(A['need'],B['need']),L=int(e-s))
DI=lambda d: D0.DIAS.index(d)
def overlaps(A,B):
    return set(A['cs'])&set(B['cs']) and min(A['e'],B['e'])>max(A['s'],B['s'])-50
def run(z,f,Z):
    dirn='X' if f<2 else 'Y'
    changed=True
    while changed:
        changed=False
        Z.sort(key=lambda q:(q['s'],min(q['cs'])))
        for i in range(len(Z)):
            for j in range(i+1,len(Z)):
                M=try_merge(z,dirn,Z[i],Z[j])
                if M and not any(overlaps(M,Z[k]) for k in range(len(Z)) if k not in(i,j)):
                    Z[i]=M; del Z[j]; changed=True; break
            if changed: break
    return Z
if __name__=='__main__':
    res,RS=pickle.load(open(S+r'\design.pkl','rb'))
    for z in res:
        D0.RAS[z]=D0.raster(z)
        for f in res[z]:
            n0=len(res[z][f]); res[z][f]=run(z,f,res[z][f])
            bad=sum(1 for i,A in enumerate(res[z][f]) for B in res[z][f][i+1:] if overlaps(A,B))
            print(z,f,n0,'->',len(res[z][f]),'single',sum(len(q['cs'])<2 for q in res[z][f]),'overlap',bad)
    pickle.dump((res,RS),open(S+r'\design.pkl','wb'))
