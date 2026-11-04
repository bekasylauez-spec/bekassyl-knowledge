import ezdxf,sys
d=ezdxf.readfile(sys.argv[1]);msp=d.modelspace()
heads=[];dims=[]
for e in msp:
    t=e.dxftype()
    if t=='MTEXT' and 'Разрез 1 - 1' in e.plain_text(): heads.append((e.dxf.insert.x,e.dxf.insert.y))
    if t=='DIMENSION':
        try: m=e.get_measurement()
        except Exception: continue
        if isinstance(m,float) and m>=400: dims.append((e.dxf.defpoint.x,e.dxf.defpoint.y,round(m)))
tabs=[]
for e in msp:
    if e.dxftype()=='ACAD_TABLE':
        tabs.append((e.dxf.insert.x,e.dxf.insert.y))
for hx,hy in sorted(heads):
    near=sorted(set(m for x,y,m in dims if hx-1500<x<hx+1500 and hy-2200<y<hy))
    print(round(hx),round(hy),near)
