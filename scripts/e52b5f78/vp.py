import ezdxf,sys,json
n=sys.argv[1]
d=ezdxf.readfile(f"dx/{n}.dxf")
res={}
for l in d.layouts:
    if l.name=='Model': continue
    for v in l.query('VIEWPORT'):
        if v.dxf.id==1: continue
        c=v.dxf.view_center_point; h=v.dxf.view_height; w=h*v.dxf.width/v.dxf.height
        res.setdefault(l.name,[]).append([round(c.x-w/2),round(c.y-h/2),round(c.x+w/2),round(c.y+h/2),round(h/v.dxf.height,2),round(v.dxf.width),round(v.dxf.height)])
json.dump(res,open(f"dx/{n}_vp.json","w"),ensure_ascii=False)
for k,v in res.items(): print(k,v)
