exec(open('groups.py',encoding='utf-8').read().split("o=open('groups.txt'")[0])
def comp(lst):
    # compress list of axis labels
    nums=sorted(set(lst),key=lambda s:(len(s),s))
    try:
        v=sorted(set(int(x) for x in lst)); out=[];st=v[0];pr=v[0]
        for x in v[1:]+[None]:
            if x is not None and x==pr+1: pr=x; continue
            out.append(f'{st}' if st==pr else f'{st}-{pr}'); 
            if x is not None: st=pr=x
        return ','.join(out)
    except: return ','.join(nums)
o=open('groups2.txt','w',encoding='utf-8')
for s in range(len(NAMES)):
    idx=[k for k in range(N) if stf[k]==s]
    if not idx: continue
    o.write(f'\n#### {s+1}. {NAMES[s]}  n={len(idx)}\n')
    V=collections.defaultdict(list); X=collections.defaultdict(list); Y=collections.defaultdict(list); D=collections.defaultdict(list); PL=collections.Counter()
    for k in idx:
        t,ns=els[k]
        if t==2: PL[tuple(sorted(set(round(P(i)[2],2) for i in ns)))[:2]]+=1; continue
        a,b=P(ns[0]),P(ns[1])
        if abs(a[0]-b[0])<1e-3 and abs(a[1]-b[1])<1e-3:
            V[(rw(a[1]),ax(a[0]))].append((min(a[2],b[2]),max(a[2],b[2])))
        elif abs(a[1]-b[1])<1e-3:
            X[(rw(a[1]),round((a[2]+b[2])/2,1))].append((min(a[0],b[0]),max(a[0],b[0])))
        elif abs(a[0]-b[0])<1e-3:
            Y[(ax(a[0]))].append((min(a[1],b[1]),max(a[1],b[1]),round(min(a[2],b[2]),2),round(max(a[2],b[2]),2)))
        else:
            D[(round(min(a[2],b[2]),1),round(max(a[2],b[2]),1))].append((rw(a[1]),rw(b[1]),ax(a[0]),ax(b[0])))
    if V:
        byrow=collections.defaultdict(lambda: collections.defaultdict(list))
        for (r,x),segs in V.items():
            zr=(round(min(z for z,_ in segs),2),round(max(z for _,z in segs),2))
            byrow[(r,zr)][0].append(x)
        for (r,zr),dd in sorted(byrow.items()): o.write(f'   V row {r} z {zr}: axes {comp(dd[0])}\n')
    for (r,z),segs in sorted(X.items()):
        o.write(f'   X row {r} z~{z}: x {min(a for a,_ in segs):.1f}..{max(b for _,b in segs):.1f} ({len(segs)} el)\n')
    ys=collections.defaultdict(list)
    for x,segs in Y.items():
        key=(round(min(s[0] for s in segs),1),round(max(s[1] for s in segs),1),min(s[2] for s in segs),max(s[3] for s in segs))
        ys[key].append(x)
    for key,axl in sorted(ys.items()): o.write(f'   Y y {rw(key[0])}..{rw(key[1])} z {key[2]}..{key[3]}: axes {comp(axl)}\n')
    for z,l in sorted(D.items()):
        rows=collections.Counter((a,b) for a,b,_,_ in l); axs=sorted(set(c for _,_,c,_ in l)|set(c for _,_,_,c in l),key=lambda s:(len(s),s))
        o.write(f'   D z {z}: n={len(l)} rows {dict(rows)} axes {comp(axs)[:150]}\n')
    for k,v in PL.items(): o.write(f'   PL z {k}: {v}\n')
