import ezdxf, sys
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
for e in m.query('LWPOLYLINE'):
    p=list(e.get_points('xy'))
    if len(p)<4: continue
    xs=[a[0] for a in p]; ys=[a[1] for a in p]; w=max(xs)-min(xs); h=max(ys)-min(ys)
    if w>15000 and h>15000: print(e.dxf.layer, e.dxf.handle, round(min(xs)),round(min(ys)),round(w),round(h), e.dxf.const_width if e.dxf.hasattr('const_width') else '')
for e in m.query('INSERT'):
    n=e.dxf.name
    if n in('Штамп№1','259191','а','купу к') or n.startswith('A$') : print('INS',n,e.dxf.layer,[round(v) for v in e.dxf.insert][:2],round(e.dxf.xscale,3),round(e.dxf.rotation))
