import ezdxf,sys
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
for t in m.query('TEXT MTEXT'):
    s=t.dxf.text if t.dxftype()=='TEXT' else t.plain_text()
    if any(k in s.lower() for k in ('схема','разрез','плит','лист','отм','блок')): print(t.dxftype(),round(t.dxf.insert.x),round(t.dxf.insert.y),s[:110].replace('\n',' '))
