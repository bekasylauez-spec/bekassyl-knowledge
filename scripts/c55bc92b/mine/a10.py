import io, collections, csv, re
D=r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\mine\\"
out=io.open(D+'a10_out.txt','w',encoding='utf-8')
def P(*a): out.write(' '.join(str(x) for x in a)+'\n')
W=list(csv.DictReader(io.open(D+'welds_run1.tsv',encoding='utf-8'),delimiter='\t'))
P('weld solids',len(W))
c=collections.Counter(); ex=collections.defaultdict(list)
def kf(n):
    m=re.search(r'kf(\d+)',n); return int(m.group(1)) if m else None
for w in W:
    ls=int(w['legsSupported']); lt=int(w['legsTotal']); ov=float(w['maxOverhang']) if w['maxOverhang'] else 0
    key=re.sub(r' - [^ ]+$','',w['name']); key=re.sub(r'^.*? - ','',key)
    cat='ok'
    if ls<2: cat='legs<2'
    elif ov>1.0: cat='overhang>1mm'
    c[(cat)]+=1; 
    if cat!='ok': ex[(cat,key)].append((ls,lt,ov,w['id'],w['key'],w['loc']))
P('weld solids by category',dict(c))
rows=sorted(ex.items(), key=lambda t:-len(t[1]))
for (cat,key),l in rows[:60]:
    P(cat,'|',key[:70],'| n=',len(l),'| max overhang',round(max(x[2] for x in l),1),'| example',l[0])
# by key type: how many weld solids per DS name type with legs<2
t=collections.Counter()
for w in W:
    key=re.sub(r' - [^ ]+$','',w['name']); 
    t[key]+=1
out.close()