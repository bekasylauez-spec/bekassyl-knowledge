import pickle,sys,matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
hor,ver,bars=pickle.load(open(sys.argv[1],'rb'))
z=float(sys.argv[2])
fig,ax=plt.subplots(figsize=(22,13))
for st,ns in hor[z]:
    ax.add_patch(Polygon([(n[0],n[1]) for n in ns],closed=True,fc='#9cf',ec='#69c',lw=0.2))
for st,ns in bars:
    if all(abs(n[2]-z)<0.01 for n in ns):
        ax.plot([n[0] for n in ns],[n[1] for n in ns],'r-',lw=1)
    elif any(abs(n[2]-z)<0.01 for n in ns) and abs(ns[0][2]-ns[1][2])>0.1:
        n=[q for q in ns if abs(q[2]-z)<0.01][0]; ax.plot(n[0],n[1],'ks',ms=5)
ax.set_aspect('equal'); ax.grid(True,lw=0.3)
import numpy as np
ax.set_xticks(np.arange(-2,94,2)); ax.set_yticks(np.arange(-2,42,1)); ax.tick_params(labelsize=6)
plt.savefig(sys.argv[3],dpi=90,bbox_inches='tight')
