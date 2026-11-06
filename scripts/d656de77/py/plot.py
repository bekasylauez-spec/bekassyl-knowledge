import sys, os
from common import *
import fitz
ks=[int(a) for a in sys.argv[1].split(',')]; tag=sys.argv[2] if len(sys.argv)>2 else 'p'
for k in ks:
    X0=SX(k); f=os.path.join(S,'img','%s6%d.pdf'%(tag,k+1))
    gx.run([dict(t='plotpdf',win=[X0,Y0,X0+31500,Y0+14850],file=f,media='ISO_full_bleed_A1_(841.00_x_594.00_MM)')],'pl')
    d=fitz.open(f); d[0].get_pixmap(dpi=100).save(f[:-4]+'.png')
    # quarter crops at higher dpi
    r=d[0].rect
    for i,(a,b) in enumerate([(0,0),(0.5,0),(0,0.5),(0.5,0.5)]):
        clip=fitz.Rect(r.width*a, r.height*(b*0.8+0.13), r.width*(a+0.5), r.height*(b*0.8+0.13+0.42))
        d[0].get_pixmap(dpi=190,clip=clip).save(f[:-4]+'_q%d.png'%i)
    d.close(); print(f)
