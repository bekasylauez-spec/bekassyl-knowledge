import ezdxf, sys
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=ezdxf.readfile('st.dxf'); msp=d.modelspace()
x0,y0,x1,y1=map(float,sys.argv[1:5]); out=sys.argv[5]
from ezdxf import bbox
ents=[]
for e in msp:
  try:
    b=bbox.extents([e])
    if b.has_data and b.extmin.x>=x0 and b.extmax.x<=x1 and b.extmin.y>=y0 and b.extmax.y<=y1: ents.append(e)
  except Exception: pass
print(len(ents))
fig=plt.figure(figsize=(float(sys.argv[6]),float(sys.argv[7])),dpi=100); ax=fig.add_axes([0,0,1,1])
ctx=RenderContext(d); be=MatplotlibBackend(ax)
Frontend(ctx,be).draw_entities(ents)
ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect('equal')
fig.savefig(out,facecolor='white')
