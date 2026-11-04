import ezdxf,collections
def texts(d):
    m=d.modelspace(); c=collections.Counter()
    for e in m:
        t=e.dxftype()
        if t=="TEXT": c[e.dxf.text.strip()]+=1
        elif t=="MTEXT": c[e.plain_text().strip().replace("\n"," | ")]+=1
        elif t=="ACAD_PROXY_ENTITY":
            try:
                for pe in e.virtual_entities():
                    if pe.dxftype()=="TEXT": c["[px]"+pe.dxf.text.strip()]+=1
                    elif pe.dxftype()=="MTEXT": c["[px]"+pe.plain_text().strip()]+=1
            except Exception: pass
    return c
D={n:ezdxf.readfile(f"lk/lk{n}.dxf") for n in ["1.1","1.2","2","3"]}
T={n:texts(d) for n,d in D.items()}
base=T["1.1"]
for n in ["1.2","2","3"]:
    a=base-T[n]; b=T[n]-base
    print("=== only in 1.1 vs",n,len(a)); [print("  +",k[:150]) for k in list(a)[:60]]
    print("=== only in",n,len(b)); [print("  -",k[:150]) for k in list(b)[:60]]
