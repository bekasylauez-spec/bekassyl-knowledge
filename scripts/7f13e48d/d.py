import fitz,numpy as np
from PIL import Image
P={'o':r"D:\РАБОЧКА\ТUNAY STROY\Проект\Лестница\КМ Чертеж БЦ.pdf",'v1':r"D:\_claude_work\bc_lestnitsa\var\v1.pdf",'v2':r"D:\_claude_work\bc_lestnitsa\var\v2.pdf"}
d={k:fitz.open(p) for k,p in P.items()}
def r(k,i,dpi=100):
    pm=d[k][i].get_pixmap(dpi=dpi); return np.frombuffer(pm.samples,np.uint8).reshape(pm.height,pm.width,3).astype(int)
for i in range(14):
    a=r('v1',i);b=r('v2',i);o=r('o',i)
    m=(np.abs(a-b).sum(2)>30)
    ys,xs=np.where(m)
    print(i+1,'v2-v1',m.sum(), (xs.min(),ys.min(),xs.max(),ys.max()) if m.sum() else '', ' v2-o',(np.abs(o-b).sum(2)>30).sum())
