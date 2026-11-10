import sys, fitz
d = fitz.open(sys.argv[1]); print("pages", len(d)); print(d.metadata)
for i in range(min(2, len(d))):
    t = d[i].get_text(); print("--- page", i+1, "textlen", len(t)); print(t[:600])
d[0].get_pixmap(dpi=70).save(sys.argv[2] + r"\p1.png")
