import ezdxf, sys, collections
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
for e in m.query('INSERT'):
    b=d.blocks[e.dxf.name]; c=collections.Counter(x.dxftype() for x in b)
    print(e.dxf.name, round(e.dxf.insert.x), round(e.dxf.insert.y), e.dxf.xscale, e.dxf.layer, dict(c))
for e in m.query('TEXT MTEXT HATCH LINE'):
    if e.dxftype()=='HATCH': print('H',e.dxf.layer, e.dxf.pattern_name); continue
    if e.dxftype()=='LINE': print('L',e.dxf.layer, e.dxf.start, e.dxf.end); continue
    t=e.dxf.text if e.dxftype()=='TEXT' else e.text
    print(e.dxftype(), e.dxf.layer, round(e.dxf.insert.x), round(e.dxf.insert.y), t[:60])
print(collections.Counter(e.dxftype() for e in d.entities))
