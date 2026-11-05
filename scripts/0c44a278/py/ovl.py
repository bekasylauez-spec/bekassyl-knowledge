import json,sys,numpy as np,matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S=r'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\0c44a278-d609-485d-a50c-02efd03030b0\scratchpad\w'
z=sys.argv[1]; R=json.load(open(S+r'\scheme.json'))[z]
g=np.load(S+r'\g%s.npy'%z.replace('.',''))
fig,ax=plt.subplots(figsize=(30,19))
ax.imshow(g,origin='lower',extent=(12000,12000+g.shape[1]*50,0,g.shape[0]*50),cmap='Blues',alpha=0.35)
for pts,cl in R['dash']:
    p=np.array(pts+([pts[0]] if cl else [])); ax.plot(p[:,0],p[:,1],'r-',lw=0.6)
for pts,cl in R['solid']+R['col']:
    p=np.array(pts+([pts[0]] if cl else [])); ax.plot(p[:,0],p[:,1],'k-',lw=0.8)
x0,x1,y0,y1=map(float,sys.argv[2:6]); ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect('equal'); ax.grid(lw=0.2)
ax.set_xticks(np.arange(x0,x1,1000)); ax.tick_params(labelsize=6)
plt.savefig(sys.argv[6],dpi=70,bbox_inches='tight')
