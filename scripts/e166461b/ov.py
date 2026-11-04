import logging; logging.disable(logging.CRITICAL)
import ezdxf, pickle, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
ar=ezdxf.readfile('w/ar.dxf').modelspace()
src=ezdxf.readfile('w/src.dxf').modelspace()
X0=-232964; Y0=464256.885
fig,axs=plt.subplots(1,3,figsize=(36,16))
plans=[(404993,-145405,2),(470698,-148639,3),(533615,-148214,3)]
hor,ver,bars=pickle.load(open('lira6/g.pkl','rb'))
levels=[(-4.65,-0.1),(-0.1,3.95),(7.1,10.25)]
for k,(ax,(ax0,ay0,col)) in enumerate(zip(axs,plans)):
    ax.set_aspect('equal')
    for e in src:
        if e.dxftype()=='LWPOLYLINE' and e.dxf.color==124:
            p=e.get_points('xy'); ax.fill([q[0]-X0 for q in p],[q[1]-Y0 for q in p],color='#bbb')
    for e in ar:
        if e.dxftype()=='LWPOLYLINE' and abs(e.get_points('xy')[0][0]-ax0)<25000:
            p=e.get_points('xy'); 
            if e.closed: p=p+[p[0]]
            ax.plot([q[0]-ax0-125 for q in p],[q[1]-ay0-125 for q in p],'b-',lw=1)
    a,b=levels[k]
    for st,ns in ver:
        zs=[n[2] for n in ns]; zm=sum(zs)/len(zs)
        if a<zm<b:
            xs=[n[0]*1000 for n in ns]; ys=[n[1]*1000+float(sys.argv[1]) for n in ns]
            ax.plot([min(xs),max(xs)],[min(ys),max(ys)],'r-',lw=1)
    for st,ns in bars:
        zm=(ns[0][2]+ns[1][2])/2
        if a<zm<b: ax.plot(ns[0][0]*1000,ns[0][1]*1000+float(sys.argv[1]),'rs',ms=6,mfc='none')
    for x in [0,6800,13250,20050]: ax.axvline(x,color='k',lw=.3)
    for y in [0,5000,14750,22750,28750]: ax.axhline(y,color='k',lw=.3)
fig.tight_layout(); fig.savefig('ov.png',dpi=45)
