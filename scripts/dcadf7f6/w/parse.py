import re,collections,pickle
s=open('aero_u.txt',encoding='utf-8-sig').read()
def doc(n):
    m=re.search(r'\(\s*%d/(.*?)\)'%n,s,re.S); return m.group(1)
d1=doc(1); d4=doc(4)
recs=[r.split() for r in d1.split('/') if r.strip()]
el=[(int(r[0]),int(r[1]),[int(x) for x in r[2:]]) for r in recs]
nums=[float(x) for x in d4.replace('/',' ').split()]
N=[tuple(nums[i:i+3]) for i in range(0,len(nums),3)]
print(len(el),len(N))
stf={1:'Рандбалка 30x60',2:'Плита? 600',3:'Столбч1 300',4:'Столбч2 700',5:'bar 10x10',6:'Колонна 50x50',7:'Стена 400',8:'bar 40x40',9:'пл 150',10:'Плита 200',11:'bar 30x65',12:'bar 35x70'}
G=collections.defaultdict(list)
for t,st,ns in el: G[(st,t)].append(ns)
for (st,t),L in sorted(G.items()):
    P=[N[i-1] for ns in L for i in ns]
    xs=[p[0] for p in P];ys=[p[1] for p in P];zs=[p[2] for p in P]
    print(st,stf.get(st),'KE',t,len(L),'x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f'%(min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)))
pickle.dump((el,N),open('txtgeo.pkl','wb'))
