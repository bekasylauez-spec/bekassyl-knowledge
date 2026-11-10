import ezdxf,collections,sys
sys.stdout.reconfigure(encoding='utf-8')
d=ezdxf.readfile("D:/_claude_work/v113/ozh/ozh_km.dxf")
msp=d.modelspace()
for e in msp:
    if e.dxftype()=='LINE':
        a,b=e.dxf.start,e.dxf.end
        L=abs(a.x-b.x)+abs(a.y-b.y)
        if L>20000 and 300000<a.x<460000 and a.y<120000: print('LINE',e.dxf.layer,round(a.x),round(a.y),round(b.x),round(b.y))
    if e.dxftype()=='LWPOLYLINE':
        p=list(e.get_points('xy'))
        xs=[q[0] for q in p];ys=[q[1] for q in p]
        if 300000<min(xs)<460000 and max(ys)<125000 and max(xs)-min(xs)>5000 and max(ys)-min(ys)>5000: print('LW',e.dxf.layer,round(min(xs)),round(min(ys)),round(max(xs)),round(max(ys)),len(p))
