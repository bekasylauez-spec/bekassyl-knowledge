import fitz,sys,collections
sys_=__import__("sys"); sys_.stdout.reconfigure(encoding="utf-8")
d=fitz.open(sys.argv[1])
k=25.4/72
for i,p in enumerate(d):
    c=collections.Counter(); sizes=collections.Counter(); ex={}
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines",[]):
            for s in l["spans"]:
                if not s["text"].strip(): continue
                f=s["font"]; c[f]+=1
                if f!="ISOCPEURItalic" and f not in ex: ex[f]=(s["text"][:30],round(s["bbox"][0]*k),round(s["bbox"][1]*k),round(s["size"]*k,2))
                sizes[round(s["size"]*k*0.72,1)]+=1
    print(i+1,dict(c),ex)
