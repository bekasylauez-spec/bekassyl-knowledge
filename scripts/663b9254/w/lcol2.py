import json,collections
C=json.load(open('lcols.json',encoding='utf-8'))
out=[]
for k,v in C.items():
    rc=[s for s in v if s[3].startswith('S0')]
    if not rc: continue
    z0=min(s[0] for s in rc); z1=max(s[1] for s in rc); sec=sorted(set(s[3].split()[2]+'x'+s[3].split()[3] for s in rc))
    zs=sorted(set([round(s[0],3) for s in rc]+[round(s[1],3) for s in rc]))
    above=[s for s in v if not s[3].startswith('S') and s[0]>=z1-1e-3]
    x,y=map(int,k.split(','))
    out.append((sec[0],z0,z1,x,y,len(above)>0,zs))
out.sort()
for o in out: print(o[0],o[1],o[2],o[3],o[4],'steel_above' if o[5] else '', o[6])
print(len(out)); print(collections.Counter((o[0],o[1],o[2]) for o in out))
