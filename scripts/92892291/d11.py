import axes,sys
for s in sys.argv[1:]:
    X,Y,H,V=axes.axes(s)
    X=[x for x in X if any(abs(abs(x-x2)-6000)<1 for x2 in X)]
    x1,yA=X[0],Y[0]
    print(s,'x1',x1,'yA',yA)
    for e in axes.E():
        if axes.ins(e,s) and e.dxf=='LWPOLYLINE' and e.lay=='Размеры' and e.bb[2]-e.bb[0]>30000:
            pts=[(round(p[0]-x1),round(p[1]-yA)) for p in e.plpts()]
            print(' ',e.h,len(pts),pts[:14])
