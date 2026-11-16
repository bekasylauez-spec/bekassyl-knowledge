import ezdxf,collections
doc=ezdxf.readfile(r'D:\_claude_work\RMC\ar\ARCH_copy.dxf')
msp=doc.modelspace()
c=collections.Counter()
for e in msp:
    t=e.dxftype()
    try:
        if t=='LINE': x,y=e.dxf.start.x,e.dxf.start.y
        elif t=='LWPOLYLINE': x,y=e.get_points('xy')[0]
        elif t in('INSERT','TEXT','CIRCLE','HATCH'): 
            x,y=(e.dxf.insert.x,e.dxf.insert.y) if t in('INSERT','TEXT') else ((e.dxf.center.x,e.dxf.center.y) if t=='CIRCLE' else (None,None))
        else: continue
    except: continue
    if x is None: 
        c[(ascii(e.dxf.layer),t)]+=0; continue
    if 996959<=x<=1102059 and 341712<=y<=401112: c[(ascii(e.dxf.layer),t)]+=1
for k,v in sorted(c.items()): print(k,v)
