import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.patches as pa, matplotlib.colors as mc
from cells import cells
import sys
z=float(sys.argv[1]); C=cells(z)
fig,axs=plt.subplots(2,2,figsize=(22,20))
names=['As1 X низ','As2 X верх','As3 Y низ','As4 Y верх']
cm=mc.ListedColormap(['#ffffff','#9ad0ff','#2f80ff','#ffb000','#ff3000','#800080'])
nb=mc.BoundaryNorm([0,3.93,7.85,9.58,11.63,13.98,30],6)
AX=[0,650,6650,12650,18650,24850,31850,38850,44850]; AY=[0,9000,13900,21000,27500,36000,39000]
for k,ax in enumerate(axs.flat):
    for c in C:
        ax.add_patch(pa.Polygon(c['poly'],closed=True,fc=cm(nb(c['As'][k])),ec='#ddd',lw=0.2))
        if c['As'][k]>3.93: ax.text(c['cx'],c['cy'],'%.1f'%c['As'][k],fontsize=4.5 if z>5 else 7,ha='center',va='center')
    for x in AX: ax.axvline(x,color='k',lw=0.3,ls='-.')
    for y in AY: ax.axhline(y,color='k',lw=0.3,ls='-.')
    ax.set_aspect('equal'); ax.autoscale(); ax.set_title(names[k])
plt.tight_layout(); plt.savefig('heat_%s.png'%sys.argv[1],dpi=90)
