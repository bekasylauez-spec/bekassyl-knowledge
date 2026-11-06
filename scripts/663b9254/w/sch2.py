import ezdxf,collections
doc=ezdxf.readfile('../dxf/sch3.dxf'); msp=doc.modelspace()
for e in msp.query('INSERT'): print('INS',e.dxf.name,e.dxf.layer,[round(v) for v in e.dxf.insert][:2],round(e.dxf.rotation,1),e.dxf.xscale)
for e in msp.query('MTEXT TEXT'):
    s=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
    print('T',e.dxf.layer,round(e.dxf.insert.x),round(e.dxf.insert.y),s[:60].replace('\n',' '))
c=collections.Counter()
for e in msp.query('LWPOLYLINE[layer=="Размеры"]'):
    p=[(round(x),round(y)) for x,y in e.get_points('xy')]
    xs=[q[0] for q in p]; ys=[q[1] for q in p]
    sheet=int((min(xs)-130000)//84100)
    c[(sheet,len(p),e.closed,max(xs)-min(xs),max(ys)-min(ys))]+=1
for k,v in sorted(c.items()): print(v,k)
