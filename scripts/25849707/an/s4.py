import ezdxf,collections,json
d=ezdxf.readfile('sch.dxf'); m=d.modelspace()
OX0,OY=141317,-1773284
res={}
for k in range(4):
    OX=OX0+84100*k
    R={'beam':[],'col':[],'other':[]}
    for e in m.query('LWPOLYLINE'):
        p=list(e.get_points('xy'))
        if len(p)!=4 or not e.closed: continue
        xs=[a[0]-OX for a in p]; ys=[a[1]-OY for a in p]
        if not(-3000<min(xs)<80000 and -3000<min(ys)<42000): continue
        r=[round(min(xs)),round(min(ys)),round(max(xs)),round(max(ys))]
        if e.dxf.linetype=='невидимая': R['beam'].append(r)
        elif e.dxf.layer=='柱': R['col'].append(r)
        else: R['other'].append(r)
    res[k]=R
    print(k,{a:len(b) for a,b in R.items()})
json.dump(res,open('rects.json','w'))
# sample columns sizes
for k in range(4):
    c=collections.Counter((r[2]-r[0],r[3]-r[1]) for r in res[k]['other']); print(k,'other',c.most_common(12))
    c=collections.Counter((r[2]-r[0],r[3]-r[1]) for r in res[k]['col']); print(k,'col',c.most_common(12))
