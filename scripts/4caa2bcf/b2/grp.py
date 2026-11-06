import re, json, collections
t=open('lira.txt',encoding='utf-8').read()
docs={}
for m in re.finditer(r'\(\s*(\d+)/(.*?)\)', t, re.S): docs.setdefault(int(m.group(1)), m.group(2))
nodes=[tuple(map(float,s.split()[:3])) for s in docs[4].split('/') if s.strip()]
els=[]
for s in docs[1].split('/'):
    v=s.split()
    if len(v)>=4: els.append((int(v[0]),int(v[1]),[int(x) for x in v[2:]]))
# vertical bars (columns) top/bottom nodes -> support points (x,y,z)
sup=set(); wallp=set()
for ft,sti,nn in els:
    if len(nn)==2:
        a=nodes[nn[0]-1]; b=nodes[nn[1]-1]
        if abs(a[0]-b[0])<1e-3 and abs(a[1]-b[1])<1e-3 and abs(a[2]-b[2])>0.1:
            for p in (a,b): sup.add((round(p[0],3),round(p[1],3),round(p[2],3)))
    elif len(nn)==4 and ft in (41,42,44,21,27):
        ps=[nodes[i-1] for i in nn]
        if max(p[2] for p in ps)-min(p[2] for p in ps)>0.1:
            for p in ps: wallp.add((round(p[0],3),round(p[1],3),round(p[2],3)))
asl=json.load(open('aslines.json'))
rows=[]
for k,p in asl.items():
    z,d,c,s=k.split('|'); z=float(z); c=float(c)
    x0,x1=p[0][0],p[-1][0]
    if d=='X': sp=sorted({x for (x,y,zz) in sup if abs(y-c)<1e-3 and abs(zz-z)<1e-3 and x0-1e-3<=x<=x1+1e-3})
    else: sp=sorted({y for (x,y,zz) in sup if abs(x-c)<1e-3 and abs(zz-z)<1e-3 and x0-1e-3<=y<=x1+1e-3})
    if d=='X': wl=any(abs(y-c)<1e-3 and abs(zz-z)<1e-3 for (x,y,zz) in wallp)
    else: wl=any(abs(x-c)<1e-3 and abs(zz-z)<1e-3 for (x,y,zz) in wallp)
    bot=max(q[1] for q in p); top=max(q[2] for q in p); sw=max(q[3] for q in p)
    rows.append(dict(z=z,d=d,c=c,s=s,x0=x0,x1=x1,L=round(x1-x0,3),sup=sp,wall=wl,bot=bot,top=top,asw=sw))
rows.sort(key=lambda r:(r['z'],r['s'],r['d'],r['c']))
for r in rows: print(r['z'],r['d'],r['c'],r['s'],'%.2f..%.2f L%.2f'%(r['x0'],r['x1'],r['L']),'sup',len(r['sup']),[round(v-r['x0'],2) for v in r['sup']][:14],'wall' if r['wall'] else '','b%.1f t%.1f w%.1f'%(r['bot'],r['top'],r['asw']))
json.dump(rows,open('rows.json','w'))
