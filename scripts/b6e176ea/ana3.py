import ezdxf,json
from ezdxf import bbox
d=ezdxf.readfile("w/cur.dxf"); m=d.modelspace()
stamps=[e for e in m.query("INSERT") if e.dxf.name=="крпкер"]
sb=[(st,bbox.extents([st],fast=True)) for st in stamps]
fr={}
for e in m:
    if e.dxftype() not in("ACAD_PROXY_ENTITY","LWPOLYLINE"): continue
    try: b=bbox.extents([e],fast=True)
    except Exception: continue
    if not b.has_data: continue
    w=b.extmax.x-b.extmin.x
    for st,s in sb:
        if b.extmin.x-1<=s.extmin.x and b.extmax.x+1>=s.extmax.x and b.extmin.y-1<=s.extmin.y and b.extmax.y>s.extmax.y+10 and w< (s.extmax.x-s.extmin.x)*4:
            k=st.dxf.handle
            if k not in fr or w>fr[k][2]-fr[k][0]:
                fr[k]=[b.extmin.x,b.extmin.y,b.extmax.x,b.extmax.y,e.dxftype(),e.dxf.handle]
out=[]
for st,s in sorted(sb,key=lambda p:p[1].extmin.x):
    f=fr.get(st.dxf.handle); print(st.dxf.handle,round(st.dxf.xscale*100),[round(v) for v in f[:4]] if f else None,f[4:] if f else "", round((f[2]-f[0])/st.dxf.xscale/100,1) if f else "",round((f[3]-f[1])/st.dxf.xscale/100,1) if f else "")
    out.append([st.dxf.handle,st.dxf.xscale*100]+(f[:4] if f else []))
json.dump(out,open("w/frames.json","w"))
