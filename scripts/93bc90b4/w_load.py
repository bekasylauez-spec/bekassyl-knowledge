import ezdxf, pickle, sys
from ezdxf import bbox
d=ezdxf.readfile(sys.argv[1])
msp=d.modelspace()
rows=[]
for e in msp:
    t=e.dxftype()
    try: b=bbox.extents([e],fast=True)
    except Exception: continue
    if not b.has_data: continue
    txt=e.dxf.text if t=='TEXT' else (e.text if t=='MTEXT' else '')
    geo=None
    if t=='LINE': geo=(e.dxf.start.x,e.dxf.start.y,e.dxf.end.x,e.dxf.end.y)
    rows.append((e.dxf.handle,t,b.extmin.x,b.extmin.y,b.extmax.x,b.extmax.y,txt,e.dxf.get('linetype','ByLayer'),e.dxf.layer,geo, e.dxf.get('rotation',0) if t in('TEXT','MTEXT') else 0))
pickle.dump(rows,open(sys.argv[2],'wb')); print(len(rows))
