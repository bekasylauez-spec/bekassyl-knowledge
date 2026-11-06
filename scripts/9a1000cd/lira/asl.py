import csv,pickle,collections,json
els,nodes,stf=pickle.load(open('m2.pkl','rb'))
L=pickle.load(open('blines.pkl','rb'))
raw=open('as_bar.csv','rb').read().decode('utf-8',errors='replace').replace('﻿','')
R=collections.defaultdict(list); msgs=collections.Counter(); grp={}
for r in csv.reader(raw.splitlines(),delimiter=';'):
    if len(r)>2 and r[1].endswith('-S'): grp[r[1][:-2]]=r[2][:110]
    if len(r)<21 or not r[4].strip().isdigit(): continue
    try: v=[float(x or 0) for x in r[10:21]]
    except: continue
    if r[9].strip(): msgs[(r[9].strip()[:60])]+=1
    R[int(r[4])].append((int(r[5]),r[6].strip(),v,r[9].strip()))
print(len(R),'elements with As'); print(msgs.most_common(8))
for k,v in grp.items(): print('grp',k,v)
out={}; bad=collections.defaultdict(list)
for k,segs in L.items():
    if k[0]=='?': continue
    pts=[]
    for a,b,e in segs:
        rows=R.get(e)
        if not rows: continue
        ns=max(s for s,_,_,_ in rows)
        ok=[x for x in rows if x[1]!='*'] or rows
        n1,n2=[nodes[i-1] for i in els[e-1][2]]
        c1=n1[0] if k[0]=='X' else n1[1]; c2=n2[0] if k[0]=='X' else n2[1]
        for s,t,v,msg in ok:
            pos=c1+(c2-c1)*(s-1)/max(ns-1,1)
            pts.append((round(pos,3),round(v[0]+v[1]+v[4],2),round(v[2]+v[3]+v[5],2),round(max(v[9],v[10]),2)))
            if msg: bad[str(k)].append((round(pos,2),msg[:50]))
    out[str(k)]=sorted(pts)
json.dump(out,open('as_lines.json','w'),ensure_ascii=False)
for k,p in sorted(out.items()):
    if not p: print(k,'NO DATA'); continue
    print(k,len(p),'низ %.1f верх %.1f asw %.1f'%(max(x[1] for x in p),max(x[2] for x in p),max(x[3] for x in p)), 'MSG %d'%len(bad[k]) if bad[k] else '')
json.dump(bad,open('msgs.json','w'),ensure_ascii=False)
