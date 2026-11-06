import axes
s='3.4'; X,Y,_,_=axes.axes(s); x1,yA=X[0],Y[0]
for e in axes.E():
    if not axes.ins(e,s): continue
    r=[e.bb[0]-x1,e.bb[1]-yA,e.bb[2]-x1,e.bb[3]-yA]
    if (r[0]>-2000 and r[2]<6500 and r[1]>-3000 and r[3]<900) or (r[0]>-3000 and r[2]<900 and r[1]>-500 and r[3]<12500):
        if e.dxf=='SPDSCONSTRUCTIONLINE': continue
        print(e.h,e.dxf,e.lay,[round(v) for v in r],e.kv.get('txt','')[:20])
