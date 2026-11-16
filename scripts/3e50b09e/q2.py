import ezdxf,sys
doc=ezdxf.readfile(r'D:\_claude_work\RMC\ar\ARCH_copy.dxf')
msp=doc.modelspace()
x0,x1,y0,y1=[float(v) for v in sys.argv[1:5]]
skip=set(sys.argv[5].split(',')) if len(sys.argv)>5 else set()
for e in msp:
    t=e.dxftype(); L=e.dxf.layer
    if L in skip: continue
    try:
        if t=='LWPOLYLINE': p=[(a,b) for a,b in e.get_points('xy')]
        elif t=='LINE': p=[(e.dxf.start.x,e.dxf.start.y),(e.dxf.end.x,e.dxf.end.y)]
        elif t=='INSERT': p=[(e.dxf.insert.x,e.dxf.insert.y)]
        elif t=='HATCH':
            p=[]
            for pa in e.paths:
                if hasattr(pa,'vertices'): p+= [(v[0],v[1]) for v in pa.vertices]
                else:
                    for ed in pa.edges:
                        if hasattr(ed,'start'): p.append((ed.start[0],ed.start[1]))
        else: continue
    except Exception as ex: continue
    if not p: continue
    xs=[a for a,b in p]; ys=[b for a,b in p]
    if max(xs)>=x0 and min(xs)<=x1 and max(ys)>=y0 and min(ys)<=y1:
        extra=e.dxf.name if t=='INSERT' else (e.dxf.pattern_name if t=='HATCH' else '')
        print(t,ascii(L),ascii(extra),[(round(a),round(b)) for a,b in p][:8])
