import ezdxf,sys
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=ezdxf.readfile(sys.argv[1]); ms=d.modelspace()
x0,y0,x1,y1=map(float,sys.argv[3:7])
fig=plt.figure(figsize=(float(sys.argv[7]) if len(sys.argv)>7 else 16,(y1-y0)/(x1-x0)*(float(sys.argv[7]) if len(sys.argv)>7 else 16))); ax=fig.add_axes([0,0,1,1])
ctx=RenderContext(d); be=MatplotlibBackend(ax)
def flt(e):
    try:
        bb=ezdxf.bbox.extents([e],fast=True)
        return bb.has_data and bb.extmax.x>x0 and bb.extmin.x<x1 and bb.extmax.y>y0 and bb.extmin.y<y1
    except Exception: return False
Frontend(ctx,be).draw_entities(ms,filter_func=flt); ax.set_xlim(x0,x1); ax.set_ylim(y0,y1)
fig.savefig(sys.argv[2],dpi=100,facecolor='white')
