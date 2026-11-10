import ezdxf,collections,sys
sys.stdout.reconfigure(encoding='utf-8')
d=ezdxf.readfile("D:/_claude_work/v113/ozh/ozh_km.dxf")
msp=d.modelspace()
st=[e for e in msp if e.dxf.layer=='1Штамп']
for e in st:
    if e.dxftype()=='LWPOLYLINE': print('LW',[tuple(round(v) for v in p) for p in e.get_points('xy')],e.dxf.get('const_width'))
    if e.dxftype()=='MTEXT': print('MT',e.dxf.insert,e.text[:80])
xs=[]
for e in st:
    if e.dxftype()=='LINE':
        a,b=e.dxf.start,e.dxf.end
        if abs(a.x-b.x)>100 or abs(a.y-b.y)>100: xs.append((round(a.x),round(a.y),round(b.x),round(b.y)))
print(len(xs)); 
for x in sorted(xs)[:60]: print(x)
