import ezdxf,sys
doc=ezdxf.readfile('D:/_claude_work/maftun/src/fv.dxf'); msp=doc.modelspace()
x0,x1,y0,y1=map(float,sys.argv[1:5])
for e in msp:
    t=e.dxftype()
    try:
        if t=='LINE': pts=[tuple(e.dxf.start)[:2],tuple(e.dxf.end)[:2]]
        elif t=='LWPOLYLINE': pts=[tuple(p[:2]) for p in e.get_points()]
        elif t=='CIRCLE': pts=[tuple(e.dxf.center)[:2]]
        else: continue
    except: continue
    if any(x0<=p[0]<=x1 and y0<=p[1]<=y1 for p in pts):
        print(t,e.dxf.layer,e.dxf.get('lineweight'),[(round(a,1),round(b,1)) for a,b in pts][:6], e.closed if t=='LWPOLYLINE' else '')
