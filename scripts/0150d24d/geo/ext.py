import pymupdf, glob
fs = glob.glob("\\\\192.168.0.107\\рабочка\\От Шерхан\\Завод\\Том 14 Водоподготовка ВП-В109\\Геология\\*.pdf")
print(fs)
d = pymupdf.open(fs[0])
out = r"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\0150d24d-bfed-4467-bd05-49bcb066cb82\scratchpad\geo\geo.txt"
with open(out, "w", encoding="utf-8") as f:
    f.write("PAGES %d\n" % len(d))
    for i, p in enumerate(d):
        f.write("\n=== PAGE %d\n" % (i + 1))
        f.write(p.get_text())
