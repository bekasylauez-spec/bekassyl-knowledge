import csv,pickle,collections,json,re
els,nodes,stf=pickle.load(open('m4.pkl','rb'))
L=pickle.load(open('blines.pkl','rb'))
raw=open('as_bar.csv','rb').read().decode('utf-8',errors='replace')
R=collections.defaultdict(list); groups={}
for r in csv.reader(raw.splitlines(),delimiter=';'):
    if len(r)>2 and r[1].endswith('-S'): groups[r[1][:-2]]=r[2][:120]
    if len(r)<20 or not r[4].strip().isdigit(): continue
    try: v=[float(x) for x in r[10:21]]
    except: continue
    R[int(r[4])].append((int(r[5]),r[6].strip('﻿'),v))
print(len(R),'elements with As')
out={}
for k,segs in L.items():
    pts=[]
    for a,b,e in segs:
        rows=R.get(e)
        if not rows: continue
        ns=max(s for s,_,_ in rows)
        ok=[x for x in rows if x[1]!='*'] or rows
        for s,t,v in ok:
            # element direction: node order
            n1,n2=[nodes[i-1] for i in els[e-1][2]]
            c1=(n1[0]-174.15)*1000 if k[0]=='X' else n1[1]*1000
            c2=(n2[0]-174.15)*1000 if k[0]=='X' else n2[1]*1000
            pos=c1+(c2-c1)*(s-1)/max(ns-1,1)
            bot=v[0]+v[1]+v[4]; top=v[2]+v[3]+v[5]; asw=max(v[9],v[10])
            pts.append((round(pos),round(bot,2),round(top,2),round(asw,2)))
    out[str(k)]=sorted(pts)
json.dump(out,open('as_lines.json','w'),ensure_ascii=False)
for k,p in out.items():
    if not p: print(k,'NO DATA'); continue
    print(k,len(p),'bot max',max(x[1] for x in p),'top max',max(x[2] for x in p),'asw max',max(x[3] for x in p))
