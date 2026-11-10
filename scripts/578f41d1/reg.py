import sys
from g import G,bb
x0,y0,x1,y1=map(float,sys.argv[1:5])
for k,h,pts in G:
    b=bb(pts)
    if b[0]>=x0 and b[2]<=x1 and b[1]>=y0 and b[3]<=y1:
        print(k,h,'%.0fx%.0f'%(b[2]-b[0],b[3]-b[1]),' '.join('%.0f,%.0f'%q for q in pts[:14]))
