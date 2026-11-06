import json, collections
def load(p='py/asbar.csv'):
    R=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0,0]))
    for l in open(p,'rb').read().decode('utf-8','replace').splitlines()[1:]:
        f=l.split(';')
        if len(f)<21 or f[1].endswith('-S'): continue
        try: el=int(f[4]); s=int(f[5]); v=[float(x or 0) for x in f[10:21]]
        except ValueError: continue
        au1,au2,au3,au4,as1,as2,as3,as4,pc,w1,w2=v
        r=R[el][s]; r[0]=max(r[0],au1+au2+as1); r[1]=max(r[1],au3+au4+as2); r[2]=max(r[2],w1,w2)
    return R
R=load(); B=json.load(open('py/beams.json'))
print('beam els with data', sum(1 for i,_,_ in B if i in R))
# marks: (name, test(p,q)->bool, coord fn -> facade-local u (mm, LIRA-based scheme coordinate))
def ymap(y): return y*1000 if y<=8.0 else y*1000+5000
MK={'Рм-1':lambda p,q:abs(p[1]+0.975)<1e-3 and abs(q[1]+0.975)<1e-3,
    'Рм-2':lambda p,q:abs(p[1]-18.275)<1e-3 and abs(q[1]-18.275)<1e-3,
    'Рм-3':lambda p,q:abs(p[1]-23.825)<1e-3 and abs(q[1]-23.825)<1e-3,
    'Рм-4':lambda p,q:abs(p[0]-q[0])<1e-3 and max(p[1],q[1])<=0.0+1e-3,
    'Рм-5':lambda p,q:abs(p[0]-q[0])<1e-3 and min(p[1],q[1])>=18.275-1e-3}
out={}
for mk,f in MK.items():
    pts=[]
    for i,p,q in B:
        if not f(p,q) or i not in R: continue
        alongx = abs(p[1]-q[1])<1e-3
        a=(p[0]*1000 if alongx else ymap(p[1])); b=(q[0]*1000 if alongx else ymap(q[1]))
        secs=sorted(R[i]); n=len(secs)
        for s in secs:
            u=a+(b-a)*(s-1)/(n-1) if n>1 else (a+b)/2
            bot,top,asw=R[i][s]; pts.append((round(u),bot,top,asw,p[2],p[0] if not alongx else p[1]))
    pts.sort(); out[mk]=pts
    print(mk, len(pts), 'max bot %.2f top %.2f asw %.2f'%(max(x[1] for x in pts),max(x[2] for x in pts),max(x[3] for x in pts)))
json.dump(out,open('py/env.json','w',encoding='utf-8'),ensure_ascii=False)
