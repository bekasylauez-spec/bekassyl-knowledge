import sys
P = r'D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\nodes.py'
s = open(P, encoding='utf-8').read()
a = s.index("# ---- end plate (фланец) of a member along Y")
b = s.index("# ================= БП2 ridge splice")
new = open(sys.argv[1], encoding='utf-8').read()
s = s[:a] + new + s[b:]
a = s.index("# ================= СФ caps −20 + 4 bolts"); b = s.index("# ================= Р2 □100x3 ends")
s = s[:a] + open(sys.argv[2], encoding='utf-8').read() + s[b:]
open(P, 'w', encoding='utf-8').write(s)
print('ok')
