import re,math,sys
D="D:/_claude_work/zavod_km_uz/plates/"
G=[]
for ln in open(D+'geom.txt',encoding='utf-8-sig'):
    p=ln.split()
    if p[0] in('PL','LN'):
        pts=[tuple(map(float,q.split(','))) for q in p[2:] if ',' in q]
        G.append((p[0],p[1],pts))
def dseg(P,A,B):
    ax,ay=A;bx,by=B;px,py=P
    dx,dy=bx-ax,by-ay;L=dx*dx+dy*dy
    t=0 if L==0 else max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L))
    return math.hypot(ax+t*dx-px,ay+t*dy-py)
def near(P,r=4):
    out=[]
    for k,h,pts in G:
        d=min(dseg(P,pts[i],pts[i+1]) for i in range(len(pts)-1)) if len(pts)>1 else 1e9
        if d<=r: out.append((d,k,h,pts))
    return sorted(out)
def bb(pts):
    xs=[p[0] for p in pts];ys=[p[1] for p in pts]
    return min(xs),min(ys),max(xs),max(ys)
if __name__=='__main__':
    for ln in open(D+'notes.txt',encoding='utf-8-sig'):
        f=ln.rstrip('\n').split('\t')
        if not f[3].startswith('-t'): continue
        e=[x for x in f if x.startswith('E')][0]
        x=float(e[1:].split(',')[0])
        sh=[n for a,b,n in [(2894065,2898265,25),(2915065,2919265,28),(3681900,3686100,38)] if a<=x<=b]
        if not sh: continue
        pts=[tuple(map(float,q.split(','))) for q in f[9:] if ',' in q and not q.startswith('E')]
        print('=== sheet',sh[0],f[1],f[3],f[4].encode('cp1252','replace') if 0 else '', 'shelf',pts[0])
        for A in pts[1:]:
            print('  arrow',A)
            for d,k,h,pp in near(A):
                b=bb(pp)
                print('    %.1f %s %s n=%d bbox %.0f..%.0f x %.0f..%.0f (%.0fx%.0f) '%(d,k,h,len(pp),b[0],b[2],b[1],b[3],b[2]-b[0],b[3]-b[1]),' '.join('%.0f,%.0f'%q for q in pp[:12]))
