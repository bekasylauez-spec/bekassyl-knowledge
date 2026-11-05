import ezdxf, sys, collections, re
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
c=collections.Counter(e.dxftype() for e in m); print(c.most_common(30))
ins=collections.Counter(e.dxf.name for e in m.query('INSERT')); print(ins.most_common(30))
lay=collections.Counter(e.dxf.layer for e in m); print(lay.most_common(40))
for e in m.query('TEXT MTEXT'):
    t=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
    if re.search(r'(План|Схема|Разрез|Плита|армир|Опалуб|Специф|Ведом|Узел|Примеч|ПРИМЕЧ)',t,re.I) and len(t)<120:
        p=e.dxf.insert; print(round(p.x),round(p.y),e.dxf.layer,repr(t[:110]))
