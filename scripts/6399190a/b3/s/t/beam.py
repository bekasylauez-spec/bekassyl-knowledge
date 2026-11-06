import ext,ab,os,math
E=ext.load('w/ext.txt')
O=[]
for dx in (0.0,28154.22):
    cx=-477952.277+dx; yb=-1739685.71; yt=-1737685.71
    W=(cx-2700,-1742500,cx+2700,-1736900)
    ins=lambda e: e.bb and W[0]<e.cx<W[2] and W[1]<e.cy<W[3]
    S=[e for e in E if ins(e)]
    circ=[e for e in S if e.dxf=='CIRCLE' and e.lay.startswith('диам')]
    blk=[e for e in S if e.dxf=='INSERT' and 'Хомут' in e.info][0]
    dims=[e for e in S if e.dxf=='DIMENSION']
    # stretch halves
    O.append({'t':'stretchwin','win':[cx+100,-1742000,cx+3200,-1736500],'d':[125,0]})
    O.append({'t':'stretchwin','win':[cx-3200,-1742000,cx-100,-1736500],'d':[-125,0]})
    # center bars: move to -417/... ; clone extra
    xs=[cx-625,cx-208.33,cx+208.33,cx+625]
    for c in circ:
        x,y=float(c.kv['ci'].split(',')[0]),float(c.kv['ci'].split(',')[1])
        O.append({'t':'erase','h':[c.h]})
    for y in (yt,yb):
        for x in xs: O.append({'t':'circle','c':[x,y],'r':62.5,'layer':'диам20'})
    for x in (cx-625,cx+625): O.append({'t':'circle','c':[x,(yt+yb)/2],'r':50,'layer':'диам20'})
    # stirrups
    O.append({'t':'dyn','h':blk.h,'prop':'Расстояние1','value':1250})
    tg='x2_%d'%int(dx)
    O.append({'t':'clone','h':blk.h,'tag':tg,'base':[cx-625,yb],'to':[cx-208.33,yb]})
    O.append({'t':'dyn','h':tg,'prop':'Расстояние1','value':416.67})
    # bottom chain 50|100|100|50 -> 50|3x83=250|50
    ch=[d for d in dims if d.kv.get('meas') in ('100',) and abs(d.dimpts()[0][1]-yb)<5]
    ch.sort(key=lambda d:min(d.dimpts()[0][0],d.dimpts()[1][0]))
    if len(ch)==2:
        p=ch[0].dimpts()
        O.append({'t':'dimpts','h':ch[0].h,'p1':[cx-625,yb],'p2':[cx+625,yb],'dl':list(p[2])})
        O.append({'t':'dimtext','h':ch[0].h,'s':'3х83=250'}); O.append({'t':'erase','h':[ch[1].h]})
    print(dx,len(circ),blk.h,len(ch))
O.append({'t':'save'})
ab.run(O,'beam'); print(open(os.environ['TEMP']+'/ab_log.txt',encoding='utf-8').read()[-400:])
