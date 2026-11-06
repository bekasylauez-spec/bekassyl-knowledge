import re,collections,json
t=open(r'C:/Users/Public/Documents/LIRA SAPR/LIRA SAPR 2024/Data/бдм блок 3 униф.txt',encoding='cp1251',errors='replace').read()
d=lambda n:[r.split() for r in re.search(r'\(\s*%d/(.*?)\)'%n,t,re.S).group(1).split('/') if r.strip()]
X=[list(map(float,r[:3])) for r in d(4)]; E=[list(map(int,r)) for r in d(1)]
S={}
for w in d(3):
    if w[0]!='0' and w[1]=='S0': S[int(w[0])]=(int(float(w[3])*10),int(float(w[4])*10))
OX=121.5-0.65  # LIRA x of axis 22
out=[]
for i,e in enumerate(E,1):
    nd=e[2:]
    if e[0]==10 and len(nd)==2 and e[1] in S:
        a,b=X[nd[0]-1],X[nd[1]-1]
        if abs(a[2]-b[2])<1e-3 and a[2]>-0.1:
            out.append(dict(el=i,sec=S[e[1]],z=a[2],x1=round((a[0]-OX)*1000),y1=round(a[1]*1000),x2=round((b[0]-OX)*1000),y2=round(b[1]*1000)))
json.dump(out,open('rc.json','w'))
g=collections.defaultdict(list)
for o in out:
    if o['y1']==o['y2']: g[(o['z'],'X',o['y1'],o['sec'])].append((min(o['x1'],o['x2']),max(o['x1'],o['x2'])))
    elif o['x1']==o['x2']: g[(o['z'],'Y',o['x1'],o['sec'])].append((min(o['y1'],o['y2']),max(o['y1'],o['y2'])))
    else: g[(o['z'],'D',0,o['sec'])].append(0)
def merge(iv):
    iv=sorted(iv); r=[list(iv[0])]
    for a,b in iv[1:]:
        if a<=r[-1][1]+1: r[-1][1]=max(r[-1][1],b)
        else: r.append([a,b])
    return r
for k in sorted(g):
    if k[1]=='D': print(k,len(g[k])); continue
    print(k, merge(g[k]))
