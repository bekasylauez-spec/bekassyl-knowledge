import sys
X0,X1=float(sys.argv[1]),float(sys.argv[2])
for l in open(r'D:/_claude_work/zavod_km_uz/plates/geom.txt',encoding='utf-8-sig'):
    p=l.split()
    if not p or p[0] not in('PL','LN'): continue
    pts=[tuple(map(float,q.split(','))) for q in p[2:] if ',' in q]
    if not pts: continue
    xs=[a for a,b in pts]
    if X0<=min(xs)<=X1:
        print(p[0],p[1],' '.join('%g,%g'%(a-X0,b+274650) for a,b in pts))
