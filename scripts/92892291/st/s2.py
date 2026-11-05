import ezdxf
d=ezdxf.readfile('st.dxf')
for l in d.layouts:
  if l.name=='Model': continue
  vps=[v for v in l.query('VIEWPORT') if v.dxf.id>1]
  print(l.name, [(round(v.dxf.view_center_point.x),round(v.dxf.view_center_point.y),round(v.dxf.view_height)) for v in vps])
