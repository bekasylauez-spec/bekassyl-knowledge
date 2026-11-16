import re, glob, os
base = "D:/РАБОЧКА/Bekassyl/18_КЖ жүйесі"
src = [p for p in glob.glob(base + "/*.md") if "03_" in os.path.basename(p)][0]
lines = open(src, encoding="utf-8").read().splitlines()
out = []
want = {"А","В","Г","Д","Е"}
for ln in lines:
    if ln.startswith("## "):
        sec = ln[3:].strip()[:1]
        if sec in want or sec == "Б":
            out.append(""); out.append("### " + ln[3:].strip())
        continue
    if not ln.startswith("| ") or ln.startswith("| №"):
        continue
    cells = [c.strip() for c in ln.strip().strip("|").split("|")]
    m = re.match(r"^([АБВГДЕ])(\d+)([а-я]?)$", cells[0])
    if not m: continue
    sec, num = m.group(1), int(m.group(2))
    if sec in want or (sec == "Б" and num in (6, 7, 9)):
        out.append(ln)
open(os.environ.get("OUTP","out.md"),"w",encoding="utf-8").write("\n".join(out)+"\n")
print(src)
print(len(out))
print("\n".join(l for l in out if "СҰРАҚ" in l))
