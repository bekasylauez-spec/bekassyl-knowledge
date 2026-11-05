import axes,grid,ab,json,os,sys
OU,NU=grid.old_u(),grid.new_u(); OP,NP=grid.prep(OU),grid.prep(NU)
O=[]; info=[]
for s,withP in (('3.1',1),('1.3',1),('3.2',0),('3.3',0),('3.4',0)):
    X,Y,H,V=axes.axes(s); X=[x for x in X if any(abs(abs(x-x2)-6000)<1 for x2 in X)]; x1,yA=X[0],Y[0]
    a,b,c,d=axes.SH[s]
    oldU=[];oldP=[]
    for e in axes.E():
        if not axes.ins(e,s) or e.dxf!='LWPOLYLINE' or e.lay!='Размеры': continue
        pts=[(p[0]-x1,p[1]-yA) for p in e.plpts()]
        if len(pts)<2: continue
        if grid.on(pts,OU): oldU.append(e.h)
        elif grid.on(pts,OP): oldP.append(e.h)
    info.append((s,len(oldU),len(oldP)))
    for k,(src,G) in enumerate([(oldU,NU)]+([(oldP,NP)] if withP else [])):
        for i,r in enumerate(grid.rings(G)):
            tag='g%s_%d_%d'%(s.replace('.',''),k,i)
            O.append({'t':'clone','h':src[0],'tag':tag})
            O.append({'t':'plset','h':tag,'p':[[x+x1,y+yA] for x,y in r],'closed':True})
    O.append({'t':'erase','h':oldU+(oldP if withP else [])})
print(info)
if len(sys.argv)>1:
    ab.run(O,'B1'); print(open(os.environ['TEMP']+'/ob_log.txt',encoding='utf-8').read()[-400:])
