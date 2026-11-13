import io, collections, csv, re, math
D=r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\q20\\"
out=io.open(D+'a8_out.txt','w',encoding='utf-8')
def P(*a): out.write(' '.join(str(x) for x in a)+'\n')
def f(x): 
    try: return float(x)
    except: return None
B=list(csv.DictReader(io.open(D+'bolts.tsv',encoding='utf-8'),delimiter='\t'))
P('=== BOLTS: stems',len(B))
nop=[b for b in B if b['nPierced']=='0']
P('stems piercing nothing (no frame/plate surface found):',len(nop), collections.Counter(re.sub(r' - [^ ]+$','',b['name'])[:60] for b in nop).most_common(8))
# edge distance by diameter
res=collections.defaultdict(list)
for b in B:
    e=f(b['edgeMin']); d=f(b['diaMM'])
    if e is None: continue
    res[round(d)].append((e,b))
for d,l in sorted(res.items()):
    l.sort(key=lambda t:t[0])
    P('dia',d,'n',len(l),'min edge',round(l[0][0],1),'1.2d =',round(1.2*d,1),'1.5d =',round(1.5*d,1),' count <1.2d:',sum(1 for e,b in l if e<1.2*d-0.01),' <1.5d:',sum(1 for e,b in l if e<1.5*d-0.01))
    for e,b in l[:5]: P('     ',round(e,1),b['name'][:70],'|',b['loc'],'|',b['edgeItem'][:60])
# group failing <1.5d by node-type
bad=collections.Counter(); badex={}
for d,l in res.items():
    for e,b in l:
        if e<1.5*d-0.01:
            k=re.sub(r' - [^ ]+$','',b['name']); k=re.sub(r'\s*\(.*?\)','',k)[:70]
            bad[(k,b['edgeItem'].split(' - ')[-2] if ' - ' in b['edgeItem'] else b['edgeItem'][:30])]+=1; badex.setdefault((k,b['edgeItem'].split(' - ')[-2] if ' - ' in b['edgeItem'] else b['edgeItem'][:30]),(round(e,1),b['loc'],b['edgeItem'][:50]))
P('--- edge<1.5d by (bolt group, item):')
for k,v in bad.most_common(30): P('   ',v,k,badex[k])
# pitch
pit=collections.defaultdict(list)
for b in B:
    p=f(b['pitchMin']); d=f(b['diaMM'])
    if p is None: continue
    pit[round(d)].append((p,b))
for d,l in sorted(pit.items()):
    l.sort(key=lambda t:t[0])
    P('PITCH dia',d,'n',len(l),'min',round(l[0][0],1),'2.5d=',round(2.5*d,1),' count<2.5d:',sum(1 for p,b in l if p<2.5*d-0.01),' hist',sorted(collections.Counter(round(p) for p,b in l).items())[:10])
    for p,b in l[:4]: P('     ',round(p,1),b['name'][:70],b['loc'])
# --- plates outstand
Pl=list(csv.DictReader(io.open(D+'plates.tsv',encoding='utf-8'),delimiter='\t'))
P('=== PLATE contacts to frame side faces',len(Pl))
byname=collections.defaultdict(list)
for r in Pl:
    n=re.sub(r' - [^ ]+$','',r['name']); byname[n].append(r)
rows=[]
for n,l in byname.items():
    rat=[f(r['ratio']) for r in l]; outs=[f(r['outstand']) for r in l]; t=f(l[0]['t'])
    rows.append((max(rat),n,len(l),t,max(outs),l[0]['contactMark']))
rows.sort(reverse=True)
for r in rows[:50]: P('   ratio max %.1f | %s | n=%d t=%.1f outstand max=%.1f | support %s'%(r[0],r[1][:80],r[2],r[3],r[4],r[5]))
P('plates (by name) with ratio>15:',sum(1 for r in rows if r[0]>15),'of',len(rows))
out.close()