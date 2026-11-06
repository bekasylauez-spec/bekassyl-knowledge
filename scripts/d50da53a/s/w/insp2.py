import ezdxf,sys,collections
d=ezdxf.readfile(sys.argv[1]); ms=d.modelspace()
for e in ms.query('INSERT'): print('I',e.dxf.name,e.dxf.layer,[round(v) for v in e.dxf.insert][:2],round(e.dxf.xscale,3))
for l in d.layouts:
    if l.name=='Model': continue
    c=collections.Counter(e.dxftype() for e in l)
    if len(l)>0: print('L',l.name,dict(c))
big=sorted(((len(b),b.name) for b in d.blocks if not b.name.startswith('*')),reverse=True)[:15]; print(big)
