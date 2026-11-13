import ezdxf,collections
doc=ezdxf.readfile('D:/_claude_work/maftun/src/fv.dxf'); msp=doc.modelspace()
secs={'1-1':(1073800,1075000),'2-2':(1082300,1083500),'3-3':(1091100,1091900),'4-4':(1099600,1100400)}
for n,(a,b) in secs.items():
    rungs=[];stubs=[]
    for e in msp:
        if e.dxftype()!='LWPOLYLINE' or not e.closed: continue
        p=[tuple(float(v) for v in q[:2]) for q in e.get_points()]
        xs=[q[0] for q in p];ys=[q[1] for q in p]
        if not(a<=min(xs) and max(xs)<=b and 106000<=min(ys) and max(ys)<=123500): continue
        h=max(ys)-min(ys);w=max(xs)-min(xs)
        if abs(h-80)<1: (rungs if w>300 else stubs).append((round((min(ys)+max(ys))/2-106116),round(min(xs)),round(w),e.dxf.layer))
    print(n,'rungs',sorted(r[0] for r in rungs))
    print('  stubs',sorted(stubs))
