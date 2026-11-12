import ezdxf,sys
sys.stdout.reconfigure(encoding='utf-8')
from ezdxf.recover import readfile
doc=ezdxf.readfile(r'D:\_claude_work\otst\src\analog.dxf')
X0=-41822+59400*int(sys.argv[1]);Y0=-1593693
for h in sys.argv[2:]:
    e=doc.entitydb[h]
    if e.dxftype()=='LWPOLYLINE':
        print(h,e.dxf.layer,'cw',e.dxf.const_width,'closed',e.closed,[(round(x-X0,1),round(y-Y0,1),round(b,4)) for x,y,s,ee,b in e.get_points('xyseb')])
    elif e.dxftype()=='LINE': print(h,'LINE',round(e.dxf.start.x-X0,1),round(e.dxf.start.y-Y0,1),round(e.dxf.end.x-X0,1),round(e.dxf.end.y-Y0,1))
    else: print(h,e.dxftype())
