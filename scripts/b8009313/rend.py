import sys,ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
f,out,x0,y0,x1,y1=sys.argv[1],sys.argv[2],*map(float,sys.argv[3:7])
d=ezdxf.readfile(f); m=d.modelspace()
fig=plt.figure(figsize=(16,16*(y1-y0)/(x1-x0))); ax=fig.add_axes([0,0,1,1])
ctx=RenderContext(d); be=MatplotlibBackend(ax)
def flt(e):
    try:
        b=ezdxf.bbox.extents([e],fast=True)
        if not b.has_data: return False
        return b.extmax.x>x0 and b.extmin.x<x1 and b.extmax.y>y0 and b.extmin.y<y1
    except Exception: return False
Frontend(ctx,be).draw_entities(filter(flt,m))
ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_facecolor('white'); fig.savefig(out,dpi=110,facecolor='white')
