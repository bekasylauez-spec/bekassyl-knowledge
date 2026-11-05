import csv,pickle,collections,sys,json
sys.path.insert(0,'.'); import model as M
els,nodes=pickle.load(open('lira6/m.pkl','rb'))
AS={}
for r in csv.reader(open('arm/as_pl6.csv',encoding='utf-8',errors='replace'),delimiter=';'):
    if len(r)<12 or not r[4].strip().isdigit(): continue
    try: v=[float(x) for x in r[8:12]]
    except ValueError: continue
    e=int(r[4]); AS[e]=[max(a,b) for a,b in zip(AS.get(e,[0,0,0,0]),v)]
cells=[]
for i,r in enumerate(els):
    t=int(r[0])
    if t not in (41,42,44): continue
    ns=[nodes[int(k)-1] for k in r[2:]]
    xs=[n[0] for n in ns]; ys=[n[1] for n in ns]; zs=[n[2] for n in ns]
    if max(zs)-min(zs)<1e-3: continue          # horizontal plate
    a=AS.get(i+1)
    if a is None: continue
    if max(xs)-min(xs)<1e-3: pl=('x',round(xs[0]*1000))
    elif max(ys)-min(ys)<1e-3: pl=('y',round(M.fy(ys[0])))
    else: continue
    lo=[min(xs)*1000,M.fy(min(ys))]; hi=[max(xs)*1000,M.fy(max(ys))]
    cells.append(dict(id=i+1,st=int(r[1]),pl=pl,x0=lo[0],x1=hi[0],y0=lo[1],y1=hi[1],z0=min(zs),z1=max(zs),As=a))
json.dump(cells,open('arm/wall_cells.json','w'))
c=collections.Counter(x['pl'] for x in cells)
for k,v in sorted(c.items()): 
    sel=[x for x in cells if x['pl']==k]
    mx=[max(x['As'][j] for x in sel) for j in range(4)]
    print(k,v,'z %.2f..%.2f'%(min(x['z0'] for x in sel),max(x['z1'] for x in sel)),'maxAS',[round(m,2) for m in mx], 'stiff',collections.Counter(x['st'] for x in sel).most_common(3))
