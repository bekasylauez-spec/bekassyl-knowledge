import ezdxf, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
d=ezdxf.readfile('sch.dxf'); m=d.modelspace()
for i,x0 in enumerate([135817,219917,304017,388117]):
    fig=plt.figure(figsize=(16,11.3),dpi=110); ax=fig.add_axes([0,0,1,1])
    Frontend(RenderContext(d),MatplotlibBackend(ax)).draw_layout(m)
    ax.set_xlim(x0,x0+84100); ax.set_ylim(-1788184,-1728784); ax.set_aspect('equal')
    fig.savefig(f's{i+1}.png'); plt.close(fig)
