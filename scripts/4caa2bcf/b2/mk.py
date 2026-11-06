import json, collections
rows=[r for r in json.load(open('rows.json')) if r['z']>-1]
# beam-on-beam supports: intersections with perpendicular beams of same level that have larger h
def hh(s): return int(s.split('x')[1])
for r in rows:
    if r['sup']: continue
    pts=set()
    for q in rows:
        if q['z']!=r['z'] or q['d']==r['d'] or q is r: continue
        if q['x0']-1e-3<=r['c']<=q['x1']+1e-3 and r['x0']-1e-3<=q['c']<=r['x1']+1e-3 and hh(q['s'])>=hh(r['s']):
            pts.add(round(q['c'],3))
    r['sup']=sorted(pts); r['onbeam']=True
G=collections.OrderedDict()
for r in sorted(rows,key=lambda r:(-r['z'],-hh(r['s']),r['d'],r['c'])):
    key=(r['z'],r['s'],r['d'],round(r['L'],2),tuple(round(v-r['x0'],2) for v in r['sup']))
    G.setdefault(key,[]).append(r)
lev={-0.05:'-0.050',4.5:'+4.500',7.0:'+7.000'}
out=[];n=0
for key,rs in sorted(G.items(),key=lambda kv:(-kv[0][0] if False else ({-0.05:0,4.5:1,7.0:2}[kv[0][0]]),-hh(kv[0][1]),kv[0][2],-kv[0][3])):
    n+=1
    m='Рм-%d'%n
    z,s,d,L,sp=key
    axes=[r['c'] for r in rs]
    b=max(r['bot'] for r in rs); t=max(r['top'] for r in rs); w=max(r['asw'] for r in rs)
    out.append(dict(mark=m,pts=[sorted([(round(q[0]-r['x0'],3),)+tuple(q[1:]) for q in r['pts']]) for r in rs],x0s=[r['x0'] for r in rs],z=z,s=s,d=d,L=L,n=len(rs),lines=axes,sup=list(sp),bot=b,top=t,asw=w,onbeam=any(r.get('onbeam') for r in rs)))
    print(m,lev[z],s,d,'L=%.2f'%L,'x%d'%len(rs),'x0',[r['x0'] for r in rs],'lines',axes,'spans',len(sp)-1 if sp else 0,'beam' if out[-1]['onbeam'] else 'col','низ %.1f верх %.1f Asw %.1f'%(b,t,w))
json.dump(out,open('marks.json','w'),ensure_ascii=False)
