import sys, ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
doc=ezdxf.readfile(r'D:\_claude_work\RMC\ar\ARCH_copy.dxf')
msp=doc.modelspace()
regs={'1':(1000000,1024000,35000,50500),'2':(1024500,1052500,35000,50500),'3':(1056500,1076000,36000,50500)}
for k,(x0,x1,y0,y1) in regs.items():
    fig=plt.figure(figsize=(16,16*(y1-y0)/(x1-x0)),dpi=110)
    ax=fig.add_axes([0,0,1,1])
    ctx=RenderContext(doc)
    Frontend(ctx,MatplotlibBackend(ax)).draw_layout(msp,finalize=False)
    ax.set_xlim(x0,x1);ax.set_ylim(y0,y1);ax.set_facecolor('white')
    fig.savefig(r'D:\_claude_work\RMC\ar\kzh_detail%s.png'%k,facecolor='white')
    print(k)
