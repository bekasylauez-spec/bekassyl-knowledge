import pickle,sys,numpy as np
from matplotlib.path import Path
from scipy import ndimage
hor,ver,bars=pickle.load(open(sys.argv[1],'rb')); z=float(sys.argv[2]); h=0.05
P=hor[z]; xs=[n[0] for _,ns in P for n in ns]; ys=[n[1] for _,ns in P for n in ns]
x0,y0=min(xs),min(ys); nx=int((max(xs)-x0)/h)+1; ny=int((max(ys)-y0)/h)+1
g=np.zeros((ny,nx),bool)
for st,ns in P:
    pts=[(n[0],n[1]) for n in ns]; import math; cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts); pts.sort(key=lambda p: math.atan2(p[1]-cy,p[0]-cx)); pa=Path(pts)
    a=min(p[0] for p in pts);b=max(p[0] for p in pts);c=min(p[1] for p in pts);d=max(p[1] for p in pts)
    i0,i1=int((a-x0)/h),int((b-x0)/h)+1; j0,j1=int((c-y0)/h),int((d-y0)/h)+1
    X,Y=np.meshgrid(x0+(np.arange(i0,i1)+0.5)*h, y0+(np.arange(j0,j1)+0.5)*h)
    m=pa.contains_points(np.c_[X.ravel(),Y.ravel()]).reshape(X.shape)
    g[j0:j1,i0:i1]|=m
print('grid',nx,ny,'filled',g.sum()*h*h)
lab,n=ndimage.label(~g)
for k in range(1,n+1):
    jj,ii=np.where(lab==k)
    if len(jj)*h*h<0.02: continue
    edge = jj.min()==0 or ii.min()==0 or jj.max()==ny-1 or ii.max()==nx-1
    print('%s area %.2f  x %.2f-%.2f  y %.2f-%.2f'%('OUT ' if edge else 'HOLE',len(jj)*h*h,x0+ii.min()*h,x0+(ii.max()+1)*h,y0+jj.min()*h,y0+(jj.max()+1)*h))
np.save(sys.argv[3],g); print(x0,y0,h)
