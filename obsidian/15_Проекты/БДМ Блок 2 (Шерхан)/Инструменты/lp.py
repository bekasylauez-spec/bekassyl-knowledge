import re, collections, json
t=open('lira.txt',encoding='utf-8').read()
docs={}
for m in re.finditer(r'\(\s*(\d+)/(.*?)\)', t, re.S): docs.setdefault(int(m.group(1)), m.group(2))
# stiffness: lines starting with number then values; sections S8 / S0 etc.
st={}; cur=None
for l in docs[3].split('/'):
    l=l.strip()
    if not l: continue
    m=re.match(r'^(\d+)\s+(S\d+)\s+(.*)',l)
    if m: st[int(m.group(1))]=(m.group(2),m.group(3)); cur=None; continue
    m=re.match(r'^(\d+)\s+[\d.e+-]+',l)
    if m and not l.startswith('0 '): cur=int(m.group(1)); continue
    m=re.match(r'^0\s+(S\d+)\s+(.*)',l)
    if m and cur: st[cur]=(m.group(1),m.group(2))
nodes=[tuple(map(float,s.split()[:3])) for s in docs[4].split('/') if s.strip()]
els=[]
for s in docs[1].split('/'):
    v=s.split()
    if len(v)>=4: els.append((int(v[0]),int(v[1]),[int(x) for x in v[2:]]))
print(len(nodes),len(els))
bars=collections.defaultdict(list)
for i,(ft,sti,nn) in enumerate(els,1):
    if ft in (10,5,2,1) and len(nn)==2:
        a=nodes[nn[0]-1]; b=nodes[nn[1]-1]
        if abs(a[2]-b[2])<1e-3 and (abs(a[0]-b[0])>1e-3 or abs(a[1]-b[1])>1e-3):
            bars[sti].append((i,a,b))
for k in sorted(bars):
    zs=collections.Counter(round(x[1][2],3) for x in bars[k])
    print(k, st.get(k), len(bars[k]), dict(zs))
json.dump({str(k):[(i,a,b) for i,a,b in v] for k,v in bars.items()},open('bars.json','w'))
