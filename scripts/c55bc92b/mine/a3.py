import io, collections, csv
D=r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\mine\\"
out=io.open(D+'a3_out.txt','w',encoding='utf-8')
def P(*a): out.write(' '.join(str(x) for x in a)+'\n')
R=list(csv.DictReader(io.open(D+'ends.tsv',encoding='utf-8'),delimiter='\t'))
ends=collections.defaultdict(dict)
for r in R: ends[(r['id'],r['end'])][r['cls']]=r
P('ends',len(ends))
TUBES=('Р1','Р2','Р3','СВ1','СВ2','СВ3','СВ4','СВ5','ГС1','ГС2')
noface=[k for k,v in ends.items() if 'NOENDFACE' in [x.get('nsamp') for x in v.values()] or any(x['nsamp']=='0' for x in v.values())]
P('no end face:',len(noface), noface[:10])
def f(x): return float(x) if x not in ('',None) else None
# tubes: cap
tb=[(k,v) for k,v in ends.items() if list(v.values())[0]['mark'] in TUBES and k not in noface]
P('tube ends',len(tb))
nocap=[(k,list(v.values())[0]['mark'],list(v.values())[0]['im'],list(v.values())[0]['cx'],list(v.values())[0]['cy'],list(v.values())[0]['cz'],list(v.values())[0]['capFrac']) for k,v in tb if f(list(v.values())[0]['capFrac'])<0.8]
P('tube ends without cap (capFrac<0.8):',len(nocap))
bm=collections.Counter(x[1] for x in nocap); P(dict(bm))
for x in nocap[:40]: P('  ',x)
# capFrac histogram
h=collections.Counter(round(f(list(v.values())[0]['capFrac']),1) for k,v in tb); P('capFrac hist',sorted(h.items()))
# contact classes for all ends
cat=collections.Counter(); ex=collections.defaultdict(list)
for k,v in ends.items():
    if k in noface: continue
    m=list(v.values())[0]['mark']
    fr=f(v['frame']['bestAbs']); pl=f(v['plate']['bestAbs']); cp=f(v['cap']['bestAbs']); wl=f(v['weld']['bestAbs']); cn=f(v['conc']['bestAbs'])
    cand=[x for x in (fr,pl,cp,cn) if x is not None]
    g=min(cand) if cand else None
    if g is None: c='free(>80)'
    elif g<=0.05: c='touch(<=0.05)'
    elif g<=0.5: c='gap 0.05-0.5'
    elif g<=5: c='gap 0.5-5'
    elif g<=30: c='gap 5-30'
    else: c='gap 30-80'
    cat[(m,c)]+=1; ex[(m,c)].append((k,v['frame']['bestAbs'],v['frame']['bestSigned'],v['frame']['bestName'],v['plate']['bestAbs'],v['plate']['bestName']))
marks=sorted(set(k[0] for k in cat))
for m in marks:
    P(m, {c:n for (mm,c),n in cat.items() if mm==m})
P('--- gap examples (0.05..80)')
for (m,c),l in sorted(ex.items()):
    if c.startswith('gap'):
        P(m,c,len(l))
        for e in l[:3]: P('    ',e)
# end-face angle for Б1..Б3 ригель, Б4,Б5, КБ1,ПБ1
P('--- end-face normal angle from horizontal (deg) for beams (vertical end face -> 0)')
for m in ('Б1','Б2','Б3','Б4','Б5','КБ1','ПБ1','Пр1'):
    a=[(f(list(v.values())[0]['angHorz']),k[1],list(v.values())[0]['im']) for k,v in ends.items() if list(v.values())[0]['mark']==m and k not in noface]
    if not a: continue
    P(m,'n',len(a),'min',round(min(x[0] for x in a),3),'max',round(max(x[0] for x in a),3),'hist',sorted(collections.Counter(round(x[0],1) for x in a).items()))
# columns: end face angle
P('--- columns tops')
for m in ('К1','К2','К3'):
    a=[(f(list(v.values())[0]['angHorz']),k) for k,v in ends.items() if list(v.values())[0]['mark']==m]
    P(m, sorted(collections.Counter(round(x[0],1) for x in a).items()))
out.close()