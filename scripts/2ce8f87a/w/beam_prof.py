import json,collections
out=json.load(open('beam_el.json'))
def tot(v): return v[0]+v[1]+v[4], v[2]+v[3]+v[5], max(v[9],v[10])   # bottom, top, asw
lines=collections.defaultdict(list)
for o in out:
    (x0,y0,z),(x1,y1,_)=o['p']
    k=('X',round(z,2),round(y0)) if abs(y1-y0)<1 else ('Y',round(z,2),round(x0))
    a,b=(x0,x1) if k[0]=='X' else (y0,y1)
    if a>b: a,b=b,a
    secs=[v for s,t,v in o['secs'] if t!='*'] or [v for s,t,v in o['secs']]
    bt=max(tot(v)[0] for v in secs); tp=max(tot(v)[1] for v in secs); sw=max(tot(v)[2] for v in secs)
    lines[k].append((a,b,bt,tp,sw))
for k in sorted(lines,key=str):
    L=sorted(lines[k]); print(k)
    # merge consecutive into 1 m bins
    for a,b,bt,tp,sw in L:
        print('   %7.0f..%7.0f  bot %5.2f top %5.2f asw %5.1f'%(a,b,bt,tp,sw))
