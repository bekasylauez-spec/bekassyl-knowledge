import ezdxf,sys
from ezdxf import bbox
S=r'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\0c44a278-d609-485d-a50c-02efd03030b0\scratchpad\w'
d=ezdxf.readfile(S+'//'+sys.argv[1]); m=d.modelspace()
x0,y0,x1,y1=map(float,sys.argv[2:6]); skip=sys.argv[6].split(',') if len(sys.argv)>6 else []
for e in m:
    if e.dxf.layer in skip: continue
    try: b=bbox.extents([e],fast=True)
    except: continue
    if not b.has_data: continue
    if b.extmax.x>=x0 and b.extmin.x<=x1 and b.extmax.y>=y0 and b.extmin.y<=y1 and b.size.x<30000:
        t=e.dxftype(); s=''
        if t=='LINE': s='%s -> %s lw%s'%(tuple(round(v) for v in e.dxf.start)[:2],tuple(round(v) for v in e.dxf.end)[:2],e.dxf.lineweight)
        elif t=='DIMENSION':
            s='dt%s %r meas=%.0f p1=%s p2=%s dl=%s tp=%s blk=%s'%(e.dxf.dimtype,e.dxf.text,e.get_measurement(),tuple(round(v) for v in e.dxf.defpoint2)[:2],tuple(round(v) for v in e.dxf.defpoint3)[:2],tuple(round(v) for v in e.dxf.defpoint)[:2],tuple(round(v) for v in e.dxf.text_midpoint)[:2],e.dxf.geometry)
            ov=e.get_overridden_dimstyle_values() if hasattr(e,'get_overridden_dimstyle_values') else None
        elif t=='MULTILEADER':
            c=e.context; s='txt=%r tl=%s leaders=%s'%(c.mtext.default_content if c.mtext else None, tuple(round(v) for v in c.mtext.insert)[:2] if c.mtext else None, [[tuple(round(v) for v in p)[:2] for p in ln.vertices] + [tuple(round(v) for v in ln.vertices[-1])[:2] if False else ()] for l in c.leaders for ln in l.lines])
            s+=' lroots=%s'%[ (tuple(round(v) for v in l.last_leader_point)[:2]) for l in c.leaders]
        elif t in('TEXT','MTEXT'): s='%r at %s'%((e.dxf.text if t=='TEXT' else e.text)[:40],tuple(round(v) for v in e.dxf.insert)[:2])
        elif t=='LWPOLYLINE': s=str([tuple(round(v) for v in p[:2]) for p in e.get_points()][:6])
        elif t=='INSERT': s='%s at %s'%(e.dxf.name,tuple(round(v) for v in e.dxf.insert)[:2])
        print(t,e.dxf.layer,e.dxf.handle,s)
