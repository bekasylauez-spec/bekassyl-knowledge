import pickle, sys, collections, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
hor,ver,bars=pickle.load(open(sys.argv[1]+'/g.pkl','rb'))
L=[-4.65,-0.1,3.95,7.1,10.25,13.4,16.55,19.7,22.4,23.1]
T={1:.2,2:.2,3:.2,4:.25,5:.25,6:.4,7:.7}
fig,axs=plt.subplots(2,5,figsize=(40,20)); axs=axs.ravel()
for k in range(len(L)-1):
    a,b=L[k],L[k+1]; ax=axs[k]; ax.set_title(f'{a}..{b}'); ax.set_aspect('equal')
    for z,v in hor.items():
        if abs(z-a)<1e-3:
            for st,ns in v:
                xs=[n[0] for n in ns]+[ns[0][0]]; ys=[n[1] for n in ns]+[ns[0][1]]
                ax.fill(xs,ys,color='#eee',lw=0)
    for st,ns in ver:
        zs=[n[2] for n in ns]; zm=sum(zs)/len(zs)
        if a<zm<b:
            xs=[n[0] for n in ns]; ys=[n[1] for n in ns]
            ax.plot([min(xs),max(xs)] if max(xs)-min(xs)>max(ys)-min(ys) else [xs[0]]*2, [ys[0]]*2 if max(xs)-min(xs)>max(ys)-min(ys) else [min(ys),max(ys)], color={1:"g",2:"g",3:"orange",4:"r",5:"m",6:"c",9:"y"}.get(st,"k"), lw=3 if st==4 else 2)
    for st,ns in bars:
        zm=(ns[0][2]+ns[1][2])/2
        if a<zm<b:
            if abs(ns[0][0]-ns[1][0])<1e-3 and abs(ns[0][1]-ns[1][1])<1e-3: ax.plot(ns[0][0],ns[0][1],'ks',ms=8)
            else: ax.plot([ns[0][0],ns[1][0]],[ns[0][1],ns[1][1]],'b-',lw=1)
    for x in [0,6.8,13.25,20.05]: ax.axvline(x,color='k',lw=.3,ls='-.')
    for y in [0,5,14.75,22.75,28.75]: ax.axhline(y,color='k',lw=.3,ls='-.')
    ax.set_xlim(-2,22); ax.set_ylim(-4,30)
fig.tight_layout(); fig.savefig(sys.argv[1]+'/storeys.png',dpi=40)
