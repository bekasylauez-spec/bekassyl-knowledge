import fitz,sys,os
d=fitz.open(sys.argv[1])
for i,p in enumerate(d):
    r=p.rect
    W=r.width/72*25.4
    nx = 1 if W<300 else (2 if W<450 else (3 if W<650 else 4))
    ny = 1 if r.height/72*25.4<300 else 2
    if W<300: ny=2
    for ix in range(nx):
        for iy in range(ny):
            clip=fitz.Rect(r.x0+r.width*ix/nx, r.y0+r.height*iy/ny, r.x0+r.width*(ix+1)/nx, r.y0+r.height*(iy+1)/ny)
            pix=p.get_pixmap(dpi=180,clip=clip)
            pix.save(f"t/p{i+1:02d}_{iy}{ix}.png")
    pix=p.get_pixmap(dpi=40); pix.save(f"t/p{i+1:02d}_all.png")
