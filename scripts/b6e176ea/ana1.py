import ezdxf,collections
from ezdxf import bbox
d=ezdxf.readfile("w/cur.dxf"); m=d.modelspace()
c=collections.Counter()
for e in m:
    t=e.dxftype()
    if t=="ACAD_PROXY_ENTITY":
        t+=":"+str(e.dxf.get("original_class_name", "")) if e.dxf.hasattr("original_class_name") else t
    c[t]+=1
print(c.most_common())
# stamp inserts
for e in m.query("INSERT"):
    if e.dxf.name.lower().startswith("крпкер") or "штамп" in e.dxf.name.lower():
        print(e.dxf.name,e.dxf.handle,[round(v) for v in e.dxf.insert][:2],e.dxf.xscale)
