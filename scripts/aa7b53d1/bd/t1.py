import ezdxf
from ezdxf.math import area
doc=ezdxf.readfile('w.dxf'); msp=doc.modelspace()
# find sheet frame of type1: texts "1-тип"
for t in msp.query('MTEXT TEXT'):
    s=t.plain_text() if t.dxftype()=='MTEXT' else t.dxf.text
    if ('1-тип' in s or 'Разрез 1 - 1' in s or 'Стенка' in s or 'Подошва' in s) and 1690000<t.dxf.insert.x<1760000:
        print('TXT',t.dxf.handle,[round(v) for v in t.dxf.insert][:2],s[:40])
