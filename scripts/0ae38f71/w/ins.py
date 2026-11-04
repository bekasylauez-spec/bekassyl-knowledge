import ezdxf
doc=ezdxf.readfile('live2.dxf'); msp=doc.modelspace()
for e in msp:
    p=None
    for a in ('insert','location','start','center','defpoint'):
        if e.dxf.hasattr(a): p=e.dxf.get(a); break
    if p is None: continue
    if 2827300<p[0]<2833500 and 1828100<p[1]<1832000 and e.dxftype() not in ('TEXT','MTEXT','LWPOLYLINE','MULTILEADER'):
        print(e.dxftype(), e.dxf.handle, e.dxf.get('name',''), tuple(round(v) for v in p))
