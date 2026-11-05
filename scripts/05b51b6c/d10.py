import ext,json,sys
from collections import Counter
SH=json.load(open('sheets.json'))
E=ext.load('w/ext.txt')
s=sys.argv[1]; a,b,c,d=SH[s]
I=[e for e in E if e.bb and a<=e.cx<=c and b<=e.cy<=d]
print(Counter((e.dxf,e.lay) for e in I).most_common(40))
L=float(sys.argv[2]) if len(sys.argv)>2 else 5000
for e in I:
    if e.dxf in ('LWPOLYLINE','LINE','SPDSCONSTRUCTIONLINE') and max(e.bb[2]-e.bb[0],e.bb[3]-e.bb[1])>L:
        print(e.h,e.dxf,e.lay,[round(v) for v in e.bb],e.info[-60:])
