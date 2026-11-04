import ezdxf,sys
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, ColorPolicy, BackgroundPolicy
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
src,out=sys.argv[1],sys.argv[2]
win=[float(x) for x in sys.argv[3].split(',')] if len(sys.argv)>3 else None
d=ezdxf.readfile(src); m=d.modelspace()
fig=plt.figure(figsize=(20,12)); ax=fig.add_axes([0,0,1,1])
cfg=Configuration(color_policy=ColorPolicy.BLACK, background_policy=BackgroundPolicy.WHITE)
Frontend(RenderContext(d),MatplotlibBackend(ax),config=cfg).draw_layout(m)
if win: ax.set_xlim(win[0],win[2]); ax.set_ylim(win[1],win[3])
ax.set_aspect('equal'); fig.savefig(out,dpi=110); 
