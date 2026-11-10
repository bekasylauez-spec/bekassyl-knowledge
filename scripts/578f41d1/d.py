import sys
X0,X1=float(sys.argv[1]),float(sys.argv[2])
bb={}
for l in open(r'D:/_claude_work/zavod_km_uz/plates/list.txt',encoding='utf-8-sig'):
    f=l.rstrip('\n').split('\t')
    if len(f)>2: bb[f[2]]=f[-1]
for l in open(r'D:/_claude_work/zavod_km_uz/plates/geom.txt',encoding='utf-8-sig'):
    p=l.split()
    if p and p[0]=='DIM':
        e=bb.get(p[1],'')
        try: a=list(map(float,e[1:].split(',')))
        except: continue
        if X0<=a[0]<=X1:
            m=[q for q in p if q.startswith('meas') or q.startswith('txt')]
            print(p[1],' '.join(m),'bb=%d,%d..%d,%d'%(a[0]-X0,a[1]+274650,a[2]-X0,a[3]+274650))
