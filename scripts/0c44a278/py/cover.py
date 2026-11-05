import pickle,numpy as np
from scipy import ndimage
import geom, design as D0
S=geom.S
res,RAS=pickle.load(open(S+r'\design.pkl','rb'))
for z in res:
    R=RAS[z]
    for f in range(4):
        dirn='X' if f<2 else 'Y'
        req=ndimage.uniform_filter1d(R['A'][f],size=5,axis=0 if dirn=='X' else 1)
        raw=R['A'][f]
        prov=np.full(req.shape,D0.BASE)
        for Zn in res[z][f]:
            for c in Zn['cs']:
                if dirn=='X':
                    j0=int((c-100-R['y0'])/100); j1=int((c+100-R['y0'])/100); i0=int((Zn['s']-R['x0'])/100); i1=int((Zn['e']-R['x0'])/100)
                    prov[j0:j1,i0:i1]+=D0.asd(Zn['d'])
                else:
                    i0=int((c-100-R['x0'])/100); i1=int((c+100-R['x0'])/100); j0=int((Zn['s']-R['y0'])/100); j1=int((Zn['e']-R['y0'])/100)
                    prov[j0:j1,i0:i1]+=D0.asd(Zn['d'])
        M=R['M'].copy()
        sl=geom.slab(z)
        for b in sl['beams']:
            w=b[2]-b[0]; h=b[3]-b[1]
            if ((w>h) if dirn=='X' else (h>w)) and min(w,h)<=700:
                i0=max(0,int((b[0]-R['x0'])/100)); i1=int((b[2]-R['x0'])/100)+1; j0=max(0,int((b[1]-R['y0'])/100)); j1=int((b[3]-R['y0'])/100)+1
                M[j0:j1,i0:i1]=False
        cols=[(x,y) for x in ([12000,18000,24000,30000,36000,42000,47500,53500,59500,65900,73100] if z=='7.0' else [12000,18000,24000,30000]) for y in ([0,9000,13900,21000,27500,36000,39000] if z=='7.0' else [0,9000])]
        X,Y=np.meshgrid(R['x0']+(np.arange(R['nx'])+0.5)*100,R['y0']+(np.arange(R['ny'])+0.5)*100)
        for (cx,cy) in cols: M&=~((abs(X-cx)<650)&(abs(Y-cy)<650))
        df=(req-prov)*M; dr=(raw-prov)*M
        print(z,f,'smoothed deficit>0.2: %.2f m2 max %.2f | raw deficit>0.5: %.2f m2 max %.2f'%(((df>0.2).sum()/100),df.max(),((dr>0.5).sum()/100),dr.max()))
        lab,n=ndimage.label(dr>0.5)
        for k in range(1,n+1):
            jj,ii=np.where(lab==k)
            if len(jj)<15 and dr[jj,ii].max()<1.5: continue
            print('    comp %.2fm2 max %.1f x %d-%d y %d-%d'%(len(jj)/100,dr[jj,ii].max(),R['x0']+ii.min()*100,R['x0']+ii.max()*100+100,R['y0']+jj.min()*100,R['y0']+jj.max()*100+100))
        if False:
            jj,ii=np.where(dr==dr.max()); print('    worst raw at x=%d y=%d req=%.1f prov=%.1f'%(R['x0']+ii[0]*100,R['y0']+jj[0]*100,raw[jj[0],ii[0]],prov[jj[0],ii[0]]))
