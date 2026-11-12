import sys
sd = r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\b76c049c-c3b6-4782-bb03-17435529c746\scratchpad"
p = r"D:\_claude_work\otst\s4\s4_qty.py"
s = open(p, encoding="utf-8").read()
new = open(sd + r"\newblock.py", encoding="utf-8").read()
a = s.index("elements = {}\n")
b = s.index('with open(os.path.join(HERE, "s4_qty.json")')
s = s[:a] + new + s[b:]
open(p, "w", encoding="utf-8").write(s)
print("ok")
