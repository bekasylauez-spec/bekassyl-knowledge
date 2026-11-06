import ezdxf,collections,json
doc=ezdxf.readfile('../dxf/sch3.dxf'); msp=doc.modelspace()
R=[]
for e in msp.query('LWPOLYLINE[layer=="Размеры"]'):
    p=[(x,y) for x,y in e.get_points('xy')]
    xs=[q[0] for q in p]; ys=[q[1] for q in p]
    sh=int((min(xs)-130000)//84100); w=round(max(xs)-min(xs)); h=round(max(ys)-min(ys))
    if (w,h) in ((600,600),(700,700),(800,1200),(1200,800),(1500,800),(1000,800),(900,800)):
        R.append(dict(sh=sh,w=w,h=h,x0=min(xs),y0=min(ys),x1=max(xs),y1=max(ys),cx=(min(xs)+max(xs))/2,cy=(min(ys)+max(ys))/2,hd=e.dxf.handle))
json.dump(R,open('schcols.json','w'))
# ins of axes block per sheet
for e in msp.query('INSERT[name=="16951165"]'): print('axes',e.dxf.insert)
s1=[r for r in R if r['sh']==1]
x0=min(r['cx'] for r in s1); y0=min(r['cy'] for r in s1)
for r in sorted(s1,key=lambda r:(r['w'],r['h'],round(r['cy']),r['cx'])): print(r['w'],r['h'],round(r['cx']-x0),round(r['cy']-y0), round(r['x0']),round(r['y0']))
