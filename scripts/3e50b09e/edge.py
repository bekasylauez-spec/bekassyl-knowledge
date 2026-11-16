import sys,glob
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import numpy as np
Image.MAX_IMAGE_PIXELS=None
for n in sys.argv[1:]:
    f=glob.glob('D:/Бекасыл КЖ КМ/РМЦ_КМ/_тексеру/Парақ_КЖ-%s_*.png'%n)[0]
    a=np.asarray(Image.open(f).convert('L'))<128
    H,W=a.shape
    # long vertical lines near right: columns with dark run >= 1000 px
    cols=[]
    for x in range(W-400,W):
        col=a[:,x]
        # longest run
        best=0;cur=0
        for v in col[::1]:
            if v: cur+=1; best=max(best,cur)
            else: cur=0
        if best>600: cols.append((x,best))
    # rightmost dark px in rows 100..1800 excluding the frame cols
    print(n,W,cols[:12])
