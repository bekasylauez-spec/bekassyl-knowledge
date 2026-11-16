import ezdxf,sys
doc=ezdxf.readfile(r'D:\_claude_work\RMC\ar\ARCH_copy.dxf')
msp=doc.modelspace()
want=sys.argv[1].split(',')
for e in msp:
    L=e.dxf.layer
    if L not in want: continue
    t=e.dxftype()
    if t=='LWPOLYLINE': p=[(round(a),round(b)) for a,b in e.get_points('xy')]
    elif t=='LINE': p=[(round(e.dxf.start.x),round(e.dxf.start.y)),(round(e.dxf.end.x),round(e.dxf.end.y))]
    elif t=='INSERT': p=[(round(e.dxf.insert.x),round(e.dxf.insert.y)),e.dxf.name]
    else: p=t
    if t=='LWPOLYLINE' and len(p)>12: p=p[:6]
    if isinstance(p,list) and p and isinstance(p[0],tuple) and not (996959<=p[0][0]<=1102059 and 341712<=p[0][1]<=401112): continue
    print(t,ascii(L),p)
