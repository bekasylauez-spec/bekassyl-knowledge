import pickle, sys, collections
hor,ver,bars=pickle.load(open(sys.argv[1]+'/g.pkl','rb'))
a,b=float(sys.argv[2]),float(sys.argv[3])
seg=collections.defaultdict(list)   # key (dir, coord, st) -> intervals
for st,ns in ver:
    zs=[n[2] for n in ns]; zm=sum(zs)/len(zs)
    if not (a<zm<b): continue
    xs=[n[0] for n in ns]; ys=[n[1] for n in ns]
    if max(xs)-min(xs)>1e-3 and max(ys)-min(ys)<1e-3: seg[('H',round(ys[0],3),st)].append((min(xs),max(xs),min(zs),max(zs)))
    elif max(ys)-min(ys)>1e-3 and max(xs)-min(xs)<1e-3: seg[('V',round(xs[0],3),st)].append((min(ys),max(ys),min(zs),max(zs)))
    else: print('skew',st,[(round(n[0],2),round(n[1],2)) for n in ns])
for k in sorted(seg):
    iv=sorted(seg[k]); out=[]
    for s,e,z0,z1 in iv:
        if out and s<=out[-1][1]+1e-3: out[-1][1]=max(out[-1][1],e); out[-1][2]=min(out[-1][2],z0); out[-1][3]=max(out[-1][3],z1)
        else: out.append([s,e,z0,z1])
    print(k, [(round(s,3),round(e,3),round(z0,2),round(z1,2)) for s,e,z0,z1 in out])
for st,ns in bars:
    zm=(ns[0][2]+ns[1][2])/2
    if a<zm<b and abs(ns[0][0]-ns[1][0])<1e-3 and abs(ns[0][1]-ns[1][1])<1e-3: print('col',st,round(ns[0][0],3),round(ns[0][1],3),round(ns[0][2],2),round(ns[1][2],2))
