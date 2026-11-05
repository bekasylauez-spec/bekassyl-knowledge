import ezdxf,sys
from ezdxf import bbox
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
for e in m.query('INSERT'):
    b=d.blocks.get(e.dxf.name)
    eff=e.dxf.name
    try:
        if e.dxf.name.startswith('*U'):
            br=b.block_record
            # effective name via xdata/ AcDbDynamicBlockGUID
            eff=e.get_xdata('AcDbBlockRepBTag') if False else e.dxf.name
    except: pass
    ext=bbox.extents([e],fast=True)
    if ext.has_data and ext.size.x>20000:
        print(e.dxf.name, e.dxf.layer, round(ext.extmin.x),round(ext.extmin.y),round(ext.size.x),round(ext.size.y))
for t in m.query('TEXT MTEXT'):
    s=t.dxf.text if t.dxftype()=='TEXT' else t.text
    if any(k in s for k in ('Схема','Разрез','Спецификац','Пм','Лист')): print('T',round(t.dxf.insert.x),round(t.dxf.insert.y),s[:90].replace('\n',' '))
