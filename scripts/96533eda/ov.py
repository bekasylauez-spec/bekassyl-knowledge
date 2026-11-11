import pymupdf,collections
d=pymupdf.open(r'R:\От Шерхан\Завод\Том 14 Водоподготовка ВП-В113\КМ Чертеж\227-23-П-УВПиОС-ВП-В113-КМ (Блок 1 стилі).pdf')
out=open("ov.txt","w",encoding="utf-8")
for i,pg in enumerate(d):
    sizes=collections.Counter()
    spans=[]
    for b in pg.get_text("dict")["blocks"]:
        for l in b.get("lines",[]):
            for s in l["spans"]:
                if s["text"].strip():
                    sizes[round(s["size"]/2.835,2)]+=1  # mm approx
                    spans.append((s["bbox"],s["text"],s["size"]))
    out.write(f"== P{i+1} sizes(mm-ish pt/2.835) {dict(sorted(sizes.items()))}\n")
    n=0
    for a in range(len(spans)):
        for b in range(a+1,len(spans)):
            r1=pymupdf.Rect(spans[a][0]);r2=pymupdf.Rect(spans[b][0])
            x=r1&r2
            if x.is_valid and not x.is_empty and x.width>1 and x.height>1.5 and x.get_area()>0.25*min(r1.get_area(),r2.get_area()):
                n+=1
                if n<=12: out.write(f"  OV {spans[a][1][:20]!r} {[round(v) for v in spans[a][0]]} x {spans[b][1][:20]!r} {[round(v) for v in spans[b][0]]}\n")
    out.write(f"  overlaps {n}\n")
