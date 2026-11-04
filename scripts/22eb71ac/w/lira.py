import re,collections,sys
t=open(sys.argv[1],encoding='utf-8-sig').read()
docs={}
for m in re.finditer(r'\(\s*(\d+)/(.*?)\)',t,re.S): docs.setdefault(int(m.group(1)),m.group(2))
def recs(s): return [r.split() for r in s.split('/') if r.strip()]
els=recs(docs[1]); nodes=[list(map(float,r)) for r in recs(docs[4])]
print('elements',len(els),'nodes',len(nodes))
byst=collections.defaultdict(list)
for i,r in enumerate(els):
    typ,st=int(r[0]),int(r[1]); ns=[int(x) for x in r[2:]]
    byst[(typ,st)].append((i+1,ns))
for k,v in sorted(byst.items()):
    xs=[nodes[n-1] for _,ns in v for n in ns]
    print(k,len(v),'x',min(p[0] for p in xs),max(p[0] for p in xs),'y',min(p[1] for p in xs),max(p[1] for p in xs),'z',sorted(set(round(p[2],3) for p in xs))[:12])
# bars detail
for k,v in sorted(byst.items()):
    if k[0] in (10,5,2):
        segs=set()
        for _,ns in v:
            a,b=nodes[ns[0]-1],nodes[ns[1]-1]
            segs.add(tuple(round(c,2) for c in a+b))
        print('BAR',k)
        # merge collinear: print unique x,y lines
        if k[1]==1:
            print(' cols xy',sorted(set((s[0],s[1]) for s in segs)), 'z',sorted(set(s[2] for s in segs)|set(s[5] for s in segs)))
        else:
            hor=collections.defaultdict(list)
            for s in segs:
                if s[1]==s[4]: hor[('y',s[1],s[2])].append((s[0],s[3]))
                elif s[0]==s[3]: hor[('x',s[0],s[2])].append((s[1],s[4]))
                else: hor['other'].append(s)
            for kk,vv in sorted(hor.items(),key=str):
                if kk=='other': print('  other',vv[:5]); continue
                lo=min(min(a,b) for a,b in vv); hi=max(max(a,b) for a,b in vv); print('  ',kk,lo,hi)
print('--- wall planes st6 and st5')
for st in (6,5):
    planes=collections.defaultdict(list)
    for _,ns in byst[(44,st)]:
        ps=[nodes[n-1] for n in ns]
        xs=set(round(p[0],3) for p in ps); ys=set(round(p[1],3) for p in ps)
        if len(xs)==1: planes[('x',xs.pop())]+= [p[1] for p in ps]
        elif len(ys)==1: planes[('y',ys.pop())]+= [p[0] for p in ps]
        else: planes['h']+=[0]
    for k,v in sorted(planes.items(),key=str): print(st,k,min(v),max(v),len(v)//4)
# holes in slabs: find node grid xy of st7 and st8 and report missing areas roughly
for st in (7,8):
    cells=[]
    for _,ns in byst[(44,st)]:
        ps=[nodes[n-1] for n in ns]; cells.append((min(p[0] for p in ps),min(p[1] for p in ps),max(p[0] for p in ps),max(p[1] for p in ps)))
    A=sum((c[2]-c[0])*(c[3]-c[1]) for c in cells); print('slab',st,'area',round(A,2))
