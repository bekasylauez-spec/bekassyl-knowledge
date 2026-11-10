import ezdxf,collections,sys
d=ezdxf.readfile("D:/_claude_work/v113/ozh/ozh_km.dxf")
msp=d.modelspace()
print("ver",d.dxfversion,"units",d.header.get('$INSUNITS'))
print("layouts",d.layouts.names_in_taborder())
c=collections.Counter(e.dxftype() for e in msp);print(c)
ins=collections.Counter(e.dxf.name for e in msp if e.dxftype()=='INSERT');print(ins.most_common(40))
for l in d.layouts:
    if l.name!='Model':
        print(l.name,l.dxf.paper_width if hasattr(l.dxf,'paper_width') else '',len(list(l.viewports())),collections.Counter(e.dxftype() for e in l).most_common(5))
