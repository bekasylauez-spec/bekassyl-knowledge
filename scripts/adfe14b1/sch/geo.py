import ezdxf,collections,json
d=ezdxf.readfile('s4.dxf'); m=d.modelspace()
b=d.blocks['259191']
for e in b.query('LWPOLYLINE'): print('axl',[(round(p[0]),round(p[1])) for p in e.get_points()])
ins=[e for e in m.query('INSERT') if e.dxf.name=='259191']
for i in ins: print('ins',i.dxf.insert)
