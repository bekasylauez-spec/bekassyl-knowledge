import ezdxf,collections,re
d=ezdxf.readfile('sch.dxf'); m=d.modelspace()
c=collections.Counter((e.dxftype(),e.dxf.layer) for e in m)
for k,v in c.most_common(60): print(v,k)
print('layouts',[l.name for l in d.layouts])
bl=collections.Counter(e.dxf.name for e in m.query('INSERT'))
print(bl.most_common(40))
for e in m.query('TEXT MTEXT'):
    t=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
    if re.search(r'(?i)схем|разрез|рм|ригел|балк|Б-|лист|отм|план',t): print(e.dxftype(),'%.0f,%.0f'%(e.dxf.insert.x,e.dxf.insert.y),repr(t[:90]))
