import sys,glob
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import numpy as np
Image.MAX_IMAGE_PIXELS=None
for n in sys.argv[1:]:
    f=glob.glob('D:/Бекасыл КЖ КМ/РМЦ_КМ/_тексеру/Парақ_КЖ-%s_*.png'%n)[0]
    a=np.asarray(Image.open(f).convert('L'))<140
    H,W=a.shape
    # frame inner x: find column with longest run near 4560
    sub=a[60:2300, :4550]
    cols=np.nonzero(sub.any(axis=0))[0]
    mx=cols.max()
    ys=np.nonzero(sub[:,mx])[0]
    # frame line x
    fr=[x for x in range(4540,4580) if a[200:2000,x].mean()>0.95]
    print(n,'rightmost content x',mx,'y',ys.min()+60,ys.max()+60,'frame cols',fr,'gap px',(fr[0]-mx) if fr else None,'mm',((fr[0]-mx)/(4600/594)) if fr else None)
