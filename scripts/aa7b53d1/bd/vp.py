import ezdxf
doc=ezdxf.readfile('w.dxf')
msp=doc.modelspace()
vps=[]
for l in doc.layouts:
    if l.name=='Model': continue
    for v in l.query('VIEWPORT'):
        if v.dxf.id==1: continue
        c=v.dxf.view_center_point; h=v.dxf.view_height; w=h*v.dxf.width/v.dxf.height
        vps.append((l.name,c.x-w/2,c.y-h/2,c.x+w/2,c.y+h/2))
for l in vps: print('VP',l[0],[round(x) for x in l[1:]])
def where(x,y):
    return [n for n,a,b,c,d in vps if a<=x<=c and b<=y<=d]
for e in msp.query('ACAD_TABLE'):
    i=e.dxf.insert; print('T',e.dxf.handle,round(i.x),round(i.y),where(i.x,i.y))
for h in ['1285A9','1285AB','14E3E6']:
    e=doc.entitydb[h]; print(h,where(e.dxf.insert.x,e.dxf.insert.y))
