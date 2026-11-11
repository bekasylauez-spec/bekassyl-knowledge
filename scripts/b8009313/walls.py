import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8")
import ezdxf
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
for e in m.query('LWPOLYLINE'):
    p=e.get_points()
    if len(p)>=6:
        xs=[q[0] for q in p]; ys=[q[1] for q in p]
        if max(xs)-min(xs)>5000 and 1000<max(ys)-min(ys)<2500 or (max(ys)-min(ys)>5000 and 1000<max(xs)-min(xs)<2500):
            print(e.dxf.handle,e.dxf.layer,len(p),'closed' if e.closed else 'open','X',sorted(set(round(x,1) for x in xs))[:3],'..','Y',sorted(set(round(y,1) for y in ys)))
