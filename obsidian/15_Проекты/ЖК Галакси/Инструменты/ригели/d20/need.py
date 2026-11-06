import json, math, collections
E=json.load(open('py/env.json',encoding='utf-8'))
A=lambda d:math.pi*d*d/400
MAIN=4*A(20)
for mk,pts in E.items():
    env=collections.defaultdict(lambda:[0,0,0])
    for u,b,t,w,z,ax in pts:
        r=env[u]; r[0]=max(r[0],b); r[1]=max(r[1],t); r[2]=max(r[2],w)
    us=sorted(env)
    print('==',mk, 'u %d..%d'%(us[0],us[-1]))
    for k,name in ((1,'top'),(0,'bot')):
        segs=[];cur=None
        for u in us:
            v=env[u][k]
            if v>MAIN+1e-6:
                if cur is None: cur=[u,u,v]
                else: cur[1]=u; cur[2]=max(cur[2],v)
            elif cur: segs.append(cur); cur=None
        if cur: segs.append(cur)
        print(' ',name, [(a,b,round(m,2),round(m-MAIN,2)) for a,b,m in segs])
