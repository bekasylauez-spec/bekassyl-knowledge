import csv,pickle,collections,json
import model as M
els,nodes=pickle.load(open('m6.pkl','rb'))
R=collections.defaultdict(list)
for r in csv.reader(open('as_bar.csv',encoding='utf-8',errors='replace'),delimiter=';'):
    if len(r)<20 or not r[4].strip().isdigit(): continue
    g=int(r[2])
    if g in (5,6,17,18): continue
    try: v=[float(x) for x in r[10:22]]
    except: continue
    R[int(r[4])].append((int(r[5]),r[6].strip('\ufeff'),v))
out=[]
for e,rows in R.items():
    ns=[nodes[int(k)-1] for k in els[e-1][2:4]]
    p=[(n[0]*1000,M.fy(n[1]),n[2]) for n in ns]
    ok=[v for s,t,v in rows if t!='*'] or [v for s,t,v in rows]
    mx=[max(v[i] for v in ok) for i in range(12)]
    out.append(dict(e=e,p=p,v=mx,secs=[(s,t,v) for s,t,v in rows]))
json.dump(out,open('beam_el.json','w'),ensure_ascii=False)
zs=collections.Counter(round(o['p'][0][2],2) for o in out); print(zs)
lines=collections.defaultdict(list)
for o in out:
    (x0,y0,z),(x1,y1,_)=o['p']
    if abs(y1-y0)<1: lines[('X',round(z,2),round(y0))].append(o)
    elif abs(x1-x0)<1: lines[('Y',round(z,2),round(x0))].append(o)
    else: lines[('?',round(z,2))].append(o)
for k in sorted(lines,key=str):
    L=lines[k]; xs=[c for o in L for q in o['p'] for c in ((q[0],) if k[0]=='X' else (q[1],))]
    print(k,len(L),'range',round(min(xs)),round(max(xs)),'max',[round(max(o['v'][i] for o in L),2) for i in range(12)])
