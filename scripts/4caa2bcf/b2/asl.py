import json, collections, csv
bars=json.load(open('bars.json'))
SEC={'20':'25x60','22':'50x70','23':'35x70','24':'50x90','25':'50x90','26':'50x90','27':'60x100','28':'60x120','44':'50x70','45':'60x70'}
A={}
f=lambda v: float(v) if v not in ('',None) else 0.0
for r in csv.reader(open('asbar.csv',encoding='utf-8',errors='replace'),delimiter=';'):
    if len(r)<22 or not r[4].isdigit(): continue
    e=int(r[4]); s=int(r[5]); bot=f(r[10])+f(r[11])+f(r[14]); top=f(r[12])+f(r[13])+f(r[15]); sw=max(f(r[19]),f(r[20]))
    o=A.setdefault(e,{})
    p=o.get(s,(0,0,0)); o[s]=(max(p[0],bot),max(p[1],top),max(p[2],sw))
lines=collections.defaultdict(list)
for k,s in SEC.items():
    for i,a,b in bars[k]:
        z=round(a[2],3)
        if k=='44' and z!=7.0: continue
        if abs(a[1]-b[1])<1e-3: key=(z,'X',round(a[1],3),s); r=(a[0],b[0])
        else: key=(z,'Y',round(a[0],3),s); r=(a[1],b[1])
        o=A.get(i,{})
        if not o: continue
        secs=sorted(o)
        # section 1 at start node a, last at b
        xa,xb=r
        for j,sn in enumerate(secs):
            x=xa+(xb-xa)*j/max(1,len(secs)-1)
            lines[key].append((round(x,3),)+o[sn])
out={}
for key in sorted(lines):
    p=sorted(lines[key]); 
    print(key, 'x %.2f..%.2f'%(p[0][0],p[-1][0]), 'bot %.2f top %.2f asw %.2f'%(max(q[1] for q in p),max(q[2] for q in p),max(q[3] for q in p)))
    out['|'.join(map(str,key))]=p
json.dump(out,open('aslines.json','w'))
print(len(A))
