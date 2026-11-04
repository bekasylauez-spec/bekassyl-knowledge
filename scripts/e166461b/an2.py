import ezdxf, sys
from ezdxf import bbox
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
print(bbox.extents(m, fast=True))
for e in m:
    t=e.dxftype()
    if t=='INSERT':
        b=d.blocks.get(e.dxf.name); n=len(b) if b else 0
        print('INS',e.dxf.handle,e.dxf.name,e.dxf.layer,[round(x) for x in e.dxf.insert][:2],round(e.dxf.xscale,3),round(e.dxf.rotation,1),n, [ (a.dxf.tag,a.dxf.text) for a in e.attribs][:6])
    elif t=='MTEXT': print('MT',e.dxf.handle,[round(x) for x in e.dxf.insert][:2],e.dxf.char_height,repr(e.text[:200]))
    elif t=='LWPOLYLINE':
        p=e.get_points('xy'); xs=[q[0] for q in p]; ys=[q[1] for q in p]
        print('PL',e.dxf.handle,e.dxf.layer,len(p),e.closed,round(min(xs)),round(min(ys)),round(max(xs)),round(max(ys)),e.dxf.get('const_width'), e.dxf.color)
    elif t=='ACAD_PROXY_ENTITY':
        bb=bbox.extents([e],fast=True)
        print('PX',e.dxf.handle,e.dxf.layer,'' ,bb.extmin if bb.has_data else None, bb.extmax if bb.has_data else None)
    elif t=='HATCH': print('HA',e.dxf.handle,e.dxf.pattern_name,len(e.paths))
    elif t=='LINE': print('LN',e.dxf.start,e.dxf.end)
    elif t=='ACAD_TABLE': print('TB',e.dxf.handle,e.dxf.insert)
