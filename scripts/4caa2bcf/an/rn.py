import ezdxf, matplotlib, sys; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
x0,y0,x1,y1=map(float,sys.argv[3:7]); W=x1-x0; H=y1-y0; s=float(sys.argv[7]) if len(sys.argv)>7 else 20
fig=plt.figure(figsize=(s,s*H/W),dpi=100); ax=fig.add_axes([0,0,1,1])
cfg=Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK)
Frontend(RenderContext(d),MatplotlibBackend(ax),config=cfg).draw_layout(m)
ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect('auto'); ax.axis('off')
fig.savefig(sys.argv[2]); plt.close(fig)
