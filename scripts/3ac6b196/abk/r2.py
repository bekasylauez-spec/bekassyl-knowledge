import ezdxf, sys, pickle, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy
from ezdxf import bbox
# usage: r2.py dxf out.png x0 y0 x1 y1 [dpi] [figw]
d = ezdxf.readfile(sys.argv[1]); m = d.modelspace()
x0, y0, x1, y1 = map(float, sys.argv[3:7])
dpi = int(sys.argv[7]) if len(sys.argv) > 7 else 150
fw = float(sys.argv[8]) if len(sys.argv) > 8 else 16
cache = bbox.Cache()
def inside(e):
    try:
        b = bbox.extents([e], cache=cache)
    except Exception:
        return False
    if not b.has_data: return False
    return b.extmax.x >= x0 and b.extmin.x <= x1 and b.extmax.y >= y0 and b.extmin.y <= y1
fh = fw * (y1 - y0) / (x1 - x0)
fig = plt.figure(figsize=(fw, fh)); ax = fig.add_axes([0, 0, 1, 1])
cfg = Configuration(background_policy=BackgroundPolicy.WHITE)
Frontend(RenderContext(d), MatplotlibBackend(ax), config=cfg).draw_layout(m, finalize=False, filter_func=inside)
ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('equal'); ax.axis('off')
fig.savefig(sys.argv[2], dpi=dpi)
