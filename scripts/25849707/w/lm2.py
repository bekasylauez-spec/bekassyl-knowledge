import pickle,collections
els,nodes,st=pickle.load(open('lm.pkl','rb'))
c=collections.Counter(); L=collections.defaultdict(float)
for i,(ty,s,nn) in enumerate(els):
    if ty!=10 or s not in (25,26,27,28,29,30,31,32,46,47,37,38): continue
    a,b=nodes[nn[0]-1],nodes[nn[1]-1]
    hz=abs(a[2]-b[2])<1e-3
    k=(s,st[s]['raw'][:30],'H z=%.3f'%a[2] if hz else 'V')
    c[k]+=1; L[k]+=((a[0]-b[0])**2+(a[1]-b[1])**2+(a[2]-b[2])**2)**.5
for k in sorted(c): print(k,c[k],round(L[k],1))
