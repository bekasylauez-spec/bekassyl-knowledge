import ezdxf,collections,sys
sys.stdout.reconfigure(encoding='utf-8')
d=ezdxf.readfile("D:/_claude_work/v113/ozh/ozh_km.dxf")
msp=d.modelspace()
x0,y0,x1,y1=193900,110030,235900,139730
T=[]
for e in msp:
    if e.dxftype()=='TEXT':
        p=e.dxf.insert
        if x0<=p.x<=x1 and y0<=p.y<=y1: T.append((e.dxf.text,round(p.x),round(p.y)))
xs=sorted(set(t[1] for t in T))
print([ (t[1]) for t in T if t[0] in('Лист','Наименование','Примечание')])
for t in sorted(T,key=lambda t:(t[1]//4000, -t[2])): print(t)
