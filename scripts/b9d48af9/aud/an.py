import re,collections
DS={};SO=collections.defaultdict(list);FI=[]
for l in open('dump.tsv',encoding='utf-8'):
    p=l.rstrip('\n').split('\t')
    if p[0]=='DS':
        bb=list(map(float,p[5:11])) if len(p)>=11 and p[5] else None
        DS[p[1]]=dict(id=p[1],cat=p[2],key=p[3],name=p[4],bb=bb)
    elif p[0]=='S':
        v=list(map(float,p[2:8]));SO[p[1]].append(dict(bb=v,vol=float(p[8]),t=float(p[9]),n=p[10],rad=float(p[11]),nf=int(p[12]),A=float(p[13])))
    elif p[0]=='FI':
        FI.append(p)
def norm(n): return re.sub(r' -?\d+(\.\d+)?','',n)
def bolts(i):
    r=[]
    for s in SO[i]:
        b=s['bb']; ext=sorted([b[3]-b[0],b[4]-b[1],b[5]-b[2]])
        d=round(s['rad']*2,1)
        if s['nf']<=4 and d in (12,16,20,24,30,42) and ext[2]>25 and abs(ext[0]-d)<5: r.append((d,round(ext[2]),[round((b[k]+b[k+3])/2) for k in range(3)]))
    return r
def plates(i):
    return SO[i]
def near(x0,x1,y0,y1,z0,z1,cats=('Соедин',),show=True):
    out=[]
    for i,d in DS.items():
        if not any(d['cat'].startswith(c) for c in cats): continue
        for s in SO[i]:
            b=s['bb']
            if b[3]>=x0 and b[0]<=x1 and b[4]>=y0 and b[1]<=y1 and b[5]>=z0 and b[2]<=z1:
                out.append((i,d['name'][:60],[round(v) for v in b],s['t'],s['n'],round(s['vol'])))
    out.sort(key=lambda r:(r[1],r[2][2]))
    if show:
        for r in out: print(r)
    return out
