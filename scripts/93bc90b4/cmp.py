import fitz, numpy as np, cv2, sys, os
SP=sys.argv[1]; PDF=sys.argv[2]
orig=fitz.open(PDF)
dpi=int(sys.argv[3]) if len(sys.argv)>3 else 100
os.makedirs(f'{SP}/cmp',exist_ok=True)
def ras(page):
    pix=page.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
    return np.frombuffer(pix.samples,np.uint8).reshape(pix.h,pix.w)
for k in range(1,12):
    a=ras(orig[k+1]); b=ras(fitz.open(f'{SP}/plot/L{k}.pdf')[0])
    h=min(a.shape[0],b.shape[0]); w=min(a.shape[1],b.shape[1])
    a=a[:h,:w]; b=b[:h,:w]
    ia=(a<160).astype(np.uint8); ib=(b<160).astype(np.uint8)
    # best shift
    best=None
    for dx in range(-6,7):
        for dy in range(-6,7):
            s=np.roll(np.roll(ib,dy,0),dx,1)
            sc=(ia&s).sum()
            if best is None or sc>best[0]: best=(sc,dx,dy)
    _,dx,dy=best
    ib=np.roll(np.roll(ib,dy,0),dx,1)
    ker=np.ones((5,5),np.uint8)
    miss=ia & (1-cv2.dilate(ib,ker))   # in PDF, not in DWG
    extra=ib & (1-cv2.dilate(ia,ker))  # in DWG, not in PDF
    print(f'L{k} shape{a.shape} shift({dx},{dy}) inkPDF {ia.sum()} inkDWG {ib.sum()} missing {miss.sum()} extra {extra.sum()}')
    vis=np.full((h,w,3),255,np.uint8)
    vis[ia>0]=(170,170,170)
    vis[miss>0]=(0,0,255)
    vis[extra>0]=(255,0,0)
    cv2.imwrite(f'{SP}/cmp/L{k}.png',vis)
    np.save(f'{SP}/cmp/L{k}_miss.npy',miss)
