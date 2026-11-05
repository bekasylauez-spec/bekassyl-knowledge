import ezdxf, json, re, pickle, collections, sys
from ezdxf import bbox
sys.stdout.reconfigure(encoding='utf-8')
doc = ezdxf.readfile('w/live.dxf'); msp = doc.modelspace(); cache = bbox.Cache()
SH = json.load(open(r'D:\РАБОЧКА\От Маке\Завод\АБК\_Инструменты\beka2_v2\sheets.json', encoding='utf-8'))
SH['4.2'] = [244346.9, -1749172.3, 274046.9, -1728172.3]
R = []
for e in msp:
    try: b = bbox.extents([e], cache=cache)
    except Exception: continue
    if not b.has_data: continue
    t = None
    if e.dxftype() == 'MTEXT': t = e.plain_text()
    elif e.dxftype() == 'TEXT': t = e.dxf.text
    try: lay = e.dxf.layer
    except Exception: lay = '?'
    R.append((e.dxf.handle, e.dxftype(), b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y, t, lay,
              getattr(e.dxf, 'char_height', None) if e.dxftype() == 'MTEXT' else getattr(e.dxf, 'height', None)))
pickle.dump((SH, R), open('w/all.pkl', 'wb'))
print(len(R))
