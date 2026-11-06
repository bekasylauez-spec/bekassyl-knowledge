import ezdxf,collections
d=ezdxf.readfile('sch.dxf')
b=d.blocks.get('15912165')
for e in b.query('TEXT'): print('T',e.dxf.text,'%.0f,%.0f'%(e.dxf.insert.x,e.dxf.insert.y))
for e in b.query('LWPOLYLINE'): p=list(e.get_points('xy')); print('PL',['%.0f,%.0f'%q for q in p][:4], e.dxf.linetype)
m=d.modelspace()
c2=collections.Counter()
for e in m.query('LWPOLYLINE'):
    c2[(e.dxf.layer,len(e),e.closed,e.dxf.linetype,round(e.dxf.const_width or 0))]+=1
print(c2.most_common(20))
for e in m.query('INSERT'): 
    if e.dxf.name in('а','купу к'): 
        bb=d.blocks.get(e.dxf.name); print(e.dxf.name,collections.Counter(x.dxftype() for x in bb))
