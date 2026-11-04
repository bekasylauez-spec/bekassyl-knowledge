import ezdxf, re, sys
d=ezdxf.readfile("r.dxf"); m=d.modelspace()
pat=re.compile(r'[+\-±]\s?\d+,\d{3}')
out=[]
def walk(e,src):
    t=e.dxftype()
    if t=="TEXT": s=e.dxf.text; p=e.dxf.insert
    elif t=="MTEXT": s=e.plain_text(); p=e.dxf.insert
    else: return
    if pat.search(s): out.append((round(p.x),round(p.y),s.replace("\n"," ")[:60],src))
for e in m:
    t=e.dxftype()
    if t in("TEXT","MTEXT"): walk(e,"")
    elif t in("ACAD_PROXY_ENTITY","INSERT") or t.startswith("Mc"):
        try:
            for v in e.virtual_entities(): walk(v,t)
        except Exception: pass
for o in sorted(out,key=lambda o:(o[0]//20000,-o[1])): print(o)
