import re,collections,json
t=open(r'C:/Users/Public/Documents/LIRA SAPR/LIRA SAPR 2024/Data/бдм блок 3 униф.txt',encoding='cp1251',errors='replace').read()
d=lambda n:[r.split() for r in re.search(r'\(\s*%d/(.*?)\)'%n,t,re.S).group(1).split('/') if r.strip()]
X=[list(map(float,r[:3])) for r in d(4)]; E=[list(map(int,r)) for r in d(1)]
S={}
for w in d(3):
    if w[0]!='0': S[int(w[0])]=w[1:]
OX=121.5-0.65
cols=collections.defaultdict(list); other=collections.Counter()
for i,e in enumerate(E,1):
    nd=e[2:]
    if len(nd)!=2: continue
    a,b=X[nd[0]-1],X[nd[1]-1]
    if abs(a[0]-b[0])<1e-4 and abs(a[1]-b[1])<1e-4 and abs(a[2]-b[2])>1e-3:
        st=S.get(e[1],['?'])
        cols[(round((a[0]-OX)*1000),round(a[1]*1000))].append((min(a[2],b[2]),max(a[2],b[2]),e[1],' '.join(st[:5]),i,e[0]))
json.dump({'%d,%d'%k:v for k,v in cols.items()},open('lcols.json','w'),ensure_ascii=False)
sig=collections.Counter()
for k in sorted(cols):
    v=sorted(cols[k]); 
    s=(round(v[0][0],3),round(v[-1][1],3),tuple(sorted(set(x[3] for x in v))))
    sig[s]+=1
for s,n in sorted(sig.items(),key=str): print(n,s)
print(len(cols))
