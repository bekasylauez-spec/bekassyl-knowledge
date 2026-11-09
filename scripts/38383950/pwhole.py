D = 'D:\\Бекасыл КЖ КМ\\Завод_В109_КМ\\_авто\\revit\\'
s = ''
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a)); s = s.replace(a, b)
p = D + 'nodes.py'; s = open(p, encoding='utf-8').read()
rep("def colstiff(g, x, y, z, prof, sides, t=14, wtop=True, slot0=-8.0):", "def colstiff(g, x, y, z, prof, sides, t=14, wtop=True, slot0=None):")
rep("        for ya, yb in ((y - yi, y + slot0), (y + 22, y + yi)):",
    "        # one whole plate; a slot (web gusset y+4…+14 passes through) only where asked (user 09.11: «целый лист болмайма»)\n        for ya, yb in (((y - yi, y + yi),) if slot0 is None else ((y - yi, y + slot0), (y + 22, y + yi))):")
open(p, 'w', encoding='utf-8').write(s)
p = D + 'b109_11_tube_nodes.cs'; s = open(p, encoding='utf-8').read()
rep("""                    foreach (var yy in new[] { new[] { yr - chf + ctf + 29, yr + 2 }, new[] { yr + 16, yr + chf - ctf - 29 } })   // clear of the root fillets (r 28)""",
    """                    foreach (var yy in new[] { new[] { yr - chf + ctf + 29, yr + chf - ctf - 29 } })   // one whole rib (the gusset ends under / over it), clear of the root fillets (r 28)""")
open(p, 'w', encoding='utf-8').write(s)
p = D + 'gen.py'; s = open(p, encoding='utf-8').read()
rep("""for (xa, ya, xb, yb) in gs:
    a, b = [xa, ya, ztop(ya) - GSZ], [xb, yb, ztop(yb) - GSZ]""",
"""ROWS = (0.0, 24000.0, 36000.0, 60000.0)
def gs_off(x, y, yo):          # user 09.11 (photos 2 / 3): over a К1 the ГС1 node goes 300 along the beam / chord, so its gusset sits on the flange tip like at a СФ
    if (abs(x % 6000) < 1 or abs(x % 6000 - 6000) < 1) and any(abs(y - r) < 1 for r in ROWS): return y + 300.0 * (1 if yo > y else -1)
    return y
for (xa, ya, xb, yb) in gs:
    ya, yb = gs_off(xa, ya, yb), gs_off(xb, yb, ya)
    a, b = [xa, ya, ztop(ya) - GSZ], [xb, yb, ztop(yb) - GSZ]""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
