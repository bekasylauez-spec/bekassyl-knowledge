import re,sys,collections,json
t=open(sys.argv[1],encoding='utf-8-sig').read()
docs={}
for m in re.finditer(r'\(\s*(\d+)/(.*?)\n\)',t,re.S): docs[int(m.group(1))]=m.group(2)
els=[]
for rec in docs[1].replace('\n',' ').split('/'):
    v=rec.split()
    if len(v)>=3: els.append([int(x) for x in v])
nodes=[]
for rec in docs[4].replace('\n',' ').split('/'):
    v=rec.split()
    if len(v)>=3: nodes.append([float(x) for x in v[:3]])
print(len(els),len(nodes))
c=collections.Counter((e[0],e[1]) for e in els); print(sorted(c.items()))
out=[]
for i,e in enumerate(els):
    if e[1]==10:
        a,b=nodes[e[2]-1],nodes[e[3]-1]; out.append((i+1,a,b))
json.dump({'els':els,'nodes':nodes},open(sys.argv[2],'w'))
xs=collections.Counter()
for i,a,b in out:
    print(i,a,b)
