import ezdxf,sys
d=ezdxf.readfile(sys.argv[1]);msp=d.modelspace()
x0,y0,x1,y1=map(float,sys.argv[2:6])
for e in msp:
    t=e.dxftype()
    if t=='DIMENSION':
        p=e.dxf.defpoint
        if x0<p.x<x1 and y0<p.y<y1:
            try: m=e.get_measurement()
            except Exception: m=None
            print('DIM',round(p.x),round(p.y),e.dxf.text,round(m,1) if isinstance(m,float) else m)
    elif t in('TEXT','MTEXT'):
        p=e.dxf.insert
        if x0<p.x<x1 and y0<p.y<y1: print(t,round(p.x),round(p.y),(e.dxf.text if t=='TEXT' else e.plain_text())[:40])
