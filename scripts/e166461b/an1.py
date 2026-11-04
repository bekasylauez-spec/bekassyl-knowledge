import ezdxf, sys, collections
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
c=collections.Counter(); lay=collections.Counter()
for e in m:
    c[e.dxftype()]+=1; lay[(e.dxf.layer,e.dxftype())]+=1
print(c.most_common())
for k,v in sorted(lay.items(), key=lambda x:-x[1])[:60]: print(v,k)
print([l.layout_key for l in d.layouts], [l.name for l in d.layouts])
ext=ezdxf.bbox.extents(m, fast=True); print(ext)
