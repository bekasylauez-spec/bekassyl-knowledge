import re,collections,json
t=open(r'C:/Users/Public/Documents/LIRA SAPR/LIRA SAPR 2024/Data/бдм блок 3 униф.txt',encoding='cp1251',errors='replace').read()
d=lambda n:[r.split() for r in re.search(r'\(\s*%d/(.*?)\)'%n,t,re.S).group(1).split('/') if r.strip()]
X=[list(map(float,r[:3])) for r in d(4)]; E=[list(map(int,r)) for r in d(1)]
S={}
for w in d(3):
    if w[0]!='0' and w[1] in('S0',): S[int(w[0])]=(int(float(w[3])*10),int(float(w[4])*10))
OX=121.5-0.65
C=collections.defaultdict(set)
for e in E:
    nd=e[2:]
    if e[0]==10 and len(nd)==2 and e[1] in S:
        a,b=X[nd[0]-1],X[nd[1]-1]
        if abs(a[0]-b[0])<1e-4 and abs(a[1]-b[1])<1e-4 and abs(a[2]-b[2])>1e-3:
            top=max(a[2],b[2]); bot=min(a[2],b[2])
            C[(round((a[0]-OX)*1000),round(a[1]*1000),S[e[1]])].add((round(bot,3),round(top,3)))
out=[]
for (x,y,s),iv in sorted(C.items()):
    zs=sorted(iv); out.append(dict(x=x,y=y,sec=s,z0=zs[0][0],z1=zs[-1][1]))
json.dump(out,open('cols.json','w'))
for o in out: print(o)
