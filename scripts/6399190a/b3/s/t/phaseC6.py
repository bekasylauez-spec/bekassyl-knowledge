import ab,os,ext,math
E={e.h:e for e in ext.load('w/ext.txt')}
C1=(-1578179.088,-1777639.836); C2=(-1567619.75,-1777639.836)
def C(h): return C1 if E[h].cx<-1573000 else C2
rmap={2500:3500,1900:2900,2100:3100,1840:2840,2060:3060,2180:3180}
def mapy(c,y):
    d=y-c[1]; s=1 if d>0 else -1
    for a,b in rmap.items():
        if abs(abs(d)-a)<3: return c[1]+s*b
    return y
O=[]
# circles
for h,r in (('3C5050',2900),('3C5051',2840),('3C50ED',3060),('3C50B2',2900),('3C50B3',2840),('3C50EF',3100),('3C50F0',3180)):
    O.append({'t':'erase','h':[h]}); O.append({'t':'circle','c':list(C(h)),'r':r,'layer':'Размеры'})
O.append({'t':'circle','c':list(C1),'r':3500,'layer':'Размеры','lw':30})
O.append({'t':'erase','h':['3C504F']})
# bar blocks
for h in ('3C508C','3C50D0'): O.append({'t':'scalegrp','h':[h],'base':list(C(h)),'s':2840/1840})
# rotated dims
for h in ('3C5052','3C5061','3C5070','3C507F','3C50B4','3C50C3'):
    p=E[h].dimpts(); c=C(h)
    p1,p2,dl=p[0],p[1],p[2]
    O.append({'t':'dimpts','h':h,'p1':[p1[0],mapy(c,p1[1])],'p2':[p2[0],mapy(c,p2[1])],'dl':[dl[0],mapy(c,dl[1])]})
# aligned diameter dims
k=2840/1840
for h in ('3C50A3','3C50E2'):
    c=C(h); sp=E[h].sp
    q=[[c[0]+(x-c[0])*k,c[1]+(y-c[1])*k] for x,y in sp[:3]]
    O.append({'t':'dimpts','h':h,'p1':q[0],'p2':q[1],'dl':q[0]})
# note arrows on circles
for h in ('3C50B0','3C50B1','3C50EB','3C50EC','3C50EE','3C50F1','3C50F2'):
    c=C(h)
    for i,(x,y) in enumerate(E[h].sp):
        r=math.hypot(x-c[0],y-c[1])
        if 1700<r<2300:
            O.append({'t':'movept','h':h,'idx':i,'d':[(x-c[0])/r*1000,(y-c[1])/r*1000]})
O.append({'t':'dimtext','h':'3C4ACE','s':'700'}); O.append({'t':'dimtext','h':'3C4ABE','s':'580'})
O.append({'t':'txtrep','win':[-1612253,-1799222,-1552753,-1757122],'pairs':[['(∅}5{','(∅}7{'],['∅400мм','∅700мм'],['L=9500)','L=9500)']]})
O.append({'t':'mcrep','win':[-1612253,-1799222,-1552753,-1757122],'pairs':[['∅368','∅568'],['%%C368','%%C568']]})
O.append({'t':'save'})
ab.run(O,'C6'); print(open(os.environ['TEMP']+'/ab_log.txt',encoding='utf-8').read()[-500:])
