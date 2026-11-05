import pickle,collections
el,N=pickle.load(open('txtgeo.pkl','rb'))
def P(i): return N[i-1]
# walls stiff 7: per plane, list of cells -> find holes on grid
W=collections.defaultdict(list)
for t,st,ns in el:
    if st==7:
        pts=[P(i) for i in ns]
        if max(p[0] for p in pts)-min(p[0] for p in pts)<1e-3: W[('X',round(pts[0][0],2))].append(pts)
        else: W[('Y',round(pts[0][1],2))].append(pts)
for k,L in sorted(W.items()):
    a=1 if k[0]=='X' else 0
    ss=sorted(set(round(p[a],2) for c in L for p in c)); zz=sorted(set(round(p[2],2) for c in L for p in c))
    area=sum((max(p[a] for p in c)-min(p[a] for p in c))*(max(p[2] for p in c)-min(p[2] for p in c))/(1 if len(c)==4 else 2) for c in L)
    full=(ss[-1]-ss[0])*(zz[-1]-zz[0])
    print(k, 'span',ss[0],ss[-1],'z',zz[0],zz[-1],'area %.1f / %.1f'%(area,full))
# slabs
for st in (4,10,9):
    L=[[P(i) for i in ns] for t,st2,ns in el if st2==st and t in (41,44)]
    xs=sorted(set(round(p[0],2) for c in L for p in c)); ys=sorted(set(round(p[1],2) for c in L for p in c))
    area=sum((max(p[0] for p in c)-min(p[0] for p in c))*(max(p[1] for p in c)-min(p[1] for p in c))/(1 if len(c)==4 else 2) for c in L)
    print('slab',st,xs[0],xs[-1],ys[0],ys[-1],'area %.1f / %.1f'%(area,(xs[-1]-xs[0])*(ys[-1]-ys[0])))
    print('  xs',xs);print('  ys',ys)
