import csv,pickle,collections,json
els,nodes,st=pickle.load(open('lm.pkl','rb'))
BEAMST={26:(25,60),27:(35,70),28:(50,70),29:(60,70),30:(50,90),31:(50,90),32:(60,120)}
R=collections.defaultdict(list)
for r in csv.reader(open('tbl01.31_1.csv',encoding='cp1251',errors='replace'),delimiter=';'):
    if len(r)<22 or not r[4].strip().isdigit(): continue
    try: v=[float(x) for x in r[10:21]]
    except: continue
    R[int(r[4])].append((int(r[5]),r[6].strip(),v))
out=[]
for e,rows in R.items():
    ty,s,nn=els[e-1]
    if ty!=10 or s not in BEAMST: continue
    a,b=nodes[nn[0]-1],nodes[nn[1]-1]
    if abs(a[2]-b[2])>1e-3: continue
    ok=[v for sc,t,v in rows if t!='*'] or [v for sc,t,v in rows]
    bot=max(v[0]+v[1]+v[4] for v in ok); top=max(v[2]+v[3]+v[5] for v in ok); sw=max(max(v[9],v[10]) for v in ok)
    out.append(dict(e=e,s=s,bh=BEAMST[s],a=[a[0]*1000,a[1]*1000,a[2]],b=[b[0]*1000,b[1]*1000,b[2]],bot=bot,top=top,sw=sw))
json.dump(out,open('beam_el.json','w'))
print(len(out))
lines=collections.defaultdict(list)
for o in out:
    (x0,y0,z),(x1,y1,_)=o['a'],o['b']
    if abs(y1-y0)<1: k=('X',round(z,3),round(y0)); u=(x0,x1)
    elif abs(x1-x0)<1: k=('Y',round(z,3),round(x0)); u=(y0,y1)
    else: k=('?',round(z,3)); u=(0,0)
    lines[k].append((min(u),max(u),o['bh'],o['bot'],o['top'],o['sw']))
for k in sorted(lines,key=str):
    L=sorted(lines[k]); bh=collections.Counter(l[2] for l in L)
    print(k,len(L),'%.0f..%.0f'%(L[0][0],L[-1][1]),dict(bh),'bot %.1f top %.1f asw %.1f'%(max(l[3] for l in L),max(l[4] for l in L),max(l[5] for l in L)))
