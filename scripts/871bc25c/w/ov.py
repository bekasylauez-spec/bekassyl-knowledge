import ezdxf,sys,collections
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
print('layouts',[l.name for l in d.layouts])
c=collections.Counter((e.dxftype(),e.dxf.layer) for e in m)
for k,v in sorted(c.items(),key=lambda x:-x[1])[:60]: print(v,k)
ins=collections.Counter(e.dxf.name for e in m.query('INSERT'))
print('INSERTS',ins.most_common(30))
