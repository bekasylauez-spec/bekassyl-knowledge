import ezdxf,sys
d=ezdxf.readfile(sys.argv[1])
for l in d.layouts:
    if l.name=='Model': continue
    for v in l.query('VIEWPORT'):
        if v.dxf.id==1: continue
        c=v.dxf.view_center_point; h=v.dxf.view_height; w=v.dxf.width; ph=v.dxf.height
        sc=h/ph if ph else 0
        print(l.name, 'center',round(c.x),round(c.y),'win',round(w*sc),round(h),'scale',round(sc,2))
