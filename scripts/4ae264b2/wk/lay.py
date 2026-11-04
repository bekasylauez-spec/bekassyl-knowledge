import ezdxf,sys
d=ezdxf.readfile(sys.argv[1])
for l in d.layouts:
    if l.name=='Model': continue
    ents=list(l)
    vps=[e for e in ents if e.dxftype()=='VIEWPORT']
    print(l.name, len(ents), 'vp',[(round(v.dxf.view_center_point[0]),round(v.dxf.view_center_point[1]),round(v.dxf.view_height)) for v in vps][:4])
