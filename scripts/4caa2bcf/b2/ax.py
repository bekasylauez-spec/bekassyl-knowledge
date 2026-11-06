import ezdxf, collections, json
d=ezdxf.readfile('sch.dxf'); m=d.modelspace()
res={}
for ins in m.query('INSERT[name=="15616169"]'):
    ve=list(ins.virtual_entities())
    circ=[e for e in ve if e.dxftype()=='CIRCLE']; txt=[e for e in ve if e.dxftype()=='TEXT']
    lab={}
    for t in txt:
        c=min(circ,key=lambda c:(c.dxf.center[0]-t.dxf.insert[0])**2+(c.dxf.center[1]-t.dxf.insert[1])**2)
        lab[t.dxf.text]=(round(c.dxf.center[0]),round(c.dxf.center[1]))
    res[round(ins.dxf.insert[0])]=lab
k=sorted(res)[2]; lab=res[k]; print(k, lab)
# columns on that sheet: 4-pt polylines in frame x 304017..388117
cols=[]
for e in m.query('LWPOLYLINE[layer=="Размеры"]'):
    p=e.get_points('xy')
    if len(p)!=4: continue
    xs=[q[0] for q in p]; ys=[q[1] for q in p]
    if 304017<min(xs)<388117:
        cols.append((round(min(xs)),round(min(ys)),round(max(xs)),round(max(ys))))
print(len(cols)); print(sorted(set((c[2]-c[0],c[3]-c[1]) for c in cols)))
json.dump(dict(lab=lab,cols=cols),open('ax23.json','w'),ensure_ascii=False)
