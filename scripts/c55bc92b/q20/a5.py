import io, collections, csv, re
D=r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\q20\\"
out=io.open(D+'a5_out.txt','w',encoding='utf-8')
def P(*a): out.write(' '.join(str(x) for x in a)+'\n')
# cap probe
R=list(csv.DictReader(io.open(D+'capprobe.tsv',encoding='utf-8'),delimiter='\t'))
P('capprobe rows',len(R))
byk=collections.defaultdict(list)
for r in R:
    v=r.get('vertexDistToCapPlane(mm,signed along end normal)')
    if v is None: P('NOCAP',r['id'],r['mark'],r['im'],r['end']); continue
    ds=[float(x) for x in v.split()]
    byk[r['mark']].append((max(abs(x) for x in ds),min(ds),max(ds),r['dotNormals'],r['capName'][:40],r['id'],r['im'],r['end']))
for m,l in byk.items():
    l.sort(reverse=True)
    P(m,'n',len(l),'max|d| hist',sorted(collections.Counter(round(x[0],1) for x in l).items()))
    for x in l[:6]: P('   ',x)
    P('   dot hist',sorted(collections.Counter(x[3] for x in l).items()))
# rays2
R=list(csv.DictReader(io.open(D+'colrays2.tsv',encoding='utf-8'),delimiter='\t'))
P('rays',len(R))
res=collections.defaultdict(lambda: collections.defaultdict(list))
for r in R:
    segs=[]
    for s in r['segs'].split(' ; '):
        m=re.match(r'([\-\d.]+)\.\.([\-\d.]+) (.*)',s)
        if m: segs.append((float(m.group(1)),float(m.group(2)),m.group(3)))
    segs.sort()
    colseg=[s for s in segs if s[2].startswith(r['mark']+' ')]
    if not colseg: continue
    ct=max(s[1] for s in colseg)
    above=[s for s in segs if s[0]>=ct-0.05 and not s[2].startswith(r['mark']+' ')]
    if not above: res[r['mark']][r['im']].append(('NOTHING',ct)); continue
    gap=round(above[0][0]-ct,2)
    chain=[]; z=ct
    for s in above:
        if s[0]<=z+0.05: chain.append(re.sub(r' - [\w\-+]+$','',s[2])[:45]); z=max(z,s[1])
        else: break
    res[r['mark']][r['im']].append((gap,round(ct,1),round(z,1),chain))
for m,d in res.items():
    P('==',m,'columns with hits',len(d))
    allg=collections.Counter(); 
    for im,l in d.items():
        for x in l: allg[x[0]]+=1
    P('gap above column top: ',sorted(allg.items(),key=lambda t:-t[1])[:12])
    # distinct chains
    ch=collections.Counter()
    for im,l in d.items():
        for x in l:
            if x[0]=='NOTHING': ch['NOTHING']+=1
            else: ch[(x[0],tuple(x[3]))]+=1
    for k,v in ch.most_common(8): P('   ',v,k)
    # columns with any ray where gap>0.5 or NOTHING
    badc=[im for im,l in d.items() if all((x[0]=='NOTHING' or x[0]>0.5) for x in l)]
    P('  columns whose every hit-ray has gap>0.5 or nothing above:',len(badc),badc[:12])
out.close()