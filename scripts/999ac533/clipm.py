# clipm.py pdf X0 Y0(sheet bottom-left model) W H(model) x0 y0 x1 y1 out dpi  -- sheet drawn in lower-left of the page; finds frame box automatically
import fitz,sys,numpy as np
f=sys.argv[1];X0,Y0,W,H,x0,y0,x1,y1=map(float,sys.argv[2:10]);out=sys.argv[10];dpi=int(sys.argv[11])
p=fitz.open(f)[0]
lo=p.get_pixmap(dpi=40);a=np.frombuffer(lo.samples,np.uint8).reshape(lo.h,lo.w,lo.n)[:,:,0]
ys,xs=np.where(a<200); s=72/40
R=xs.max()*s; B=ys.max()*s  # right/bottom of drawing in pt (frame right/bottom = sheet edge-5mm)
k=72/25.4; sc=W/ (W/100) # unused
mm=lambda v: v
# sheet scale: model units per mm
import math
u=float(sys.argv[12]) if len(sys.argv)>12 else 100.0
sr=R+5*k; sb=B+5*k   # sheet right/bottom pt
def P(x,y): return (sr-(X0+W-x)/u*k, sb-(y-Y0)/u*k)
A=P(x0,y1);Bp=P(x1,y0)
p.get_pixmap(dpi=dpi,clip=fitz.Rect(A[0],A[1],Bp[0],Bp[1])).save(out)
