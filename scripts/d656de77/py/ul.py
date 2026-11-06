import sys,os,re; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from common import *
import ezdxf
f=gx.S+r'\w\tmp2.dxf'; gx.run([dict(t='dxfout',file=f)],'dx')
doc=ezdxf.readfile(f); ops=[]
for e in doc.modelspace().query('MTEXT'):
    x,y=e.dxf.insert[0],e.dxf.insert[1]
    if not (SX(0)<=x<=SX(4)+31500 and Y0<=y<=Y0+14850): continue
    t=e.text
    if re.match(r'^(Ригель Рм-\d|Разрез \d - \d)$',t) and y>Y0+5000:
        ops.append(dict(t='settext',h=e.dxf.handle,s='{\L'+t+'}')); print(e.dxf.handle,round(x),round(y),t)
r,lg,er=run(ops,'ul'); print(len(ops),er)
