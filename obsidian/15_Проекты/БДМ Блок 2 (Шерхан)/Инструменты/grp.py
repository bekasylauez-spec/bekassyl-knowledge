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
import collections as _c
bars=json.load(open('bars.json'))
SEC={'20':'25x60','22':'50x70','23':'35x70','24':'50x90','25':'50x90','26':'50x90','28':'60x120','44':'50x70','45':'60x70'}
geo=_c.defaultdict(list)
for k_,s_ in SEC.items():
    for i,a,b in bars[k_]:
        z_=round(a[2],3)
        if k_=='44' and z_!=7.0: continue
        if abs(a[1]-b[1])<1e-3: key='|'.join(map(str,[z_,'X',round(a[1],3),s_])); r_=sorted([a[0],b[0]])
        else: key='|'.join(map(str,[z_,'Y',round(a[0],3),s_])); r_=sorted([a[1],b[1]])
        geo[key].append(r_)
runs=[]
for key,segs in geo.items():
    segs.sort(); rr=[]
    for a,b in segs:
        if rr and abs(rr[-1][1]-a)<1e-3: rr[-1][1]=b
        else: rr.append([a,b])
    p0=sorted(asl.get(key,[]))
    for a,b in rr:
        p=[q for q in p0 if a-1e-3<=q[0]<=b+1e-3]
        if not p: p=[(a,0,0,0),(b,0,0,0)]
        p=[(a,0,0,0)]+p+[(b,0,0,0)]
        runs.append((key,p))
for k,p in runs:
    z,d,c,s=k.split('|'); z=float(z); c=float(c)
    x0,x1=p[0][0],p[-1][0]
    if d=='X': sp=sorted({x for (x,y,zz) in sup if abs(y-c)<1e-3 and abs(zz-z)<1e-3 and x0-1e-3<=x<=x1+1e-3})
    else: sp=sorted({y for (x,y,zz) in sup if abs(x-c)<1e-3 and abs(zz-z)<1e-3 and x0-1e-3<=y<=x1+1e-3})
    if d=='X': wl=any(abs(y-c)<1e-3 and abs(zz-z)<1e-3 for (x,y,zz) in wallp)
    else: wl=any(abs(x-c)<1e-3 and abs(zz-z)<1e-3 for (x,y,zz) in wallp)
    bot=max(q[1] for q in p); top=max(q[2] for q in p); sw=max(q[3] for q in p)
    rows.append(dict(pts=p,z=z,d=d,c=c,s=s,x0=x0,x1=x1,L=round(x1-x0,3),sup=sp,wall=wl,bot=bot,top=top,asw=sw))
rows.sort(key=lambda r:(r['z'],r['s'],r['d'],r['c']))
for r in []: print(r['z'],r['d'],r['c'],r['s'],'%.2f..%.2f L%.2f'%(r['x0'],r['x1'],r['L']),'sup',len(r['sup']),[round(v-r['x0'],2) for v in r['sup']][:14],'wall' if r['wall'] else '','b%.1f t%.1f w%.1f'%(r['bot'],r['top'],r['asw']))
json.dump(rows,open('rows.json','w'))
