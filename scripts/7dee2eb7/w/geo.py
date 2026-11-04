import ezdxf,sys,collections
d=ezdxf.readfile('b4.dxf'); m=d.modelspace()
k=int(sys.argv[1]); X0=145817+84100*k; Y0=-1686243
for e in m:
    t=e.dxftype()
    if t=='LWPOLYLINE':
        p=list(e.get_points('xy'))
        if not (X0-15000<p[0][0]<X0+70000): continue
        q=[(round(a-X0),round(b-Y0)) for a,b in p]
        print('PL',e.dxf.handle,e.dxf.linetype,e.dxf.color,round(e.dxf.const_width or 0),e.closed,len(q),q[:8])
    elif t in('LINE',):
        if X0-15000<e.dxf.start[0]<X0+70000: print('LN',e.dxf.layer,[round(e.dxf.start[0]-X0),round(e.dxf.start[1]-Y0),round(e.dxf.end[0]-X0),round(e.dxf.end[1]-Y0)])
    elif t=='HATCH':
        try:
            pth=e.paths.paths[0]; v=pth.vertices if hasattr(pth,'vertices') else [ed.start for ed in pth.edges]
            if X0-15000<v[0][0]<X0+70000: print('HA',e.dxf.pattern_name,len(e.paths.paths),[(round(a-X0),round(b-Y0)) for a,b,*_ in v][:5])
        except Exception as ex: pass
    elif t in('TEXT','MTEXT','INSERT'):
        x=e.dxf.insert[0]
        if X0-15000<x<X0+70000: print(t,getattr(e.dxf,'name',''),round(x-X0),round(e.dxf.insert[1]-Y0),(e.plain_text() if t=='MTEXT' else getattr(e.dxf,'text',''))[:60])
