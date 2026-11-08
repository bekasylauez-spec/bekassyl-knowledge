p = r'D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\nodes.py'
s = open(p, encoding='utf-8').read()
def R(a, b):
    global s
    assert s.count(a) == 1, (a[:80], s.count(a)); s = s.replace(a, b)
R("TF = {", "TF = {'50Ш2': 17.5, ")
R("TW = {", "TW = {'50Ш2': 14.5, ")
R("RR = {", "RR = {'50Ш2': 26, ")
R("def bolt(g, p, d, dia, grip):", "def plt(g, o, eu, ev, u0, v0, u1, v1, t): L.append(['PLT', g] + [f(v) for v in o] + [f(v) for v in eu] + [f(v) for v in ev] + [f(u0), f(v0), f(u1), f(v1), f(t)])\ndef bolt(g, p, d, dia, grip):")
R("if r == 'A': sides.append((1, '30Б1'))\n            if r == 'M': sides.append((-1, '30Б1'))\n            if r == 'E': sides.append((-1, '30Б1'))\n            if r == 'H': sides.append((1, '30Б1'))",
  "if r == 'A': sides.append((1, '20Ш1'))\n            if r == 'M': sides.append((-1, '20Ш1'))\n            if r == 'E': sides.append((-1, '20Ш1'))\n            if r == 'H': sides.append((1, '20Ш1'))")
R("if r == 'E': sides.append((1, '60Ш3'))               # БП2 E–H on all axes\n        if r == 'H': sides.append((-1, '60Ш3'))",
  "if r == 'E': sides.append((1, '40Б1'))               # БП2 E–H on all axes\n        if r == 'H': sides.append((-1, '40Б1'))")
R("if r == 'A': sides.append((1, '40Б1'))\n            if r == 'E': sides.append((-1, '40Б1'))\n            if r == 'H': sides.append((1, '40Б1'))\n            if r == 'M': sides.append((-1, '40Б1'))",
  "if r == 'A': sides.append((1, '30Б1'))\n            if r == 'E': sides.append((-1, '30Б1'))\n            if r == 'H': sides.append((1, '30Б1'))\n            if r == 'M': sides.append((-1, '30Б1'))")
R("st = {'30Б1': 312.0, '60Ш3': 314.5, '40Б1': 309.5}[mp]", "st = {'20Ш1': 312.0, '40Б1': 314.5, '30Б1': 309.5}[mp]")
i = s.index('# ================= Р1 (узел 4)'); j = s.index('# ================= КН consoles'); s = s[:i] + s[j:]
R("zc = ztop(30000) - H['60Ш3'] / 2; z0, z1 = clearI('60Ш3', zc); z0 += 20; z1 -= 20", "zc = ztop(30000) - H['40Б1'] / 2; z0, z1 = clearI('40Б1', zc); z0 += 15; z1 -= 15")
R("box(g, [x + 9, 29995 - 200, z0], [x + 19, 30005 + 200, z1])", "box(g, [x + 3.5, 29995 - 200, z0], [x + 13.5, 30005 + 200, z1])")
R("for k in range(3): bolt(g, [x - 9, yy, (z0 + z1) / 2 + (k - 1) * 120], [1, 0, 0], 16, 28)", "for k in range(3): bolt(g, [x - 3.5, yy, (z0 + z1) / 2 + (k - 1) * 80], [1, 0, 0], 16, 17)")
R("y = R[r]; mp = '60Ш3' if r in 'FG' else '40Б1'; zt = ztop(y) - H[mp] - 24", "y = R[r]; mp = '40Б1' if r in 'FG' else '30Б1'; zt = ztop(y) - H[mp] - 24")
i = s.index('# ================= Р2 fins'); j = s.index('# ================= purlins')
s = s[:i] + open(r'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\blk_truss.py', encoding='utf-8').read() + s[j:]
R("            for by in (-40, 40):\n                if k == 10 and by * 1 == by: pass\n                bolt(g, [x + sx * 50, y + by, zb - tsup], [0, 0, 1], 16, tsup + TF['25Б1'])",
  "            for by in (WEBSIGN * -5, WEBSIGN * -30):\n                bolt(g, [x + sx * 50, y + by, zb - tsup], [0, 0, 1], 16, tsup + 10.5)")
R("        if k in (0, 8, 12, 20): sup, tsup = 'cap', 14\n        elif 8 < k < 12: sup, tsup = 'БП2', TF['60Ш3']\n        elif i in (0, 27): sup, tsup = 'БП1', TF['40Б1']\n        else: sup, tsup = 'ВП', TF['30Б1']",
  "        if k in (0, 8, 12, 20): sup, tsup = 'cap', 14\n        elif 8 < k < 12: sup, tsup = 'БП2', TF['40Б1']\n        elif i in (0, 27): sup, tsup = 'БП1', TF['30Б1']\n        else: sup, tsup = 'ВП', TF['20Ш1']")
R("L = []", "L = []\nWEBSIGN = float(open(os.path.join(gen.HERE, '_websign.txt')).read()) if os.path.exists(os.path.join(gen.HERE, '_websign.txt')) else 1.0   # +1: channel web on +Y")
i = s.index('# ================= площадка'); j = s.index('# ================= caps on the tube posts')
s = s[:i] + open(r'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\blk_plosh.py', encoding='utf-8').read() + s[j:]
open(p, 'w', encoding='utf-8').write(s)
print('patched')
