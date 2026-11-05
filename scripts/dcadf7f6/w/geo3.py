import pickle,collections
el,N=pickle.load(open('txtgeo.pkl','rb'))
P=lambda i:N[i-1]
def lines(st):
    segs=[]
    for t,s,ns in el:
        if s==st and t==10:
            a,b=P(ns[0]),P(ns[1]); segs.append((a,b))
    # merge collinear by line key
    G=collections.defaultdict(list)
    for a,b in segs:
        if abs(a[0]-b[0])<1e-3 and abs(a[1]-b[1])<1e-3: G[('V',round(a[0],2),round(a[1],2))].append((min(a[2],b[2]),max(a[2],b[2])))
        elif abs(a[1]-b[1])<1e-3: G[('X',round(a[1],2),round(a[2],2))].append((min(a[0],b[0]),max(a[0],b[0])))
        elif abs(a[0]-b[0])<1e-3: G[('Y',round(a[0],2),round(a[2],2))].append((min(a[1],b[1]),max(a[1],b[1])))
        else: G[('D',)].append((a,b))
    out=[]
    for k,iv in sorted(G.items(),key=str):
        if k[0]=='D': out.append((k,len(iv)));continue
        iv.sort(); runs=[]; s,e=iv[0]
        for a,b in iv[1:]:
            if a<=e+1e-3: e=max(e,b)
            else: runs.append((round(s,2),round(e,2))); s,e=a,b
        runs.append((round(s,2),round(e,2)))
        out.append((k,runs))
    return out
for st,nm in ((1,'Рандбалка 30x60'),(5,'10x10'),(6,'Колонна 50x50'),(8,'40x40'),(11,'30x65'),(12,'35x70')):
    print('==',st,nm)
    for r in lines(st): print('  ',r)
