import re,sys
t=open(sys.argv[1],encoding='utf-8-sig',errors='replace').read()
def doc(n):
    m=re.search(r'\(\s*%d/(.*?)\)'%n,t,re.S); return m.group(1)
els={}
for i,r in enumerate(doc(1).split('/'),1):
    p=r.split()
    if len(p)>=3: els[i]=(int(p[0]),int(p[1]),[int(x) for x in p[2:]])
co={}
for i,r in enumerate(doc(4).split('/'),1):
    p=r.split()
    if len(p)>=3: co[i]=tuple(map(float,p[:3]))
for e in map(int,sys.argv[2:]):
    print(e,els[e],[co[n] for n in els[e][2]])
