import pickle,collections
m=pickle.load(open('geo.pkl','rb'));N=m['nodes']
def pl(base):
    ok=0
    for ns in m['plates'][:2000]:
        try: P=[N[i-base] for i in ns]
        except IndexError: return 0
        if any(max(p[j] for p in P)-min(p[j] for p in P)<1e-4 for j in range(3)): ok+=1
    return ok/2000
for b in (0,1,2): print('base',b,pl(b))
