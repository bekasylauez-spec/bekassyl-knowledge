import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8")
import ezdxf
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
lay=sys.argv[2]
for e in m:
    if e.dxf.layer==lay or e.dxftype()==lay:
        if e.dxftype()=='INSERT': print(e.dxf.handle,'INS',e.dxf.name,round(e.dxf.insert.x,1),round(e.dxf.insert.y,1),round(e.dxf.rotation,1),e.dxf.xscale)
        elif e.dxftype()=='LINE': print(e.dxf.handle,'LINE',[round(v,1) for v in (*e.dxf.start.vec2,*e.dxf.end.vec2)])
        elif e.dxftype()=='LWPOLYLINE': print(e.dxf.handle,'PL',[(round(p[0],1),round(p[1],1)) for p in e.get_points()][:8])
        else: print(e.dxf.handle,e.dxftype())
