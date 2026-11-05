import ezdxf, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy
d = ezdxf.readfile(sys.argv[1]); m = d.modelspace()
x0, y0, x1, y1 = map(float, sys.argv[3:7])
fig = plt.figure(figsize=(float(sys.argv[7]), float(sys.argv[8])))
ax = fig.add_axes([0, 0, 1, 1])
ctx = RenderContext(d)
cfg = Configuration(background_policy=BackgroundPolicy.WHITE)
Frontend(ctx, MatplotlibBackend(ax), config=cfg).draw_layout(m, finalize=True)
ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
fig.savefig(sys.argv[2], dpi=int(sys.argv[9]) if len(sys.argv) > 9 else 150)
