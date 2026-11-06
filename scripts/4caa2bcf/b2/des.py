import json, math, sys
asl=json.load(open('aslines.json')); marks={m['mark']:m for m in json.load(open('marks.json'))}
A25=4.909
def env(mk):
    m=marks[mk]; key=lambda c: '|'.join(map(str,[m['z'],m['d'],c,m['s']]))
    pts=[]
    for c in m['lines']:
        p=asl[key(c)]; x0=p[0][0]
        pts+= [(round(q[0]-x0,3),)+tuple(q[1:]) for q in p]
    return m, sorted(pts)
def zones(mk):
    m,pts=env(mk); sp=m['sup']; out=[]
    for i in range(len(sp)-1):
        a,b=sp[i],sp[i+1]; L=b-a
        def mx(lo,hi,k): v=[q[k] for q in pts if lo-1e-6<=q[0]<=hi+1e-6]; return max(v) if v else 0
        out.append(dict(span=i,a=a,b=b,L=L, topL=mx(a,a+L/3,2), topR=mx(b-L/3,b,2), topM=mx(a+L/3,b-L/3,2), bot=mx(a,b,1),
                        botM=mx(a+L/4,b-L/4,1), swS=max(mx(a,a+L/4,3),mx(b-L/4,b,3)), swM=mx(a+L/4,b-L/4,3)))
    return m,out
if __name__=='__main__':
    m,z=zones(sys.argv[1]); print(m['mark'],m['s'],m['sup'])
    for q in z: print({k:(round(v,2) if isinstance(v,float) else v) for k,v in q.items()})
