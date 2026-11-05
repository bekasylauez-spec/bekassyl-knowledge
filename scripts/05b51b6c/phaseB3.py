import axes,ab,os
s='3.4'; X,Y,_,_=axes.axes(s); x1,yA=X[0],Y[0]
bay=[];ax1=[]
for e in axes.E():
    if not axes.ins(e,s) or e.dxf=='SPDSCONSTRUCTIONLINE': continue
    r=[e.bb[0]-x1,e.bb[1]-yA,e.bb[2]-x1,e.bb[3]-yA]
    if r[0]>60 and r[2]<59940 and r[1]>-3000 and r[3]<300 and e.dxf in('LWPOLYLINE','DIMENSION','LINE') and e.h!='368629': bay.append(e.h)
    if r[0]>-3000 and r[2]<300 and r[1]>300 and r[3]<12100 and e.lay=='ф8_арм': ax1.append(e.h)
print(len(bay),len(ax1))
O=[{'t':'clonexf','hs':bay+['368629'],'d':[0,6075],'pre':'s34B_'}]
for k in range(1,10):
    O.append({'t':'clonexf','hs':ax1+['36865D'],'d':[6000*k+75,0],'pre':'s34_%d_'%k})
O.append({'t':'clone','h':'365360','tag':'n34','layer':'Размеры','base':[0,0],'to':[0,0]})
O.append({'t':'settext','h':'n34','s':'Шаг хомутов Х1 в лентах по осям 2...10 - как в ленте по оси 1 (см. размеры по оси 1).','w':12000})
O.append({'t':'moveto','h':'n34','to':[x1+63500,yA+11000]})
ab.run(O,'B3'); L=open(os.environ['TEMP']+'/ob_log.txt',encoding='utf-8').read(); print(L[-300:])
