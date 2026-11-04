import ezdxf,sys,collections
doc=ezdxf.readfile(sys.argv[1])
msp=doc.modelspace()
for e in msp.query('MTEXT TEXT'):
    t=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
    if 'Гидроизол' in t or 'битумн' in t:
        print(e.dxftype(),e.dxf.handle,e.dxf.layer,e.dxf.insert,repr(t[:300]))
print('layouts',[l.name for l in doc.layouts])
c=collections.Counter((e.dxf.layer,e.dxftype()) for e in msp)
for k,v in sorted(c.items(),key=lambda x:-x[1])[:50]: print(k,v)
