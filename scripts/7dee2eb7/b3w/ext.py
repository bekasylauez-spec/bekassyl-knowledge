import ezdxf, sys
from ezdxf import bbox
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
xs=[];ys=[]
for e in m.query('TEXT MTEXT'):
    xs.append(e.dxf.insert[0]); ys.append(e.dxf.insert[1])
xs.sort(); ys.sort(); n=len(xs)
print(xs[0],xs[n//50],xs[-n//50],xs[-1]); print(ys[0],ys[n//50],ys[-n//50],ys[-1])
