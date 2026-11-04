import ezdxf,sys,json
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, ColorPolicy, BackgroundPolicy, ProxyGraphicPolicy
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
src=sys.argv[1]; wins=json.load(open(sys.argv[2])); outdir=sys.argv[3]
d=ezdxf.readfile(src); m=d.modelspace()
from ezdxf import bbox
cache=bbox.Cache()
ents=list(m)
boxes=[]
for e in ents:
    try: b=bbox.extents([e],cache=cache,fast=True); boxes.append((e,b))
    except: pass
cfg=Configuration(color_policy=ColorPolicy.BLACK, background_policy=BackgroundPolicy.WHITE)
for name,(x0,y0,x1,y1) in wins.items():
    sel=[e for e,b in boxes if b.has_data and b.extmax[0]>=x0 and b.extmin[0]<=x1 and b.extmax[1]>=y0 and b.extmin[1]<=y1]
    w=x1-x0;h=y1-y0; fw=16; fh=fw*h/w
    fig=plt.figure(figsize=(fw,fh)); ax=fig.add_axes([0,0,1,1])
    fe=Frontend(RenderContext(d),MatplotlibBackend(ax),config=cfg)
    fe.draw_entities(sel)
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect('equal'); ax.axis('off')
    fig.savefig(f'{outdir}/{name}.png',dpi=100); plt.close(fig); print(name,len(sel))
