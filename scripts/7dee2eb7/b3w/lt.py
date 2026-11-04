import re, collections, json
t=open(r'C:/Users/Public/Documents/LIRA SAPR/LIRA SAPR 2024/Data/бдм блок 3-кор.txt','rb').read().decode('cp1251',errors='replace')
def doc(n):
    m=re.search(r'\(\s*%d/'%n,t); s=m.end(); e=t.index(')',s); return t[s:e]
nodes=[tuple(map(float,r.split())) for r in doc(4).split('/') if r.strip()]
els=[]
for r in doc(1).split('/'):
    a=r.split()
    if a: els.append((int(a[0]),int(a[1]),[int(v) for v in a[2:]]))
print(len(nodes),len(els))
print(collections.Counter(e[0] for e in els))
# plates: type 41/42/44 shells
pl=[(i+1,e) for i,e in enumerate(els) if e[0] in (41,42,44,141,142,144)]
zc=collections.Counter()
for i,e in pl:
    zs=[nodes[n-1][2] for n in e[2]]
    if max(zs)-min(zs)<1e-3: zc[(round(zs[0],3),e[1])]+=1
    else: zc[('v',e[1])]+=1
for k,v in sorted(zc.items(),key=str): print(k,v)
json.dump({'nodes':nodes,'els':els},open('lmodel.json','w'))
