import json,collections
L=json.load(open('lines.json')); E=json.load(open('beam_el.json'))
R=json.load(open('../an/rects.json'))
LVK={-0.05:'1',4.5:'2',7.0:'3'}
# LIRA elements by (d,z) -> list
idx=collections.defaultdict(list)
for o in E:
    (x0,y0,z),(x1,y1,_)=o['a'],o['b']
    if abs(y1-y0)<1: idx[('X',round(z,3))].append((y0,min(x0,x1),max(x0,x1),o))
    elif abs(x1-x0)<1: idx[('Y',round(z,3))].append((x0,min(y0,y1),max(y0,y1),o))
out=[]
for ln in L:
    a,b=ln['segs'][0][0],ln['segs'][-1][1]
    cand=[t for t in idx[(ln['d'],round(ln['z'],3))] if t[2]>a-200 and t[1]<b+200 and abs(t[0]-ln['c'])<800]
    cs=collections.Counter(round(t[0]) for t in cand)
    if not cs: print('NO LIRA',ln['z'],ln['d'],ln['c'],a,b); ln['lira']=None; out.append(ln); continue
    lc=min(cs,key=lambda c:abs(c-ln['c']))
    els=sorted([t for t in cand if round(t[0])==lc],key=lambda t:t[1])
    ln['lira_c']=lc
    ln['prof']=[(t[1],t[2],t[3]['bot'],t[3]['top'],t[3]['sw'],t[3]['bh']) for t in els]
    bh=collections.Counter(tuple(t[3]['bh']) for t in els)
    ln['bh']=bh.most_common(1)[0][0]; ln['bhs']={str(k):v for k,v in bh.items()}
    out.append(ln)
    print(ln['z'],ln['d'],ln['c'],'lira',lc,'%d..%d'%(a,b),dict(bh),'bot %.1f top %.1f sw %.1f'%(max(p[2] for p in ln['prof']),max(p[3] for p in ln['prof']),max(p[4] for p in ln['prof'])))
json.dump(out,open('lines2.json','w'))
