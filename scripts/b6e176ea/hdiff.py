import ezdxf,sys,collections,json
from ezdxf import bbox
F=json.load(open("lk/frames.json"))
def sheet(b):
    if b is None: return "?"
    cx=(b.extmin.x+b.extmax.x)/2; cy=(b.extmin.y+b.extmax.y)/2
    for k,(x1,y1,x2,y2,sc,f) in F.items():
        if x1<=cx<=x2 and y1<=cy<=y2: return k
    return "out"
def sig(e):
    t=e.dxftype(); s=[t,e.dxf.layer]
    try:
        b=bbox.extents([e],fast=True)
        if b.has_data: s+= [round(b.extmin.x),round(b.extmin.y),round(b.extmax.x),round(b.extmax.y)]
    except Exception: pass
    if t=="TEXT": s.append(e.dxf.text)
    if t=="MTEXT": s.append(e.text[:80])
    if t=="ACAD_PROXY_ENTITY": s.append(len(e.proxy_graphic or b''))
    return s
def load(n):
    d=ezdxf.readfile(f"lk/lk{n}.dxf"); r={}
    for e in d.modelspace():
        try: b=bbox.extents([e],fast=True); b=b if b.has_data else None
        except Exception: b=None
        r[e.dxf.handle]=(e,sig(e),b)
    return r
a=load(sys.argv[1]); b=load(sys.argv[2])
new=[h for h in a if h not in b]; gone=[h for h in b if h not in a]
mod=[h for h in a if h in b and a[h][1]!=b[h][1]]
print("in",sys.argv[1],"not in",sys.argv[2],":",len(new),"| missing:",len(gone),"| modified:",len(mod))
for title,L,src in (("NEW in A",new,a),("GONE from A",gone,b),("MODIFIED",mod,a)):
    c=collections.Counter((sheet(src[h][2]),src[h][1][0]) for h in L)
    print(title, sorted(c.items()))
if len(sys.argv)>3:
    for title,L,src in (("NEW",new,a),("GONE",gone,b),("MOD",mod,a)):
        for h in L:
            s=sheet(src[h][2])
            if s in sys.argv[3].split(","):
                x=src[h][1]; y=b[h][1] if (title=="MOD") else ""
                print(title,s,h,x[0],x[1],x[2:7],"|", y[2:7] if y else "")
