import ezdxf, pickle
from ezdxf import recover, bbox
doc, aud = recover.readfile('src.dxf')
msp = doc.modelspace()
R=[]
for e in msp.query('INSERT'):
    n=e.dxf.name
    if n.startswith('A$') or 'Двутавр' in n or 'Труба' in n or 'Швеллер' in n or n.startswith('*U') or 'Короб' in n:
        try:
            b=bbox.extents(e.virtual_entities())
            R.append((n,e.dxf.insert.x,e.dxf.insert.y,e.dxf.get('rotation',0),e.dxf.get('xscale',1),e.dxf.get('yscale',1),b.extmin.x,b.extmin.y,b.extmax.x,b.extmax.y))
        except Exception as ex: R.append((n,e.dxf.insert.x,e.dxf.insert.y,0,0,0,0,0,0,0))
pickle.dump(R,open('ins.pkl','wb')); print(len(R))
