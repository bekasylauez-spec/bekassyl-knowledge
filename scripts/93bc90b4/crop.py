import fitz, sys, numpy as np, cv2
SP=sys.argv[1]; PDF=sys.argv[2]; k=int(sys.argv[3]); x,y,w,h=map(float,sys.argv[4:8]); out=sys.argv[8]
dpi=int(sys.argv[9]) if len(sys.argv)>9 else 300
s=72/100
clip=fitz.Rect(x*s,y*s,(x+w)*s,(y+h)*s)
a=fitz.open(PDF)[k+1].get_pixmap(clip=clip,dpi=dpi)
b=fitz.open(f'{SP}/plot/L{k}.pdf')[0].get_pixmap(clip=clip,dpi=dpi)
A=np.frombuffer(a.samples,np.uint8).reshape(a.h,a.w,a.n)[:,:,:3]; B=np.frombuffer(b.samples,np.uint8).reshape(b.h,b.w,b.n)[:,:,:3]
B=cv2.resize(B,(A.shape[1],A.shape[0])); sep=np.zeros((6,A.shape[1],3),np.uint8); sep[:]=(0,0,255)
cv2.imwrite(out, np.vstack([A[:,:,::-1],sep,B[:,:,::-1]]))
