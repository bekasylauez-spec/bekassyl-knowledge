import ezdxf,sys,math
doc=ezdxf.readfile(sys.argv[1]); msp=doc.modelspace()
out=open('an3.txt','w',encoding='utf-8')
# title positions of foundation formwork sheets (sheet frames width ~ 42000? A3 at 1:100 = 42000x29700)
titles={'T1':(1600051,1190452),'T2':(1962151,1190452),'T3':(2325544,1190290)}
for k,(tx,ty) in titles.items():
    out.write(f'== {k}\n')
    for e in msp.query('LWPOLYLINE'):
        pts=list(e.get_points('xy'))
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        if not(tx-25000<min(xs) and max(xs)<tx+25000 and ty-30000<min(ys) and max(ys)<ty+2000): continue
        if len(pts)<4: continue
        per=sum(math.dist(pts[i],pts[(i+1)%len(pts)]) for i in range(len(pts) if e.closed else len(pts)-1))
        w=max(xs)-min(xs); h=max(ys)-min(ys)
        if w<3000 and h<3000: continue
        out.write(f'{e.dxf.handle}\t{e.dxf.layer}\tclosed={e.closed}\tn={len(pts)}\tW={w:.0f}\tH={h:.0f}\tper={per:.0f}\tbox=({min(xs):.0f},{min(ys):.0f})\n')
