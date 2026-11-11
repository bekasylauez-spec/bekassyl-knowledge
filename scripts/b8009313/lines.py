import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8")
import ezdxf,collections
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
c=collections.Counter()
for e in m.query('LINE'):
    if e.dxf.layer=='Несущие колонны':
        if abs(e.dxf.start.y-e.dxf.end.y)<1 and abs(e.dxf.start.x-e.dxf.end.x)<=60.5:
            c[(int(e.dxf.start.x//14850), round(e.dxf.start.y))]+=1
for k in sorted(c): print(k,c[k])
