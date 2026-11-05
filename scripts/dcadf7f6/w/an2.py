import pickle,collections
m=pickle.load(open('geo.pkl','rb'));N=m['nodes']
H=collections.Counter();V=collections.defaultdict(list)
hz=collections.defaultdict(list)
for ns in m['plates']:
    P=[N[i-1] for i in ns]
    r=[max(p[j] for p in P)-min(p[j] for p in P) for j in range(3)]
    if r[2]<1e-4: hz[round(P[0][2],3)].append(P)
    elif r[0]<1e-4: V[('X',round(P[0][0],3))].append(P)
    elif r[1]<1e-4: V[('Y',round(P[0][1],3))].append(P)
    else: H['other']+=1
for z,L in sorted(hz.items()):
    xs=[p[0] for P in L for p in P];ys=[p[1] for P in L for p in P]
    print('H z=%s n=%d x %.2f..%.2f y %.2f..%.2f'%(z,len(L),min(xs),max(xs),min(ys),max(ys)))
for k,L in sorted(V.items()):
    a=0 if k[0]=='Y' else 1
    s=[p[a] for P in L for p in P];zz=[p[2] for P in L for p in P]
    print('W %s=%s n=%d along %.2f..%.2f z %.2f..%.2f'%(k[0],k[1],len(L),min(s),max(s),min(zz),max(zz)))
print(H)
# bars
B=collections.Counter()
for ns in m['bars']:
    a,b=N[ns[0]-1],N[ns[1]-1]
    d=tuple(round(b[j]-a[j],2) for j in range(3))
    B['vert' if abs(d[0])<1e-3 and abs(d[1])<1e-3 else 'hor']+=1
print(B)
