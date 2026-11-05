import ezdxf,collections,pickle
doc=ezdxf.readfile('an.dxf'); msp=doc.modelspace()
from ezdxf import bbox
F=[(0,29700,'2.1'),(29700,59400,'2.2'),(59400,89100,'2.3'),(89100,118800,'3.1'),(118800,148500,'3.2'),(148500,178200,'3.3'),(178200,207900,'3.4'),(207900,237600,'3.5'),(237600,267300,'3.6'),(267300,277800,'3.7')]
rows=[]
for e in msp:
  try:
      if not hasattr(e.dxf,'handle'): continue
      try: b=bbox.extents([e],fast=True)
      except Exception: continue
      if not b.has_data: continue
      cx=(b.extmin.x+b.extmax.x)/2; cy=(b.extmin.y+b.extmax.y)/2
      if not (340000<=cy<=382000): continue
      sh=None
      for a,c,n in F:
          if a<=cx<c: sh=n
      txt=''
      if e.dxftype()=='MTEXT': txt=e.plain_text()[:60]
      elif e.dxftype()=='TEXT': txt=e.dxf.text[:60]
      elif e.dxftype()=='DIMENSION': txt=(e.dxf.get('text','') or '')+' st=%s'%e.dxf.dimstyle
      rows.append((sh,e.dxftype(),e.dxf.handle,e.dxf.get('layer',''),round(b.extmin.x),round(b.extmin.y),round(b.extmax.x),round(b.extmax.y),txt))
  except Exception as ex: pass
pickle.dump(rows,open('rows.pkl','wb'))
C=collections.Counter((r[0],r[1]) for r in rows)
for k in sorted(C,key=str): print(k,C[k])
