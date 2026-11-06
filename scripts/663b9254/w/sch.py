import ezdxf,collections
doc=ezdxf.readfile('../dxf/sch3.dxf'); msp=doc.modelspace()
c=collections.Counter((e.dxftype(),e.dxf.layer) for e in msp)
for k,v in c.most_common(40): print(v,k)
# frames / texts with "Схема"
for e in msp.query('TEXT MTEXT'):
    s=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
    if 'хема' in s or 'Отм' in s or 'отм' in s: print(e.dxftype(),round(e.dxf.insert.x),round(e.dxf.insert.y),s[:80])
for e in msp.query('INSERT'):
    pass
ins=collections.Counter(e.dxf.name for e in msp.query('INSERT'))
print(ins.most_common(30))
print(collections.Counter(e.dxftype() for e in msp if e.dxftype().startswith('ACAD_PROXY')))
