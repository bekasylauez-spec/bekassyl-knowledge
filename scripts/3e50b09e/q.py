import ezdxf,sys
doc=ezdxf.readfile(r'D:\_claude_work\RMC\ar\ARCH_copy.dxf')
msp=doc.modelspace()
x0,x1,y0,y1=[float(v) for v in sys.argv[1:5]]
skip=set(sys.argv[5].split(',')) if len(sys.argv)>5 else set()
for e in msp:
    t=e.dxftype()
    if e.dxf.layer in skip: continue
    try:
        if t=='LWPOLYLINE': p=list(e.get_points('xy'))
        elif t=='LINE': p=[(e.dxf.start.x,e.dxf.start.y),(e.dxf.end.x,e.dxf.end.y)]
        else: continue
    except: continue
    if p and all(x0<=a<=x1 and y0<=b<=y1 for a,b in p):
        print(t,e.dxf.layer,e.dxf.get('linetype',''),[(round(a),round(b)) for a,b in p][:6])
