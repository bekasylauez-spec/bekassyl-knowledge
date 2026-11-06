import re,collections,pickle
t=open('m2.txt',encoding='utf-8').read()
docs={}
for m in re.finditer(r'\(\s*(\d+)/(.*?)\)',t,re.S): docs.setdefault(int(m.group(1)),m.group(2))
recs=lambda s:[r.strip() for r in s.split('/') if r.strip()]
els=[]
for r in recs(docs[1]):
    v=r.split(); els.append((int(v[0]),int(v[1]),[int(x) for x in v[2:]]))
nodes=[]
for r in recs(docs[4]):
    v=r.split(); nodes.append(tuple(float(x) for x in v[:3]))
# stiffness descriptions
stf={}
cur=None
for r in recs(docs[3]):
    v=r.split()
    if v[0]!='0': cur=int(v[0]); stf[cur]=r
    else: stf[cur]+=' | '+r
pickle.dump((els,nodes,stf),open('m2.pkl','wb'))
c=collections.Counter((e[0],e[1]) for e in els)
for (ty,s),n in sorted(c.items()):
    if ty in (10,5,1,2,3,4,6,7): 
        zs=collections.Counter(round(nodes[e[2][0]-1][2],2) for e in els if e[0]==ty and e[1]==s and len(e[2])==2)
        print(ty,s,n,stf.get(s,'')[:90],dict(zs.most_common(6)))
