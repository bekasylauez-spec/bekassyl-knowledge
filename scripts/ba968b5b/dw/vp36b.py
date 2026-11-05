import ab, sys, km2_sec as K
sys.stdout.reconfigure(encoding='utf-8')
NODES={(-686779,-1743838):('А',2),(-686779,-1737838):('Б',3),(-686779,-1731838):('В',2),(-665379,-1743838):('А',2),(-665379,-1737838):('Б',3),(-665379,-1731838):('В',2)}
ops=[]
for (x,y),(row,k) in NODES.items():
    lo,hi={'А':(y-200,y+600),'В':(y-600,y+200),'Б':(y-750,y+750)}[row]
    yc=(lo+hi)/2
    E=K.listwin([x-260,lo-60,x+260,hi+60])
    outl=[e for e in E if e['t']=='LWPOLYLINE' and abs(e['e'][0]-(x-200))<3 and abs(e['e'][2]-(x+200))<3 and abs(e['e'][1]-lo)<5 and abs(e['e'][3]-hi)<5]
    nest=[e for e in E if e['t']=='INSERT' and e['lay']=='0' and (e['e'][2]-e['e'][0])>300]
    dots=[e for e in E if e['t']=='INSERT' and e['lay']=='диам20' and abs((e['e'][0]+e['e'][2])/2-x)<200 and abs((e['e'][1]+e['e'][3])/2-y)<200]
    print(row,len(outl),len(nest),len(dots))
    assert len(outl)==1 and len(dots)==8
    t=dots[0]; tc=((t['e'][0]+t['e'][2])/2,(t['e'][1]+t['e'][3])/2)
    if k==2: ys=[-360,-180,0,180,360]
    else: ys=[-710,-426,-142,142,426,710]
    pos=[(sx,yy) for sx in (-160,160) for yy in ys]+[(0,ys[0]),(0,ys[-1])]
    ops.append({'t':'erase','h':[e['h'] for e in nest]+[e['h'] for e in dots if e['h']!=t['h']]})
    for px,py in pos: ops.append({'t':'clone','h':t['h'],'base':[0,0],'to':[x+px-tc[0],yc+py-tc[1]]})
    ops.append({'t':'erase','h':[t['h']]})
    o=outl[0]
    ops.append({'t':'clone','h':o['h'],'base':[0,0],'to':[0,0],'tag':'in_%d_%d'%(x,y)})
    pts=o['pts']
    for i,(px,py) in enumerate(pts[:4]):
        ops.append({'t':'movept','h':'in_%d_%d'%(x,y),'idx':i,'d':[-20 if px>x else 20, -20 if py>yc else 20]})
print(ab.run(ops+[{'t':'save'}],'v36b',600)[-300:])
