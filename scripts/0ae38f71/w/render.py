import ezdxf, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf import bbox
src,out=sys.argv[1],sys.argv[2]; X0,Y0,X1,Y1=map(float,sys.argv[3:7])
doc=ezdxf.readfile(src); msp=doc.modelspace()
cache=bbox.Cache(); ents=[]
for e in msp:
    try: b=bbox.extents([e],cache=cache,fast=True)
    except Exception: continue
    if not b.has_data: continue
    if b.extmax.x<X0 or b.extmin.x>X1 or b.extmax.y<Y0 or b.extmin.y>Y1: continue
    if e.dxftype()=='SPDSFORMAT': continue
    ents.append(e)
fig=plt.figure(figsize=(12,12*(Y1-Y0)/(X1-X0))); ax=fig.add_axes([0,0,1,1])
ctx=RenderContext(doc); be=MatplotlibBackend(ax)
Frontend(ctx,be).draw_entities(ents)
ax.set_xlim(X0,X1); ax.set_ylim(Y0,Y1); ax.set_facecolor('white')
fig.savefig(out,dpi=110,facecolor='white')
