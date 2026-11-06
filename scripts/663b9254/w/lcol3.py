import re,collections,json
t=open(r'C:/Users/Public/Documents/LIRA SAPR/LIRA SAPR 2024/Data/бдм блок 3 униф.txt',encoding='cp1251',errors='replace').read()
d=lambda n:[r.split() for r in re.search(r'\(\s*%d/(.*?)\)'%n,t,re.S).group(1).split('/') if r.strip()]
X=[list(map(float,r[:3])) for r in d(4)]; E=[list(map(int,r)) for r in d(1)]
S={}
for w in d(3):
    if w[0]!='0': S[int(w[0])]=w[1:]
OX=121.5-0.65
key=lambda p:(round((p[0]-OX)*1000),round(p[1]*1000))
colk=set(); 
C=json.load(open('lcols.json',encoding='utf-8'))
for k,v in C.items():
    if any(s[3].startswith('S0') and s[1]>0 for s in v): colk.add(tuple(map(int,k.split(','))))
att=collections.defaultdict(set)
plates=collections.Counter()
for i,e in enumerate(E,1):
    nd=e[2:]
    if len(nd)==2:
        a,b=X[nd[0]-1],X[nd[1]-1]
        if abs(a[2]-b[2])<1e-3:
            st=S.get(e[1],['?'])
            if st[0]!='S0': continue
            for p in (a,b):
                k=key(p)
                if k in colk: att[k].add((round(p[2],3),st[2]+'x'+st[3]))
    elif len(nd)>=3:
        for n in nd:
            p=X[n-1]; k=key(p)
            if k in colk: plates[(k,round(p[2],2))]+=1
res={}
for k in sorted(colk):
    lv=collections.defaultdict(set)
    for z,s in att[k]: lv[z].add(s)
    pl=sorted(set(z for (kk,z) in plates if kk==k))
    res['%d,%d'%k]={str(z):sorted(v) for z,v in sorted(lv.items())}
    print(k, dict(sorted((z,sorted(v)) for z,v in lv.items())), 'plates@',pl)
json.dump(res,open('colbeams.json','w'))
