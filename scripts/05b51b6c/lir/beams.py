import json,collections,math
m=json.load(open('model.json'));N=m['nodes'];NM={int(k):v for k,v in m['names'].items()}
def runs(zlo,zhi,stiffs):
    segs=collections.defaultdict(list)
    for e in m['els']:
        if e['s'] not in stiffs or len(e['n'])!=2: continue
        a,b=[N[j] for j in e['n'][:2]]
        if not(zlo<=a[2]<=zhi and zlo<=b[2]<=zhi): continue
        if abs(a[0]-b[0])<1e-3 and abs(a[1]-b[1])<1e-3: continue
        if abs(a[1]-b[1])<1e-3: key=('X',round(a[1],3)); s=sorted([a[0],b[0]])
        elif abs(a[0]-b[0])<1e-3: key=('Y',round(a[0],3)); s=sorted([a[1],b[1]])
        else: key=('D',0); s=[0,0]
        segs[(e['s'],)+key].append(tuple(round(v,3) for v in s))
    out=[]
    for k,L in segs.items():
        L.sort(); cur=list(L[0])
        for s in L[1:]:
            if s[0]<=cur[1]+1e-3: cur[1]=max(cur[1],s[1])
            else: out.append((k,tuple(cur))); cur=list(s)
        out.append((k,tuple(cur)))
    return sorted(out,key=lambda r:(r[0][1],r[0][2],r[1][0]))
if __name__=='__main__':
    for lev,(lo,hi) in (('6.2',(5.5,6.3)),('11.4',(11.3,11.5)),('found',(-1.1,-0.9))):
        print('==',lev)
        for k,s in runs(lo,hi,set(range(3,22))):
            print('  %-14s %s=%6.2f  %6.2f..%6.2f  L=%.2f'%(NM[k[0]],k[1],k[2],s[0],s[1],s[1]-s[0]))
