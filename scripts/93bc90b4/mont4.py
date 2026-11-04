import fitz, sys, numpy as np, cv2
SP=sys.argv[1]; PDF=sys.argv[2]; KIND=sys.argv[3]; ONLY=[int(x) for x in sys.argv[4].split(',')]
orig=fitz.open(PDF)
for k in ONLY:
    m=np.load(f'{SP}/cmp4/L{k}_{KIND}.npy'); m[:16,:]=0
    H,W=m.shape
    # skip stamp corner region (logo, stamp) bottom-right 300x260 px
    dm=cv2.dilate(m,np.ones((31,31),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(dm)
    tiles=[]
    pa=orig[k+1]; pb=fitz.open(f'{SP}/plotMM/L{k}.pdf')[0]
    for i in range(1,n):
        x,y,w,h,a=st[i]
        if m[y:y+h,x:x+w].sum()<80: continue
        if x>W-640 and y>H-520: continue
        cx,cy=x+w/2,y+h/2; R=max(w,h)/2+80
        s=72/200; clip=fitz.Rect((cx-R)*s,(cy-R)*s,(cx+R)*s,(cy+R)*s)
        imgs=[]
        for p in (pa,pb):
            px=p.get_pixmap(clip=clip,dpi=int(200*120/(2*R*2)) if R>120 else 200)
            A=np.frombuffer(px.samples,np.uint8).reshape(px.h,px.w,px.n)[:,:,:3]
            imgs.append(cv2.resize(A,(240,240)))
        t=np.hstack([imgs[0],np.full((240,4,3),(255,0,0),np.uint8),imgs[1]])
        cv2.putText(t,f'{int(x)},{int(y)}',(5,15),0,0.45,(0,0,255),1)
        tiles.append(t)
    if not tiles: print(k,'none'); continue
    rows=[]
    for i in range(0,len(tiles),4):
        r=tiles[i:i+4]
        while len(r)<4: r.append(np.full_like(tiles[0],255))
        rows.append(np.hstack([np.pad(t,((4,4),(4,4),(0,0)),constant_values=128) for t in r]))
    cv2.imwrite(f'{SP}/cmp4/m_{KIND}_L{k}.png',np.vstack(rows)[:,:,::-1])
    print(k,len(tiles))
