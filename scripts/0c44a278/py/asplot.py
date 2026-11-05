import json,sys,matplotlib,numpy as np
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.colors import ListedColormap,BoundaryNorm
S=r'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\0c44a278-d609-485d-a50c-02efd03030b0\scratchpad\w'
D=json.load(open(S+r'\as.json'))[sys.argv[1]]
b=[0,3.93,6.44,7.85,9.58,11.63,13.98,16.65,19.6,30]
cols=['#ffffff','#fff2a8','#ffd166','#f4a261','#e76f51','#d62828','#9d0208','#6a040f','#000000']
cm=ListedColormap(cols); nm=BoundaryNorm(b,cm.N)
names=['AS1 X низ','AS2 X верх','AS3 Y низ','AS4 Y верх']
xs=[p[0] for d in D for p in d['p']]; ys=[p[1] for d in D for p in d['p']]
for k in range(4):
    fig,ax=plt.subplots(figsize=(24,14))
    for d in D:
        ax.add_patch(Polygon(d['p'],closed=True,fc=cm(nm(d['a'][k])),ec='#ccc',lw=0.1))
    ax.set_xlim(min(xs)-0.5,max(xs)+0.5); ax.set_ylim(min(ys)-0.5,max(ys)+0.5); ax.set_aspect('equal')
    ax.set_xticks(np.arange(int(min(xs)),max(xs)+1,1)); ax.set_yticks(np.arange(0,max(ys)+1,1)); ax.tick_params(labelsize=6); ax.grid(lw=0.2)
    ax.set_title('%s %s  (бел ≤Ø10/200; жёлт +Ø8; оранж +Ø10; +Ø12; красн +Ø14; +Ø16; +Ø18; +Ø20; чёрн >)'%(sys.argv[1],names[k]))
    plt.savefig(S+r'\as_%s_%d.png'%(sys.argv[1],k+1),dpi=80,bbox_inches='tight'); plt.close()
