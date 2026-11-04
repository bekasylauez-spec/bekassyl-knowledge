import ezdxf, sys, collections
from ezdxf import bbox
doc=ezdxf.readfile('km5.dxf'); msp=doc.modelspace()
import pickle
rows=[]
for e in msp:
    t=e.dxftype()
    try:
        bb=bbox.extents([e],fast=True)
        if not bb.has_data: continue
        x0,y0,x1,y1=bb.extmin.x,bb.extmin.y,bb.extmax.x,bb.extmax.y
    except Exception as ex: continue
    txt=''
    if t=='TEXT': txt=e.dxf.text
    elif t=='MTEXT': txt=e.text
    elif t=='ACAD_PROXY_ENTITY':
        t='PX:'+str(e.dxf.get('original_class_name', '')) if False else 'PX'
        try:
            parts=[]
            for v in e.virtual_entities():
                if v.dxftype() in('TEXT','MTEXT'): parts.append(v.dxf.text if v.dxftype()=='TEXT' else v.text)
            txt='|'.join(parts)
        except Exception as ex: txt='?'
    rows.append((e.dxf.handle,t,x0,y0,x1,y1,txt,e.dxf.layer))
pickle.dump(rows,open('rows.pkl','wb'))
print(len(rows))
