import sys,ezdxf,matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
f,out,x0,y0,x1,y1=sys.argv[1],sys.argv[2],*map(float,sys.argv[3:7])
d=ezdxf.readfile(f); m=d.modelspace()
w=20; h=w*(y1-y0)/(x1-x0)
fig=plt.figure(figsize=(w,h),dpi=120); ax=fig.add_axes([0,0,1,1])
cfg=Configuration(background_policy=BackgroundPolicy.WHITE,color_policy=ColorPolicy.BLACK)
Frontend(RenderContext(d),MatplotlibBackend(ax),config=cfg).draw_layout(m,finalize=False)
ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect('equal'); ax.axis('off')
fig.savefig(out,facecolor='white')
