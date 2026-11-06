import json, collections
rc=json.load(open('rc.json')); geo=json.load(open('schgeo.json'))
LV={4.5:'2.3',7.0:'2.4'}
def parts():
    g=collections.defaultdict(list)
    for o in rc:
        if o['z'] not in LV: continue
        if o['y1']==o['y2']: k=(o['z'],'X',o['y1'],tuple(o['sec'])); a,b=sorted((o['x1'],o['x2']))
        elif o['x1']==o['x2']: k=(o['z'],'Y',o['x1'],tuple(o['sec'])); a,b=sorted((o['y1'],o['y2']))
        else: continue
        g[k].append((a,b,o['el'],o['x1']>o['x2'] if k[1]=='X' else o['y1']>o['y2']))
    out=[]
    for k,iv in g.items():
        iv.sort(); cur=None
        for a,b,el,rev in iv:
            if cur and a<=cur['e']+1: cur['e']=b; cur['els'].append((a,b,el,rev))
            else:
                cur=dict(z=k[0],dir=k[1],c=k[2],sec=k[3],s=a,e=b,els=[(a,b,el,rev)]); out.append(cur)
    return out
def supports(p):
    cols=geo[LV[p['z']]]['cols']; res=[]
    for x0,y0,x1,y1 in cols:
        if p['dir']=='X' and y0<=p['c']<=y1 and x1>=p['s']-700 and x0<=p['e']+700: res.append(('col',x0,x1))
        if p['dir']=='Y' and x0<=p['c']<=x1 and y1>=p['s']-700 and y0<=p['e']+700: res.append(('col',y0,y1))
    # crossing beams of bigger/equal height (supports for secondaries)
    for q in P:
        if q is p or q['z']!=p['z'] or q['dir']==p['dir']: continue
        if q['s']<=p['c']<=q['e'] and p['s']<=q['c']<=p['e'] and q['sec'][1]>=p['sec'][1]:
            if not any(a<=q['c']<=b for _,a,b in res): res.append(('beam',q['c']-q['sec'][0]//2,q['c']+q['sec'][0]//2))
    return sorted(set(res),key=lambda r:r[1])
P=parts()
for p in P: p['sup']=supports(p)
json.dump(P,open('parts.json','w'))
if __name__=='__main__':
    for p in sorted(P,key=lambda p:(p['z'],p['sec'],p['dir'],p['c'],p['s'])):
        print(p['z'],p['dir'],p['c'],p['sec'],p['s'],p['e'],len(p['els']),[(t[0],a,b) for t,a,b in p['sup']])
