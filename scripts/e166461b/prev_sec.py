import gen_sec as G, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,axs=plt.subplots(1,3,figsize=(48,16))
for ax,(cut,pos,view) in zip(axs,[('x',11900,-1),('y',1500,1),('y',16600,1)]):
    c,p,l=G.section(cut,pos,view)
    for g in G.geoms(c):
        ax.fill(*g.exterior.xy,color='#999'); 
        for r in g.interiors: ax.fill(*r.xy,color='w')
    for g in G.geoms(p): ax.fill(*g.exterior.xy,color='#dd8')
    for ln in l: ax.plot([a for a,b in ln],[b for a,b in ln],'k-',lw=.4)
    ax.set_aspect('equal'); ax.set_title(f'{cut}={pos}')
fig.tight_layout(); fig.savefig('w/secprev.png',dpi=40)
