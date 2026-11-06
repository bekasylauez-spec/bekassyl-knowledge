import axes,grid,ab,os,sys
from shapely.geometry import box
from shapely.ops import unary_union
pads=unary_union([box(6000*i-1000,6000*j-1000,6000*i+1000,6000*j+1000) for i in range(11) for j in range(3)])
st=[box(0,5750,60000,6250)]+[box(6000*i-250,0,6000*i+250,12000) for i in range(1,10)]
NU=unary_union([pads]+st)
s='2.1'; X,Y,_,_=axes.axes(s); x1,yA=X[0],Y[0]
old=[e.h for e in axes.E() if axes.ins(e,s) and e.dxf=='LWPOLYLINE' and e.lay=='Размеры' and len(e.plpts())>=4 and grid.on([(p[0]-x1,p[1]-yA) for p in e.plpts()],pads)]
print(len(old))
O=[]
for i,r in enumerate(grid.rings(NU)):
    O.append({'t':'clone','h':old[0],'tag':'g21_%d'%i}); O.append({'t':'plset','h':'g21_%d'%i,'p':[[x+x1,y+yA] for x,y in r],'closed':True})
O.append({'t':'erase','h':old}); O.append({'t':'save'})
print(len(grid.rings(NU)))
if len(sys.argv)>1: ab.run(O,'B5'); print(open(os.environ['TEMP']+'/ab_log.txt',encoding='utf-8').read()[-150:])
