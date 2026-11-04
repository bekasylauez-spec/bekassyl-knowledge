import sys
from shapely.geometry import box
from shapely.ops import unary_union
f,x0,y0,w,h,ycut=sys.argv[1],*map(float,sys.argv[2:7])
B=[]
for l in open(f,encoding='utf-8-sig'):
    a=l.rstrip('\n').split('\t')
    if len(a)<7: continue
    X0,Y0,X1,Y1=map(float,a[3:7])
    if X0>=x0-10 and X1<=x0+w+10 and Y0>=y0-h-10 and Y1<=y0-ycut and (X1-X0)<w*0.9:
        B.append((box(X0,Y0,X1,Y1).buffer(600),a))
U=unary_union([b for b,_ in B])
for g in (U.geoms if hasattr(U,'geoms') else [U]):
    bb=g.buffer(-600).bounds
    txt=[a[8][:30] for b,a in B if b.intersects(g) and a[8]][:4]
    print([round(v-o) for v,o in zip(bb,(x0,y0,x0,y0))], txt)
