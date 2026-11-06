import ezdxf
d=ezdxf.readfile('sch.dxf'); m=d.modelspace()
for e in m.query('INSERT'): print('INS',e.dxf.name,e.dxf.layer,'%.0f,%.0f'%(e.dxf.insert.x,e.dxf.insert.y),e.dxf.xscale)
for e in m.query('LWPOLYLINE[layer=="0"]'):
    p=list(e.get_points('xy')); xs=[a[0] for a in p]; ys=[a[1] for a in p]; print('PL0',min(xs),min(ys),max(xs),max(ys))
import collections
for e in m:
    if e.dxftype() not in ('LWPOLYLINE','HATCH','LINE','MTEXT','TEXT','INSERT'): print(e.dxftype())
xs=[];ys=[]
for e in m.query('LWPOLYLINE[layer=="Размеры"]'):
    for a in e.get_points('xy'): xs.append(a[0]); ys.append(a[1])
print('razm ext',min(xs),min(ys),max(xs),max(ys))
