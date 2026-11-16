import sys,glob
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import numpy as np
Image.MAX_IMAGE_PIXELS=None
for f in sorted(glob.glob('D:/Бекасыл КЖ КМ/РМЦ_КМ/_тексеру/Парақ_КЖ-*.png')):
    a=np.asarray(Image.open(f).convert('RGB')).astype(int)
    m=(a[:,:,1]>a[:,:,0]+60)&(a[:,:,1]>a[:,:,2]+60)
    r=(a[:,:,0]>a[:,:,1]+60)&(a[:,:,0]>a[:,:,2]+60)
    b=(a[:,:,2]>a[:,:,0]+60)&(a[:,:,2]>a[:,:,1]+60)
    ys,xs=np.nonzero(m)
    print(f.split('_')[1][:6], 'green',m.sum(),'red',r.sum(),'blue',b.sum(), (xs.min(),ys.min(),xs.max(),ys.max()) if m.sum() else '')
