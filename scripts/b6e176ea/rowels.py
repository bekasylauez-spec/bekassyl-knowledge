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
ys=sorted(set(round(c[1],3) for c in co.values()))
print('ys',ys, 'nel',len(els))
for yv in (min(ys),max(ys)):
    sel=[e for e,(ft,st,ns) in els.items() if all(abs(co[n][1]-yv)<1e-3 for n in ns) and len(ns)==2]
    print(yv,len(sel),sel)
    print('  st',sorted(set(els[e][1] for e in sel)))
for yv in (0.0,1.5):
    sel=[e for e,(ft,st,ns) in els.items() if all(abs(co[n][1]-yv)<1e-3 for n in ns) and len(ns)==2]
    print(yv,len(sel),' '.join(map(str,sel)))
    print('  st',[(e,els[e][1]) for e in sel])
