import ezdxf,sys,collections
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
c=collections.Counter(e.dxftype() for e in m); print(c.most_common())
print('layouts',[l.name for l in d.layouts])
# frames: block inserts with name containing Штамп / формат
bi=collections.Counter(e.dxf.name for e in m if e.dxftype()=='INSERT'); print(bi.most_common(40))
ly=collections.Counter(e.dxf.layer for e in m); print(ly.most_common(60))
