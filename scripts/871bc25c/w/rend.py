import ezdxf,sys,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration
d=ezdxf.readfile(sys.argv[1]); lay=d.layouts.get(sys.argv[3]) if len(sys.argv)>3 else d.modelspace()
fig=plt.figure(figsize=(30,20)); ax=fig.add_axes([0,0,1,1])
ctx=RenderContext(d); be=MatplotlibBackend(ax)
Frontend(ctx,be,config=Configuration(background_policy=ezdxf.addons.drawing.config.BackgroundPolicy.WHITE)).draw_layout(lay,finalize=True)
if len(sys.argv)>4:
  x0,y0,x1,y1=map(float,sys.argv[4].split(',')); ax.set_xlim(x0,x1); ax.set_ylim(y0,y1)
fig.savefig(sys.argv[2],dpi=int(sys.argv[5]) if len(sys.argv)>5 else 80)
