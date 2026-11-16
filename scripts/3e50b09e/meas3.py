import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import numpy as np
p=sys.argv[1]; x0,x1,y0,y1=map(int,sys.argv[2:6])
a=np.asarray(Image.open(p).convert("L"))[y0:y1,x0:x1]<160
cols=np.where(a.any(0))[0]
groups=[];s=None;q=None
for c in cols:
    if s is None: s=q=c; continue
    if c<=q+2: q=c; continue
    groups.append((s,q)); s=q=c
if s is not None: groups.append((s,q))
for g in groups[:8]:
    sub=a[:,g[0]:g[1]+1]; r=np.where(sub.any(1))[0]
    print("x%d-%d rows %d-%d h=%d"%(g[0]+x0,g[1]+x0,r[0]+y0,r[-1]+y0,r[-1]-r[0]+1))
