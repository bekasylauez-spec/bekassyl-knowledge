import io, collections, csv, re, math
D=r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\mine\\"
out=io.open(D+'a6_out.txt','w',encoding='utf-8')
def P(*a): out.write(' '.join(str(x) for x in a)+'\n')
DS={r['id']:r for r in csv.DictReader(io.open(D+'ds.tsv',encoding='utf-8'),delimiter='\t')}
SS=list(csv.DictReader(io.open(D+'dssolid.tsv',encoding='utf-8'),delimiter='\t'))
F=list(csv.DictReader(io.open(D+'frame.tsv',encoding='utf-8'),delimiter='\t'))
P('DS',len(DS),'solids',len(SS))
# --- materials of DS solids
mc=collections.Counter(s['mat'] for s in SS); P('DS solid materials:',dict(mc))
bad=[s for s in SS if not s['mat'].startswith('КМ_уз_')]
P('DS solids with non КМ_уз_ material:',len(bad), collections.Counter((DS[s['id']]['appid'],s['mat']) for s in bad))
# name keyword -> material
def kw(n):
    nl=n.lower()
    for k in ('шов','заглушка','вставка','гусет','фасонка','гайка','шайба','болт','анкер','ребро','оголовок','диафрагма','кронштейн','фланец','накладка','прокладка','плита','траверса','подливка','лист','тартпа','рельс','уголок','швеллер','брус','косынка','рыбка','тіреуіш','подколонник','тірек','жота','столик'):
        if k in nl: return k
    return 'other'
mm=collections.defaultdict(collections.Counter)
for s in SS:
    n=DS[s['id']]['name']; n=re.sub(r'^.*? - ','',n) if ' - ' in n else n
    mm[kw(n)][s['mat']]+=1
for k,v in sorted(mm.items()): P(k, dict(v))
# --- mark material colours vs part colours
pal={}
for s in SS: pass
markcol={}
for f in F: markcol[f['mark']]=(f['r'],f['g'],f['b'])
# duplicates among mark colors
byc=collections.defaultdict(list)
for k,v in markcol.items(): byc[v].append(k)
P('mark colour duplicates:',[ (v,k) for v,k in byc.items() if len(k)>1])
# near-colours between marks (distance<40)
mk=sorted(markcol.items())
near=[]
for i in range(len(mk)):
    for j in range(i+1,len(mk)):
        a=tuple(map(int,mk[i][1])); b=tuple(map(int,mk[j][1])); d=math.dist(a,b)
        if d<60: near.append((mk[i][0],mk[j][0],round(d)))
P('mark colour pairs with RGB distance <60:',near)
# part-type colour vs mark colour
PCOL={'КМ_уз_плита':(70,130,180),'КМ_уз_ребро':(60,160,90),'КМ_уз_столик':(230,150,30),'КМ_уз_ребро_столика':(150,100,50),'КМ_уз_накладка':(0,150,160),'КМ_уз_уголок':(130,90,170),'КМ_уз_фасонка':(200,60,60),'КМ_уз_вставка':(120,150,30),'КМ_уз_заглушка':(150,150,150),'КМ_уз_фланец':(40,80,150),'КМ_уз_прокладка':(210,180,60),'КМ_уз_брус':(160,120,80),'КМ_уз_болт':(60,60,60),'КМ_уз_шов':(110,110,110),'КМ_уз_рельс':(95,100,115),'КМ_уз_стойка':(160,60,150),'КМ_уз_швеллер':(210,120,160),'КМ_уз_тартпа':(215,125,70)}
cl=[]
for pn,pc in PCOL.items():
    for m,c in markcol.items():
        d=math.dist(pc,tuple(map(int,c)))
        if d<45: cl.append((pn,m,round(d)))
P('part colour ~ mark colour (dist<45):',cl)
# --- DS location structure: bbox span per DS and per (key,loc)
big=[]
for i,r in DS.items():
    if r['bx0']=='' : continue
    sp=max(float(r['bx1'])-float(r['bx0']),float(r['by1'])-float(r['by0']),float(r['bz1'])-float(r['bz0']))
    if sp>2500 and not r['appid']=='БК_ЖБ': big.append((round(sp),r['name'][:60],r['nsol'],r['id']))
big.sort(reverse=True); P('DS with bbox span>2500:',len(big)); 
for b in big[:15]: P('   ',b)
noloc=[r for r in DS.values() if '|' not in r['appdata'] or r['appdata'].split('|')[1].strip()=='']
P('DS without location in ApplicationDataId:',len(noloc),[ (r['name'][:50],r['appdata']) for r in noloc[:5]])
multi=[r for r in DS.values() if int(r['nsol'])>1]
cm=collections.Counter(re.sub(r' - [^ ]+$','',r['name']) for r in multi); P('DS with >1 solid:',len(multi)); 
for k,v in cm.most_common(25): P('   ',v,k[:90], 'maxnsol',max(int(r['nsol']) for r in multi if re.sub(r' - [^ ]+$','',r['name'])==k))
# location groups: per (key,loc) span
grp=collections.defaultdict(list)
for r in DS.values():
    if r['bx0']=='' or r['appid']=='БК_ЖБ': continue
    k=(r['appdata'].split('|')[0].strip(), r['appdata'].split('|')[1].strip() if '|' in r['appdata'] else '')
    grp[k].append(r)
wide=[]
for k,l in grp.items():
    x0=min(float(r['bx0']) for r in l); x1=max(float(r['bx1']) for r in l); y0=min(float(r['by0']) for r in l); y1=max(float(r['by1']) for r in l); z0=min(float(r['bz0']) for r in l); z1=max(float(r['bz1']) for r in l)
    sp=max(x1-x0,y1-y0,z1-z0)
    wide.append((round(sp),k,len(l)))
wide.sort(reverse=True)
P('location groups (key,loc):',len(grp),'widest spans:',wide[:12])
out.close()