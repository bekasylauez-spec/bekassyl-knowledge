import io, collections, csv, re
D=r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\mine\\"
out=io.open(D+'a4_out.txt','w',encoding='utf-8')
def P(*a): out.write(' '.join(str(x) for x in a)+'\n')
R=list(csv.DictReader(io.open(D+'colrays.tsv',encoding='utf-8'),delimiter='\t'))
P('rays',len(R))
res=collections.defaultdict(list)
for r in R:
    segs=[]
    for s in r['segs'].split(' ; '):
        m=re.match(r'([\-\d.]+)\.\.([\-\d.]+) (.*)',s)
        if m: segs.append((float(m.group(1)),float(m.group(2)),m.group(3)))
    segs.sort()
    top=float(r['colTop'])
    # chain starting from segment of column
    colseg=[s for s in segs if s[2].startswith(r['mark'])]
    if not colseg: res[r['mark']].append((r['id'],r['im'],'NOCOL',r['px'],r['py'])); continue
    ct=max(s[1] for s in colseg)
    chain=[]; cur=ct; 
    # walk upward: next segments by start
    above=[s for s in segs if s[0]>=ct-0.05 and not s[2].startswith(r['mark'])]
    if not above: res[r['mark']].append((r['id'],r['im'],'NOTHING_ABOVE',round(ct,2),r['px'],r['py'])); continue
    nxt=above[0]
    gap=nxt[0]-ct
    # find also beam: first segment named Б*
    beam=[s for s in above if s[2].startswith('Б')]
    bgap=(beam[0][0]-ct) if beam else None
    # plate chain contiguous?
    chn=[]; z=ct
    for s in above:
        if s[0]<=z+0.05: chn.append(s[2].split(' - ')[1] if ' - ' in s[2] else s[2]); z=max(z,s[1])
    res[r['mark']].append((r['id'],r['im'],round(ct,2),round(gap,2),nxt[2][:50],None if bgap is None else round(bgap,2),chn[:3], r['px'],r['py']))
for m,l in res.items():
    P('==',m,len(l))
    c=collections.Counter()
    for x in l:
        if len(x)>3 and isinstance(x[3],float): c[x[3]]+=1
        else: c[x[2]]+=1
    P(sorted(c.items(),key=lambda t:-t[1])[:25])
    seen=set()
    for x in l:
        k=(x[1])
        if k in seen: continue
        seen.add(k)
        if len(seen)<=14: P('   ',x)
out.close()