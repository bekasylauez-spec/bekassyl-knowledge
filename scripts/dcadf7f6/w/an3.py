import pickle,collections
m=pickle.load(open('geo.pkl','rb'));N=m['nodes']
C=collections.defaultdict(list);Bm=collections.defaultdict(list)
for ns in m['bars']:
    a,b=N[ns[0]-1],N[ns[1]-1]
    if abs(a[0]-b[0])<1e-3 and abs(a[1]-b[1])<1e-3: C[(round(a[0],2),round(a[1],2))].append((min(a[2],b[2]),max(a[2],b[2])))
    else:
        z=round(a[2],2); Bm[z].append((a,b))
for k,v in sorted(C.items()): print('col',k,min(x[0] for x in v),max(x[1] for x in v),len(v))
for z,L in sorted(Bm.items()):
    xs=sorted(set(round(p[0],2) for s in L for p in s)); ys=sorted(set(round(p[1],2) for s in L for p in s))
    dirs=collections.Counter('X' if abs(a[1]-b[1])<1e-3 else ('Y' if abs(a[0]-b[0])<1e-3 else 'D') for a,b in L)
    print('beam z',z,len(L),dirs,'x',xs[:12],'y',ys[:3],ys[-3:])
