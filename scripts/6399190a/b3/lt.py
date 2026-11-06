import re,sys,json,collections
T=open(sys.argv[1],encoding='utf-8-sig').read()
docs={}
for m in re.finditer(r'\(\s*(\d+)\s*/(.*?)\)',T,re.S):
    docs.setdefault(int(m.group(1)),m.group(2))
def recs(s): return [r.split() for r in s.split('/') if r.strip()]
el=recs(docs[1]); xyz=[list(map(float,r)) for r in recs(docs[4])]
# stiffness: parse doc3 blocks
st={}; cur=None
for r in recs(docs[3]):
    if r[0]!='0': cur=int(r[0]); st[cur]={'raw':r}
    elif r[1]=='S8': st[cur]['s8']=r[2:]
    else: st[cur].setdefault('x',[]).append(r[1:])
bars=[]
for i,r in enumerate(el,1):
    t,s=int(r[0]),int(r[1]); n=list(map(int,r[2:]))
    if t==10 and len(n)==2:
        a,b=xyz[n[0]-1],xyz[n[1]-1]
        if abs(a[0]-b[0])<1e-3 and abs(a[1]-b[1])<1e-3:
            bars.append((i,s,a[0],a[1],min(a[2],b[2]),max(a[2],b[2])))
c=collections.Counter(b[1] for b in bars)
for s,k in sorted(c.items()):
    zs=[b for b in bars if b[1]==s]
    print('stiff',s,st[s].get('s8'),'n',k,'z',min(b[4] for b in zs),max(b[5] for b in zs), 'xy',len({(round(b[2],2),round(b[3],2)) for b in zs}))
json.dump({'bars':bars,'st':{k:v.get('s8') for k,v in st.items()}},open(sys.argv[2],'w'))
print('types',collections.Counter(int(r[0]) for r in el))
