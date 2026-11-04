import pickle, sys, collections, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
els,nodes=pickle.load(open(sys.argv[1],'rb'))
def N(i): return nodes[int(i)-1]
hor=collections.defaultdict(list); ver=[]; bars=[]
for r in els:
    t=int(r[0]); st=int(r[1]); ns=[N(i) for i in r[2:]]
    if t in (41,42,44):
        zs=[n[2] for n in ns]
        if max(zs)-min(zs)<1e-3: hor[round(zs[0],3)].append((st,ns))
        else: ver.append((st,ns))
    elif t==10: bars.append((st,ns))
for z,v in sorted(hor.items()):
    if len(v)>20: print('slab z',z,len(v),collections.Counter(s for s,_ in v), 'x',round(min(n[0] for _,ns in v for n in ns),3),round(max(n[0] for _,ns in v for n in ns),3),'y',round(min(n[1] for _,ns in v for n in ns),3),round(max(n[1] for _,ns in v for n in ns),3))
print('walls',len(ver),collections.Counter(s for s,_ in ver)); print('bars',len(bars),collections.Counter(s for s,_ in bars))
pickle.dump((hor,ver,bars),open(sys.argv[2],'wb'))
