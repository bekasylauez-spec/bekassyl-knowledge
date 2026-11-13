import io, json, csv, math, collections
D=r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\mine\\"
out=io.open(D+'a7_out.txt','w',encoding='utf-8')
def P(*a): out.write(' '.join(str(x) for x in a)+'\n')
M=json.load(io.open(r"D:\_claude_work\RMC\lira\model.json",encoding='utf-8'))
F=list(csv.DictReader(io.open(D+'frame.tsv',encoding='utf-8'),delimiter='\t'))
INCL={8:'Пр1',9:'Р1',10:'Р2',11:'Р3',12:'СВ',13:'ГС',15:'Б1',16:'Б2',17:'Б3',18:'К3',19:'К1',20:'К2',21:'КБ1',22:'Б4',23:'Б5',25:'ПБ1'}
rods=[r for r in M['rods'] if r['s'] in INCL]
P('LIRA rods in scope',len(rods), collections.Counter(INCL[r['s']] for r in rods))
def f(x): return float(x)
# model members as 3D segments (mm)
mem=[]
for r in F:
    mk=r['mark']; cls=mk if not (mk.startswith('СВ') or mk.startswith('ГС')) else mk[:2]
    if r['kind']=='C':
        mem.append(dict(id=r['id'],mark=mk,cls=cls,a=(f(r['bx0'])+ (f(r['bx1'])-f(r['bx0']))/2, f(r['by0'])+(f(r['by1'])-f(r['by0']))/2, f(r['bz0'])), b=(f(r['bx0'])+(f(r['bx1'])-f(r['bx0']))/2, f(r['by0'])+(f(r['by1'])-f(r['by0']))/2, f(r['bz1']))))
    else:
        mem.append(dict(id=r['id'],mark=mk,cls=cls,a=(f(r['x0']),f(r['y0']),f(r['z0'])),b=(f(r['x1']),f(r['y1']),f(r['z1']))))
def seg_dist(p,a,b):
    ab=[b[i]-a[i] for i in range(3)]; ap=[p[i]-a[i] for i in range(3)]
    L2=sum(x*x for x in ab)
    t=0 if L2==0 else max(0,min(1,sum(ap[i]*ab[i] for i in range(3))/L2))
    q=[a[i]+ab[i]*t for i in range(3)]
    return math.dist(p,q)
def plan_dist(p,a,b):
    return seg_dist((p[0],p[1],0),(a[0],a[1],0),(b[0],b[1],0))
# LIRA coordinate -> model (loose): x*1000, y*1000, z: <=5 -> +1000 ; >5 : roof (use +600 loose)
def mp(p,qr=None):
    x,y,z=p[0]*1000,p[1]*1000,p[2]*1000
    zz=z+1000 if z<=5000 else z+600
    return (x,y,zz)
bycls=collections.defaultdict(list)
for m in mem: bycls[m['cls']].append(m)
miss=[]; ok=0
for r in rods:
    cls=INCL[r['s']]
    ps=[0.1,0.3,0.5,0.7,0.9]
    allok=True; worst=0
    for t in ps:
        pt=tuple(r['p'][i]+(r['q'][i]-r['p'][i])*t for i in range(3)); m3=mp(pt)
        best=1e18
        for m in bycls[cls]:
            # horizontal distance + loose z
            d=plan_dist(m3,m['a'],m['b'])
            if cls in('К1','К2','К3'):
                # column: plan distance only and z inside
                z0=min(m['a'][2],m['b'][2])-600; z1=max(m['a'][2],m['b'][2])+600
                if not (z0<=m3[2]<=z1): continue
            best=min(best,d)
        worst=max(worst,best)
    tol=700 if cls in ('СВ','ГС') else 450
    if worst>tol: miss.append((r['i'],cls,round(worst),[round(v,3) for v in r['p']],[round(v,3) for v in r['q']]))
    else: ok+=1
P('LIRA rods matched by loose plan-distance test:',ok,'unmatched',len(miss))
for x in miss[:25]: P('  UNMATCHED',x)
# reverse: model members with no LIRA rod nearby (plan, class)
rb=collections.defaultdict(list)
for r in rods: rb[INCL[r['s']]].append(r)
extra=[]
for m in mem:
    cls=m['cls']; mid=tuple((m['a'][i]+m['b'][i])/2 for i in range(3))
    best=1e18
    for r in rb[cls]:
        a=mp(r['p']); b=mp(r['q'])
        best=min(best,plan_dist(mid,a,b))
    tol=700 if cls in ('СВ','ГС') else 450
    if best>tol: extra.append((m['id'],m['mark'],round(best),[round(v) for v in mid]))
P('model members with no LIRA rod within tol:',len(extra))
for x in extra[:20]: P('  EXTRA',x)
# length totals by class (LIRA vs model)
Ll=collections.defaultdict(float); Lm=collections.defaultdict(float)
for r in rods: Ll[INCL[r['s']]]+=math.dist(r['p'],r['q'])
for m in mem: Lm[m['cls']]+=math.dist(m['a'],m['b'])/1000
for c in sorted(set(list(Ll)+list(Lm))): P(c,'LIRA Σ length m',round(Ll[c],1),'model Σ length m (axis)',round(Lm[c],1),'ratio',round(Lm[c]/Ll[c],3) if Ll[c] else None)
# counts of members per grid location for columns
colxy=collections.Counter((round(m['a'][0]/50)*50,round(m['a'][1]/50)*50) for m in mem if m['cls'] in('К1','К2','К3'))
P('column positions',len(colxy))
# LIRA column nodes (rods s 18,19,20)
lc=set()
for r in rods:
    if r['s'] in(18,19,20): lc.add((round(r['p'][0],1),round(r['p'][1],1)))
P('LIRA column XY positions',len(lc))
# which LIRA column positions lack a model column within 400
lacking=[]
cols=[m for m in mem if m['cls'] in('К1','К2','К3')]
for (x,y) in lc:
    if not any(math.hypot(m['a'][0]-x*1000,m['a'][1]-y*1000)<400 for m in cols): lacking.append((x,y))
P('LIRA column positions without model column (<400mm):',lacking)
out.close()