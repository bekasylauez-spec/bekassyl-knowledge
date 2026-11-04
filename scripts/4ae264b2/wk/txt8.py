import ezdxf,sys,re
d=ezdxf.readfile(sys.argv[1])
pat=re.compile(sys.argv[2])
for sp in [d.modelspace()]+[l for l in d.layouts if l.name!='Model']:
    for e in sp:
        if e.dxftype() in ('TEXT','MTEXT'):
            t=e.dxf.text if e.dxftype()=='TEXT' else e.plain_text()
            if pat.search(t): print(sp.name if hasattr(sp,'name') else 'M', e.dxftype(), repr(t[:80]), (round(e.dxf.insert.x),round(e.dxf.insert.y)))
