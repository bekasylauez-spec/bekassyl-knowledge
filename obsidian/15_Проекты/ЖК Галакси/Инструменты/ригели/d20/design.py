import json, math, collections
E=json.load(open('py/env.json',encoding='utf-8'))
A=lambda d:math.pi*d*d/400; a20=A(20); MAIN=4*a20; ANCH=1220
# beam bar extents (scheme u, mm): main bars run END0+20 .. END1-20
ENDS={'Рм-1':(-125,20175),'Рм-2':(-125,20175),'Рм-3':(-125,20175),'Рм-4':(-3275,125),'Рм-5':(23050,31175)}
def envelope(mk):
    env=collections.defaultdict(lambda:[0,0,0])
    for u,b,t,w,z,ax in E[mk]:
        r=env[u]; r[0]=max(r[0],b); r[1]=max(r[1],t); r[2]=max(r[2],w)
    return env
def pieces(mk,k,extra_bars):
    """bars beyond 'extra_bars' already counted; returns pieces [u0,u1,n] where need>MAIN+extra_bars*a20"""
    env=envelope(mk); us=sorted(env); base=MAIN+extra_bars*a20
    e0,e1=ENDS[mk]; lo,hi=e0+20,e1-20
    segs=[]
    for u in us:
        v=env[u][k]
        if v>base+1e-6:
            n=math.ceil((v-base)/a20-1e-9)
            segs.append([max(lo,u-ANCH),min(hi,u+ANCH),n])
    segs.sort(); out=[]
    for s in segs:
        if out and s[0]<=out[-1][1]: out[-1][1]=max(out[-1][1],s[1]); out[-1][2]=max(out[-1][2],s[2])
        else: out.append(s)
    return out
def rnd(p,lo,hi):
    a=math.floor(p[0]/10)*10; b=math.ceil(p[1]/10)*10
    return [max(a,lo),min(b,hi),p[2]]
D={}
for mk in E:
    e0,e1=ENDS[mk]; lo,hi=e0+20,e1-20
    top=[rnd(p,lo,hi) for p in pieces(mk,1,0)]
    bot=[rnd(p,lo,hi) for p in pieces(mk,0,0)]
    D[mk]=dict(top=top,bot=bot)
    print(mk,'top',[(a,b,b-a,n) for a,b,n in top]); print('   bot',[(a,b,b-a,n) for a,b,n in bot])
# Рм-5 top second row: where need > 4+3 bars
p2=[rnd(p,23070,31155) for p in pieces('Рм-5',1,3)]
print('Рм-5 top 2nd row', [(a,b,b-a,n) for a,b,n in p2])
json.dump(D,open('py/design.json','w',encoding='utf-8'),ensure_ascii=False)
