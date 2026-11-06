import ezdxf, sys, collections
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
c=collections.Counter(e.dxftype() for e in m); print(c.most_common(25))
L=collections.Counter(e.dxf.layer for e in m); print(L.most_common(40))
# texts containing marks
for e in m.query('TEXT MTEXT'):
    t=e.dxf.text if e.dxftype()=='TEXT' else e.text
    if any(k in t for k in ('Рм','Б-','Р-','Схема','План','отм','Лист','Ригель')):
        p=e.dxf.insert; print(round(p.x),round(p.y),t[:80].replace('\n',' '))
