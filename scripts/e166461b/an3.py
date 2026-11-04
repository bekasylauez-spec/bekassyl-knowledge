import ezdxf, sys
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
for e in m:
    if e.dxftype() in ('TEXT','MTEXT'):
        t=e.dxf.text if e.dxftype()=='TEXT' else e.plain_text()
        h=e.dxf.height if e.dxftype()=='TEXT' else e.dxf.char_height
        if h>150 or any(k in t.lower() for k in ('план','отм','этаж','разрез','схема')): print(e.dxftype(),[round(x) for x in e.dxf.insert][:2],round(h),repr(t[:120]))
