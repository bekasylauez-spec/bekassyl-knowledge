import ezdxf, collections
d=ezdxf.readfile('../dxf/an.dxf'); m=d.modelspace()
print(collections.Counter(e.dxftype() for e in m).most_common())
# frames: SPDS format proxies? find stamp inserts and big polylines
for e in m.query('INSERT'):
    if 'Штамп' in e.dxf.name or 'Формат' in e.dxf.name or 'Рамк' in e.dxf.name:
        print('INS',e.dxf.name, round(e.dxf.insert.x), round(e.dxf.insert.y), e.dxf.xscale)
for e in m.query('TEXT MTEXT'):
    t=e.dxf.text if e.dxftype()=='TEXT' else e.plain_text()
    if any(k in t for k in ('Рм','Ригель','Разрез','Спецификац','Ведомость','Узел','Лист','отм')):
        p=e.dxf.insert; print(round(p.x),round(p.y),e.dxftype(),t[:70].replace('\n',' '))
