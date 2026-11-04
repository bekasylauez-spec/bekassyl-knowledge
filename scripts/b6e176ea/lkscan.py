import ezdxf,sys,collections
from ezdxf import bbox
def txt(e):
    t=e.dxftype()
    if t=="TEXT": return e.dxf.text
    if t=="MTEXT": return e.plain_text()
    return ""
for n in ["1.1","1.2","2","3"]:
    d=ezdxf.readfile(f"lk/lk{n}.dxf"); m=d.modelspace()
    print("=====",n, collections.Counter(e.dxftype() for e in m).most_common(6))
    items=[]
    for e in m.query("TEXT MTEXT"):
        try: b=bbox.extents([e],fast=True)
        except Exception: continue
        if b.has_data: items.append((e,txt(e),b))
    st=[e for e in m.query("INSERT") if e.dxf.name=="крпкер"]
    rows=[]
    for s in st:
        bb=bbox.extents([s],fast=True); found=[]
        for e,t,b in items:
            cx=(b.extmin.x+b.extmax.x)/2; cy=(b.extmin.y+b.extmax.y)/2
            if bb.extmin.x<cx<bb.extmax.x and bb.extmin.y<cy<bb.extmax.y: found.append(t.replace("\n"," ")[:70])
        rows.append((bb.extmin.x,round(bb.extmin.y),round(s.dxf.xscale*100),found))
    for r in sorted(rows): print("  stamp x%.0f y%d sc%d"%r[:3], r[3])
    for t in m.query("ACAD_TABLE"): print("  TABLE",t.dxf.handle,[round(v) for v in t.dxf.insert][:2])
    print("  layouts",[l.name for l in d.layouts])
