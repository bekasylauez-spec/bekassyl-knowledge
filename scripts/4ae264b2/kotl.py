import numpy as np
from shapely.geometry import Polygon, Point
from shapely import vectorized
B=Polygon([(-1100,-1100),(61300,-1100),(61300,7350),(50100,7350),(50100,18500),(-1100,18500)])
print('bottom area m2', B.area/1e6)
pts=np.array([(-1100-2050,18500+2050),(50100+2300,18500+2300),(50100+2480,7350+2480),(61300+2500,7350+2500),(61300+2700,-1100-2700),(-1100-2400,-1100-2400)],float)
g=np.array([793.30,793.83,794.17,794.24,794.59,794.00])
bot=789.30
step=100
xs=np.arange(-6000,66000,step)+step/2; ys=np.arange(-6000,23000,step)+step/2
X,Y=np.meshgrid(xs,ys)
W=1/(((X[...,None]-pts[:,0])**2+(Y[...,None]-pts[:,1])**2)+1)**1.0; G=(W*g).sum(-1)/W.sum(-1)
from shapely import distance, points
P=points(X.ravel(),Y.ravel())
D=distance(B,P).reshape(X.shape)/1000.0
for k in (0.5,1.0):
  Z=bot+D/k
  V=np.clip(G-Z,0,None).sum()*(step/1000)**2
  inside=D==0
  print('slope 1:%.2f  V=%.0f m3, avg depth bottom %.2f'%(k,V,(G[inside]-bot).mean()))
# top outline check: slope width at corners
for p,gg in zip(pts,g): print(gg, (gg-bot)*0.5)
