import json,numpy as np
from scipy import ndimage
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
S=r'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\0c44a278-d609-485d-a50c-02efd03030b0\scratchpad\w'
AXX={'3':12000,'4':18000,'5':24000,'6':30000,'7':36000,'8':42000,'9':47500,'10':53500,'11':59500,'12':65900,'13':73100,'14':73750}
AXY={'А':0,'Б':9000,'В':13900,'Г':21000,'Д':27500,'Е':36000,'Ж':39000}
SCH=json.load(open(S+r'\scheme.json'))
def beams(z):
    R=SCH[z]; out=[]
    for pts,cl in R['dash']+R['solid']:
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        if len(pts)==4: out.append((min(xs),min(ys),max(xs),max(ys)))
    return out
def holes_from_lira(z):
    g=np.load(S+r'\g%s.npy'%z.replace('.','')); h=50; x0=12000; y0=0
    lab,n=ndimage.label(~g); res=[]
    for k in range(1,n+1):
        jj,ii=np.where(lab==k); a=len(jj)*h*h/1e6
        if a<1.0 and not (0.70<a*1e6/((ii.max()-ii.min()+1)*(jj.max()-jj.min()+1)*h*h)<0.86): continue
        if jj.min()==0 or ii.min()==0 or jj.max()==g.shape[0]-1 or ii.max()==g.shape[1]-1: continue
        bx=(x0+ii.min()*h,y0+jj.min()*h,x0+(ii.max()+1)*h,y0+(jj.max()+1)*h)
        fill=a*1e6/((bx[2]-bx[0])*(bx[3]-bx[1]))
        res.append(dict(bbox=bx,area=a,fill=fill))
    return res
def snap(v,faces,tol=400):
    best=None
    for f in faces:
        if abs(f-v)<=tol and (best is None or abs(f-v)<abs(best-v)): best=f
    return best if best is not None else round(v/50)*50
def slab(z):
    B=beams(z)
    if z=='7.0':
        outer=Polygon([(11750,-250),(73350,-250),(73350,16050),(36250,16050),(36250,25500),(73350,25500),(73350,39250),(59250,39250),(59250,36250),(42250,36250),(42250,39250),(40500,39250),(40500,36250),(11750,36250)])
    else:
        outer=box(11750,-250,30250,9250)
    holes=[]
    for H in holes_from_lira(z):
        x0,y0,x1,y1=H['bbox']
        if z=='7.0' and x0>31000 and x1<35500 and y0>16000: # opening 6-7 by beams
            holes.append(dict(kind='rect',geom=box(31375,16050,34750,26375))); continue
        if 0.70<H['fill']<0.86 and abs((x1-x0)-(y1-y0))<300 and (x1-x0)>500:
            c=((x0+x1)/2,(y0+y1)/2); d=round(max(x1-x0,y1-y0)/50)*50
            holes.append(dict(kind='circle',c=(round(c[0]/50)*50,round(c[1]/50)*50),d=d,geom=Point(round(c[0]/50)*50,round(c[1]/50)*50).buffer(d/2,64)))
        else:
            fx=[b[0] for b in B]+[b[2] for b in B]; fy=[b[1] for b in B]+[b[3] for b in B]
            r=(snap(x0,fx,150),snap(y0,fy,150),snap(x1,fx,150),snap(y1,fy,150))
            holes.append(dict(kind='rect',geom=box(*r)))
    g=outer
    for h in holes: g=g.difference(h['geom'])
    return dict(outer=outer,holes=holes,geom=g,beams=B)
if __name__=='__main__':
    for z in ('7.0','4.5'):
        s=slab(z); print(z,'area m2',round(s['geom'].area/1e6,2))
        for h in s['holes']: print('  ',h['kind'],[round(v) for v in h['geom'].bounds], h.get('d',''), round(h['geom'].area/1e6,2))
