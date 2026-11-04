import numpy as np, cv2, sys
SP=sys.argv[1]
for k in range(1,12):
    m=np.load(f'{SP}/cmp/L{k}_miss.npy')
    dm=cv2.dilate(m,np.ones((15,15),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(dm)
    cl=[]
    for i in range(1,n):
        x,y,w,h,a=st[i]
        px=int(m[y:y+h,x:x+w].sum())
        if px>=25: cl.append((px,x,y,w,h))
    cl.sort(reverse=True)
    print(f'L{k}: clusters {len(cl)}', [(c[0],c[1],c[2],c[3],c[4]) for c in cl[:12]])
