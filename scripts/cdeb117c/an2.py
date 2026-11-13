import ezdxf
doc=ezdxf.readfile('D:/_claude_work/maftun/src/fv.dxf')
for s in doc.styles:
    if s.dxf.name in('Standard','стиль1','ГОСТ 2.304','Isocpeur','СПДС'): print(s.dxf.name,s.dxf.font,s.dxf.height,s.dxf.width)
for d in doc.dimstyles:
    if d.dxf.name in ('СПДС',): print({k:d.dxf.get(k) for k in ('dimtxt','dimscale','dimtxsty','dimasz','dimexo','dimexe','dimgap','dimtad','dimlfac','dimclrt')})
