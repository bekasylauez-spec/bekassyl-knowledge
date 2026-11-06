import pickle,collections,re
els,nodes,stf=pickle.load(open('m3.pkl','rb'))
def sec(s):
    m=re.search(r'S0 \S+ (\S+) (\S+)',stf[s]); return '%sx%s'%(m.group(1),m.group(2)) if m else None
H=collections.defaultdict(list); V=collections.defaultdict(list)
for i,(ty,s,ns) in enumerate(els,1):
    if ty!=10 or len(ns)!=2: continue
    sc=sec(s)
    if not sc: continue
    a,b=nodes[ns[0]-1],nodes[ns[1]-1]
    if abs(a[2]-b[2])<0.005:
        if abs(a[1]-b[1])<0.005: H[('X',round(a[2],3),round(a[1],3),sc)].append((round(min(a[0],b[0]),3),round(max(a[0],b[0]),3),i))
        elif abs(a[0]-b[0])<0.005: H[('Y',round(a[2],3),round(a[0],3),sc)].append((round(min(a[1],b[1]),3),round(max(a[1],b[1]),3),i))
        else: H[('?',round(a[2],3),0,sc)].append((a,b,i))
    else:
        V[(round(a[0],3),round(a[1],3),sc)].append((round(min(a[2],b[2]),3),round(max(a[2],b[2]),3)))
def merge(rs):
    rs=sorted(rs); out=[[rs[0][0],rs[0][1]]]
    for a,b,_ in rs[1:]:
        if a<=out[-1][1]+0.001: out[-1][1]=max(out[-1][1],b)
        else: out.append([a,b])
    return out
for k in sorted(H,key=lambda k:(k[1],k[0],k[3],k[2])):
    if k[0]=='?': print(k,len(H[k])); continue
    print(k,len(H[k]),merge(H[k]))
print('--- columns')
for k in sorted(V):
    r=sorted(V[k]); print(k, r[0][0], r[-1][1])
pickle.dump(dict(H),open('blines.pkl','wb'))
