# final rigel layout (scheme u, mm). dop: pos, side, n, u0, u1, hook0, hook1 (90° 12d=240 into support)
import json, math, collections
HK=240
L={
 'Рм-1':[('2','top',2,-105,2420,True,False),('3','top',2,4505,9295,False,False),('3','top',2,10960,15750,False,False),('2','top',2,17630,20155,False,True)],
 'Рм-2':[('3','top',2,5730,8920,False,False),('3','top',2,11730,14920,False,False),('2','top',2,17100,20155,False,True)],
 'Рм-3':[('2','top',3,-105,2020,True,False),('3','top',3,5100,9040,False,False),('3','top',3,11130,15070,False,False),('2','top',3,18030,20155,False,True)],
 'Рм-4':[('2','top',3,-3255,105,False,True)],
 'Рм-5':[('2','top',3,26230,30600,False,False),('4','top',4,26730,29750,False,False),('3','bot',3,23070,26090,True,False)],
}
if __name__=='__main__':
    E=json.load(open('py/env.json',encoding='utf-8'))
    A=lambda d:math.pi*d*d/400; a=A(20); ANCH=1220
    tab=[]
    for mk,pts in E.items():
        env=collections.defaultdict(lambda:[0,0,0])
        for u,b,t,w,z,ax in pts:
            r=env[u]; r[0]=max(r[0],b); r[1]=max(r[1],t)
        bad=[]; mx={'top':(0,0),'bot':(0,0)}
        for u,(b,t,_) in env.items():
            for side,need in (('bot',b),('top',t)):
                have=4*a
                for p,s,n,u0,u1,h0,h1 in L[mk]:
                    if s==side and (u0 if h0 else u0+ANCH)<=u<=(u1 if h1 else u1-ANCH): have+=n*a
                if need>have+1e-6: bad.append((u,side,need,round(have,2)))
                if need>mx[side][0]: mx[side]=(need,have)
        print(mk,'bad',len(bad),bad[:5],'gov top %.2f/%.2f bot %.2f/%.2f'%(mx['top'][0],mx['top'][1],mx['bot'][0],mx['bot'][1]))
        tab.append((mk,mx))
    json.dump({k:[list(x) for x in v] for k,v in L.items()},open('py/layout.json','w',encoding='utf-8'),ensure_ascii=False)
