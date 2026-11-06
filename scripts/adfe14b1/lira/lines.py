import pickle,collections,re
els,nodes,stf=pickle.load(open('m4.pkl','rb'))
def sec(s):
    m=re.search(r'S0 \S+ (\S+) (\S+)',stf[s]); 
    if m: return '%sx%s'%(m.group(1),m.group(2))
    m=re.search(r'S50 \S+ (.*?) \|',stf[s]); return 'T'+m.group(1).replace(' ','/') if m else '?'
X0=174.15
L=collections.defaultdict(list)
for i,(ty,s,ns) in enumerate(els,1):
    if ty!=10 or len(ns)!=2: continue
    a,b=nodes[ns[0]-1],nodes[ns[1]-1]
    if abs(a[2]-b[2])>0.01 or round(a[2],2) not in (-0.05,4.5,7.0): continue
    if not stf[s].split()[1].startswith('S'): continue
    p=[(round((n[0]-X0)*1000),round(n[1]*1000)) for n in (a,b)]
    if p[0][1]==p[1][1]: k=('X',a[2],p[0][1],sec(s)); r=sorted([p[0][0],p[1][0]])
    elif p[0][0]==p[1][0]: k=('Y',a[2],p[0][0],sec(s)); r=sorted([p[0][1],p[1][1]])
    else: k=('?',a[2],0,sec(s)); r=p
    L[k].append((r[0],r[1],i))
pickle.dump(dict(L),open('blines.pkl','wb'))
def merge(rs):
    rs=sorted(rs); out=[[rs[0][0],rs[0][1]]]
    for a,b,_ in rs[1:]:
        if a<=out[-1][1]+1: out[-1][1]=max(out[-1][1],b)
        else: out.append([a,b])
    return out
for k in sorted(L,key=lambda k:(k[1],k[0],k[2])):
    print(k,len(L[k]),merge(L[k]))
