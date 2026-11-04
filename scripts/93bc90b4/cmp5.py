import fitz, numpy as np, cv2, sys, os
SP=sys.argv[1]; PDF=sys.argv[2]; dpi=150
o=fitz.open(PDF); os.makedirs(SP+'/cmp5',exist_ok=True)
def ras(p):
    x=p.get_pixmap(dpi=dpi,colorspace=fitz.csGRAY); return np.frombuffer(x.samples,np.uint8).reshape(x.h,x.w)
for k in range(1,12):
    a=ras(o[k+1]); b=ras(fitz.open(f'{SP}/plotI3/L{k}.pdf')[0])
    h=min(a.shape[0],b.shape[0]); w=min(a.shape[1],b.shape[1]); a=a[:h,:w]; b=b[:h,:w]
    ia=(a<200).astype(np.uint8); ib=(b<200).astype(np.uint8)
    best=max(((ia&np.roll(np.roll(ib,dy,0),dx,1)).sum(),dx,dy) for dx in range(-3,4) for dy in range(-3,4))
    ib=np.roll(np.roll(ib,best[2],0),best[1],1)
    miss=ia&(1-cv2.dilate(ib,np.ones((11,11),np.uint8)))
    miss[:12,:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(cv2.dilate(miss,np.ones((25,25),np.uint8)))
    cl=[]
    for i in range(1,n):
        x,y,ww,hh,_=st[i]; px=int(miss[y:y+hh,x:x+ww].sum())
        if px>=40: cl.append((x,y,ww,hh,px))
    tiles=[]
    for x,y,ww,hh,px in cl:
        cx,cy=x+ww/2,y+hh/2; R=max(ww,hh)/2+60; s=72/dpi
        clip=fitz.Rect((cx-R)*s,(cy-R)*s,(cx+R)*s,(cy+R)*s); ims=[]
        for p in (o[k+1], fitz.open(f'{SP}/plotI3/L{k}.pdf')[0]):
            pm=p.get_pixmap(clip=clip,dpi=200); A=np.frombuffer(pm.samples,np.uint8).reshape(pm.h,pm.w,pm.n)[:,:,:3]; ims.append(cv2.resize(A,(220,220)))
        t=np.hstack([ims[0],np.full((220,4,3),(255,0,0),np.uint8),ims[1]]); cv2.putText(t,f'{x},{y}',(4,14),0,0.4,(0,0,255),1); tiles.append(t)
    print('L%d clusters %d'%(k,len(cl)))
    if tiles:
        rows=[np.hstack([np.pad(t,((3,3),(3,3),(0,0)),constant_values=128) for t in (tiles[i:i+4]+[np.full_like(tiles[0],255)]*(4-len(tiles[i:i+4])))]) for i in range(0,len(tiles),4)]
        cv2.imwrite(f'{SP}/cmp5/m_L{k}.png',np.vstack(rows)[:,:,::-1])
