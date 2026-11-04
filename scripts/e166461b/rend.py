import ezdxf, sys, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, ColorPolicy, BackgroundPolicy
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
x0,y0,x1,y1=map(float,sys.argv[3:7])
fig=plt.figure(figsize=(float(sys.argv[7]) if len(sys.argv)>7 else 16, (float(sys.argv[7]) if len(sys.argv)>7 else 16)*(y1-y0)/(x1-x0)))
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(x0,x1); ax.set_ylim(y0,y1)
cfg=Configuration(color_policy=ColorPolicy.BLACK, background_policy=BackgroundPolicy.WHITE, proxy_graphic_policy=ezdxf.addons.drawing.config.ProxyGraphicPolicy.SHOW)
ctx=RenderContext(d)
Frontend(ctx, MatplotlibBackend(ax), config=cfg).draw_layout(m, finalize=False)
ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect('equal'); ax.axis('off')
fig.savefig(sys.argv[2], dpi=100)
