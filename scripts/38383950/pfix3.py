D = 'D:\\Бекасыл КЖ КМ\\Завод_В109_КМ\\_авто\\revit\\'
s = ''
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a)); s = s.replace(a, b)
p = D + 'nodes.py'; s = open(p, encoding='utf-8').read()
rep("""for r, off in gen.CRANE:
    y = R[r]; sy = 1 if off > 0 else -1; yb = y + off""", """KN_DONE = set()                                              # rows E / H carry two consoles: the column stiffeners once per column
for r, off in gen.CRANE:
    y = R[r]; sy = 1 if off > 0 else -1; yb = y + off""")
rep("""        colstiff(g, x, y, zt - TF['40Ш1'] / 2, pr, (-1, 1), 14, True, -50.0); colstiff(g, x, y, zbm + TF['40Ш1'] / 2, pr, (-1, 1))""",
"""        if (x, y) not in KN_DONE:
            KN_DONE.add((x, y))
            for sxs in (-1, 1):                                  # slot only on a side where the Р1 +10.340 web gusset (and its rib) passes
                p1 = not ((i == 0 and sxs < 0) or (i == 27 and sxs > 0))
                colstiff(g, x, y, zt - TF['40Ш1'] / 2, pr, (sxs,), 14, True, -50.0 if p1 else None)
            colstiff(g, x, y, zbm + TF['40Ш1'] / 2, pr, (-1, 1))""")
open(p, 'w', encoding='utf-8').write(s)
p = D + 'gen.py'; s = open(p, encoding='utf-8').read()
rep("""    if (abs(x % 6000) < 1 or abs(x % 6000 - 6000) < 1) and any(abs(y - r) < 1 for r in ROWS): return y + 300.0 * (1 if yo > y else -1)""",
"""    if (abs(x % 6000) < 1 or abs(x % 6000 - 6000) < 1) and any(abs(y - r) < 1 for r in ROWS):
        sg = 1 if yo > y else -1
        rigid = abs(x) < 1 or abs(x - 162000) < 1 or (abs(y - 24000) < 1 and sg > 0) or (abs(y - 36000) < 1 and sg < 0)
        return y + sg * (460.0 if rigid else 300.0)      # БП1 / БП2 side: beyond the top cover taper (gusset not under the cover)""")
open(p, 'w', encoding='utf-8').write(s)
p = D + 'b109_11_tube_nodes.cs'; s = open(p, encoding='utf-8').read()
rep("""                            if (sy > 0) { e.Ylo = row + 316; e.Yhi = 1e9; } else { e.Ylo = -1e9; e.Yhi = row - 316; }""",
"""                            bool rigidSide = Math.Abs(xa) < 1 || Math.Abs(xa - 162000) < 1 || (row == 24000 && sy > 0) || (row == 36000 && sy < 0);
                            double yc = rigidSide ? 440 : 316;                          // БП1 / БП2: beyond the top cover where it overhangs the flange tip
                            if (sy > 0) { e.Ylo = row + yc; e.Yhi = 1e9; } else { e.Ylo = -1e9; e.Yhi = row - yc; }""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
