import ezdxf,collections,json
d=ezdxf.readfile('s4.dxf'); m=d.modelspace()
AX={0:'32',650:'33',6650:'34',12650:'35',18650:'36',24850:'37',31850:'38',38850:'39',44850:'40'}
AY={0:'А',9000:'Б',13900:'В',21000:'Г',27500:'Д',36000:'Е',39000:'Ж'}
out={}
for sh,ox in (('2.2',84100),('2.3',168200),('2.4',252300)):
  R=[]
  for e in m.query('LWPOLYLINE'):
    if not e.closed: continue
    p=[(x-ox-145817,y+1786760) for x,y,*_ in e.get_points()]
    xs=[a for a,b in p]; ys=[b for a,b in p]
    if min(xs)<-3000 or max(xs)>48000 or min(ys)<-3000 or max(ys)>42000: continue
    R.append(dict(c=e.dxf.color,x0=round(min(xs)),y0=round(min(ys)),x1=round(max(xs)),y1=round(max(ys)),n=len(p)))
  out[sh]=R
  cc=collections.Counter(r['c'] for r in R); print(sh,cc)
json.dump(out,open('rects.json','w'))
