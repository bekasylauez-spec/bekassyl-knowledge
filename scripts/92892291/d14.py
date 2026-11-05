import axes,sys
from collections import Counter
s=sys.argv[1]; X,Y,_,_=axes.axes(s); x1,yA=X[0],Y[0]
c=Counter()
for e in axes.E():
    if not axes.ins(e,s) or e.dxf in('SPDSCONSTRUCTIONLINE',): continue
    r=[e.bb[0]-x1,e.bb[1]-yA,e.bb[2]-x1,e.bb[3]-yA]
    if r[0]>4000 and r[2]<8000 and r[1]>-1500 and r[3]<7500:
        print(e.h,e.dxf,e.lay,[round(v) for v in r],e.info[:60])
