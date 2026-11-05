import ezdxf, collections
from ezdxf import bbox
d=ezdxf.readfile('a61.dxf'); m=d.modelspace()
c=collections.Counter(e.dxftype() for e in m); print(c.most_common(30))
fr=[e for e in m if e.dxftype() in ('ACAD_PROXY_ENTITY',) or 'FORMAT' in e.dxftype()]
print(len(fr))
# SPDS format frames are proxies; get bbox of each proxy with class name
for e in m:
    if e.dxftype()=='ACAD_PROXY_ENTITY':
        pass
print('layouts',[l.name for l in d.layouts])
ts=[]
for e in m.query('TEXT MTEXT'):
    t=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
    if any(k in t for k in ('Ригель','Рм','Разрез','Специфик','Ведомост','Схема')): ts.append((round(e.dxf.insert.x),round(e.dxf.insert.y),round(e.dxf.char_height if e.dxftype()=='MTEXT' else e.dxf.height,1),t[:80]))
for t in sorted(ts,key=lambda r:(-r[1],r[0])): print(t)
eb=bbox.extents(m); print(eb.extmin,eb.extmax)
