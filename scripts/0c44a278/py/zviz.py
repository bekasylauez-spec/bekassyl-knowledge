import pickle,sys,numpy as np,matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import geom
S=geom.S
res,RAS=pickle.load(open(S+r'\design.pkl','rb'))
z=sys.argv[1]; f=int(sys.argv[2]); R=RAS[z]
A=R['A'][f]-3.93; A[~R['M']]=np.nan
fig,ax=plt.subplots(figsize=(30,19))
ax.imshow(np.clip(A,0,None),origin='lower',extent=(R['x0'],R['x0']+R['nx']*100,R['y0'],R['y0']+R['ny']*100),cmap='YlOrRd',vmin=0,vmax=12)
sl=geom.slab(z)
x,y=sl['outer'].exterior.xy; ax.plot(x,y,'k-',lw=1)
for h in sl['holes']:
    x,y=h['geom'].exterior.xy; ax.plot(x,y,'k-',lw=0.8)
for Z in res[z][f]:
    c0,c1=min(Z['cs']),max(Z['cs'])
    if f<2: r=Rectangle((Z['s'],c0),Z['e']-Z['s'],c1-c0+1,fill=False,ec='b',lw=1.2)
    else: r=Rectangle((c0,Z['s']),c1-c0+1,Z['e']-Z['s'],fill=False,ec='b',lw=1.2)
    ax.add_patch(r)
    tx=(Z['s']+Z['e'])/2; ty=(c0+c1)/2
    ax.text(tx if f<2 else ty, ty if f<2 else tx,'%d/%d n%d'%(Z['d'],Z['L'],len(Z['cs'])),fontsize=7,color='b',ha='center')
ax.set_aspect('equal'); x0,x1,y0,y1=(map(float,sys.argv[4:8]) if len(sys.argv)>4 else (R['x0'],R['x0']+R['nx']*100,R['y0'],R['y0']+R['ny']*100)); ax.set_xlim(x0,x1); ax.set_ylim(y0,y1)
plt.savefig(sys.argv[3],dpi=60,bbox_inches='tight')
