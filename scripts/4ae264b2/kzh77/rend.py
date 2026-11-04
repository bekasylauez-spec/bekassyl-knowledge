import sys, ezdxf
from ezdxf.recover import readfile
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
f,x0,y0,x1,y1,out=sys.argv[1],*map(float,sys.argv[2:6]),sys.argv[6]
doc,_=readfile(f); msp=doc.modelspace()
def inbox(e):
    try:
        from ezdxf import bbox
        b=bbox.extents([e],fast=True)
        if not b.has_data: return False
        return b.extmax.x>=x0 and b.extmin.x<=x1 and b.extmax.y>=y0 and b.extmin.y<=y1
    except Exception: return False
fig=plt.figure(figsize=((x1-x0)/1500,(y1-y0)/1500),dpi=150); ax=fig.add_axes([0,0,1,1])
cfg=Configuration(background_policy=BackgroundPolicy.WHITE,color_policy=ColorPolicy.BLACK)
Frontend(RenderContext(doc),MatplotlibBackend(ax),config=cfg).draw_entities(msp.query('*'),filter_func=inbox)
ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect('equal'); ax.axis('off')
fig.savefig(out,dpi=150,facecolor='white')
