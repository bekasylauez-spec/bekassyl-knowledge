import fitz, sys, re
doc = fitz.open(sys.argv[1]); out = sys.argv[2]
for i, p in enumerate(doc):
    t = p.get_text()
    m = [k for k in ["База колонн Б1","База колонн Б2а","База колонн Б2","База колонн Б3","Узел 7","Узлы 12, 12а"] if k in t]
    if m:
        print(i, m[:2], len(re.findall(r"−t|-t", t)), "К1" in t)
for i in [int(x) for x in sys.argv[3].split(",")]:
    pix = doc[i].get_pixmap(dpi=110); pix.save(out + f"\\old_p{i}.png"); print("saved", i)
