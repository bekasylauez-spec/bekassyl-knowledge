import os
S = os.environ["SCRATCH"]
parts = ["c01.md","c02.md","c03.md","c04.md","c05.md","c06.md","c07.md","c08.md","c09.md","c10.md","c11.md","c12.md"]
text = ""
for p in parts:
    text += open(os.path.join(S,p), encoding="utf-8").read()
chk = open(os.path.join(S,"_part_checklist.md"), encoding="utf-8").read().strip()
text = text.replace("@@CHECKLIST@@", chk)
dst = "D:/_claude_work/Kasymova/revit/_rules/obsidian_rules.md"
os.makedirs(os.path.dirname(dst), exist_ok=True)
open(dst, "w", encoding="utf-8", newline="\n").write(text)
print("lines", text.count("\n"), "bytes", len(text.encode("utf-8")))
