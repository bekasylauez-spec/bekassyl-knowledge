import ezdxf,matplotlib,sys
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy
from ezdxf import bbox
d=ezdxf.readfile(sys.argv[1]); ms=d.modelspace()
cache=bbox.Cache()
def rend(fn,x0,y0,x1,y1,w=24,dpi=90):
  fig=plt.figure(figsize=(w,w*(y1-y0)/(x1-x0))); ax=fig.add_axes([0,0,1,1])
  ctx=RenderContext(d); be=MatplotlibBackend(ax)
  def filt(e):
    try:
      bb=bbox.extents([e],fast=True,cache=cache)
      if not bb.has_data: return False
      return bb.extmax.x>x0 and bb.extmin.x<x1 and bb.extmax.y>y0 and bb.extmin.y<y1
    except Exception: return False
  Frontend(ctx,be,config=Configuration(background_policy=BackgroundPolicy.WHITE)).draw_layout(ms,finalize=False,filter_func=filt)
  ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect('equal'); ax.axis('off')
  fig.savefig(fn,dpi=dpi); plt.close(fig)
args=sys.argv[2:]
for i in range(0,len(args),5):
  fn=args[i]; x0,y0,x1,y1=map(float,args[i+1:i+5]); rend(fn,x0,y0,x1,y1)
