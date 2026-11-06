import ezdxf, collections
d=ezdxf.readfile('a61.dxf'); m=d.modelspace()
print(collections.Counter(e.dxftype() for e in m).most_common(25))
for e in m.query('MTEXT TEXT'):
    t=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
    if any(k in t for k in ('Ригель','Разрез','Спецификац','Ведомость','Узел','Таблица','Лист','6.')) and len(t)<90:
        print(e.dxf.handle, repr(t[:80]), [round(v) for v in e.dxf.insert][:2], round(e.dxf.char_height if e.dxftype()=='MTEXT' else e.dxf.height,1))
