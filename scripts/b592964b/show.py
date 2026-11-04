import json,sys
sys.stdout.reconfigure(encoding='utf-8')
d=json.load(open(sys.argv[1])); el,nd=d['el'],d['nd']
zlo,zhi=float(sys.argv[2]),float(sys.argv[3]); stf=sys.argv[4].split(',')
f=lambda n:'(%g,%g,%g)'%tuple(nd[n-1])
for i,r in enumerate(el,1):
    if r[1] not in stf: continue
    ns=list(map(int,r[2:]))
    zz=[nd[n-1][2] for n in ns]
    if min(zz)>=zlo and max(zz)<=zhi: print(i,r[0],r[1],' '.join(f(n) for n in ns), ns)
