import ezdxf, collections
d=ezdxf.readfile('sch.dxf'); m=d.modelspace()
for e in m.query('INSERT'):
    b=d.blocks[e.dxf.name]; c=collections.Counter(x.dxftype() for x in b)
    print(e.dxf.name, [round(v) for v in e.dxf.insert], e.dxf.xscale, e.dxf.layer, dict(c))
for e in m.query('TEXT MTEXT'): print(e.dxftype(), (e.dxf.text if e.dxftype()=='TEXT' else e.plain_text())[:60], [round(v) for v in e.dxf.insert])
for e in m.query('LINE'): print('L',[round(v) for v in e.dxf.start],[round(v) for v in e.dxf.end],e.dxf.layer)
xs=[];ys=[]
for e in m.query('LWPOLYLINE'):
    for p in e.get_points('xy'): xs.append(p[0]);ys.append(p[1])
print('pl ext',min(xs),max(xs),min(ys),max(ys))
print(len(d.layouts), [l.name for l in d.layouts])
