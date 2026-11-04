import ezdxf, sys
from ezdxf import bbox
sys.stdout.reconfigure(encoding='utf-8')
doc = ezdxf.readfile(sys.argv[1]); msp = doc.modelspace()
x, y, w, h = map(float, sys.argv[2].split(','))
allt = len(sys.argv) > 3
for e in msp:
    try: b = bbox.extents([e])
    except Exception: continue
    if not b.has_data: continue
    cx, cy = (b.extmin.x + b.extmax.x) / 2, (b.extmin.y + b.extmax.y) / 2
    if not (x <= cx <= x + w and y <= cy <= y + h): continue
    ty = e.dxftype(); t = ''
    if ty == 'MTEXT': t = e.plain_text()[:70]
    elif ty == 'TEXT': t = e.dxf.text
    elif ty == 'INSERT': t = e.dxf.name
    elif ty == 'DIMENSION': t = 'dim ' + str(round(e.get_measurement() if hasattr(e,'get_measurement') else 0))
    if allt or ty in ('MTEXT', 'TEXT') or (ty == 'INSERT' and not any(k in t for k in ('Профиль', 'Двутавр', 'Швеллер'))) or b.size.x > 20000:
        lay='?'
        try: lay=e.dxf.layer
        except Exception: pass
        print(ty, e.dxf.handle, lay,  [round(v) for v in (b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y)], t.replace('\n', '|'))
