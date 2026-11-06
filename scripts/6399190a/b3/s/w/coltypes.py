import json,math,collections
cols=json.load(open(r'%s/cols.json'%r'C:/Users/Admin/AppData/Local/Temp/claude/210ab68cad67e8c1/6399190a-f172-4888-a7c9-e3d967ee3eb0/scratchpad/b3/s'))
# scheme columns (axis coords) -> lira (x-1.2, y-1.35)
AX={55050:'9',64150:'10',73650:'11',79650:'12',86250:'13'}; AY={0:'А',7000:'Б',10500:'В',16500:'Д',22000:'Ж',29000:'К'}
sch=[(54849,400,900,1300),(64150,400,900,1300),(73650,400,900,1300),(79650,400,900,1300),(86450,400,900,1300),
(54850,28625,900,1300),(64150,28625,900,1300),(73650,28625,900,1300),(79650,28625,900,1300),(86450,28625,900,1300)]
for y in (7000,16500,22000):
    for x in (54750,64150,73650,79650,86550): sch.append((x,y,700,700))
sch.append((86550,10500,700,700))
by=collections.defaultdict(list)
for g,l in cols.items():
    for c in l: by[(round(c['a'][0],2),round(c['a'][1],2))].append(dict(c,g=g))
A28=math.pi*2.8**2/4
used=set()
rows=[]
for (sx,sy,w,h) in sch:
    best=min(by,key=lambda k:(k[0]+1.2-sx/1000)**2+(k[1]+1.35-sy/1000)**2)
    d=math.hypot(best[0]+1.2-sx/1000,best[1]+1.35-sy/1000); used.add(best)
    es=[e for e in by[best] if e['b'][2]>0 and e['a'][2]>=-0.06]
    zs=sorted({e['a'][2] for e in es}|{e['b'][2] for e in es})
    asum=max(e['asum'] for e in es); asw=max(e['asw'] for e in es)
    ax=min(AX,key=lambda a:abs(a-sx)); ay=min(AY,key=lambda a:abs(a-sy))
    rows.append(dict(ax=AX[ax],ay=AY[ay],sx=sx,sy=sy,w=w,h=h,lira=best,d=round(d,3),zs=zs,asum=asum,asw=asw,n=math.ceil(asum/A28),sec=[e['g'] for e in es]))
    print(AY[ay]+'/'+AX[ax],w,h,best,round(d,2),zs,asum,'n28=%.1f'%(asum/A28),'asw',asw,[ (e['a'][2],e['b'][2],e['asum'],e['asw']) for e in es])
print('LIRA not in scheme:',[k for k in by if k not in used])
json.dump(rows,open(r'C:/Users/Admin/AppData/Local/Temp/claude/210ab68cad67e8c1/6399190a-f172-4888-a7c9-e3d967ee3eb0/scratchpad/b3/s/rows.json','w'),ensure_ascii=False,default=list)
