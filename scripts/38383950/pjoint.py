D = 'D:\\Бекасыл КЖ КМ\\Завод_В109_КМ\\_авто\\revit\\'
p = D + 'gen.py'; s = open(p, encoding='utf-8').read()
a = """            ya = R[ra] + (309.5 if ra in 'AEHM' else 0.5)
            yb = R[rb] - (309.5 if rb in 'AEHM' else 0.5)"""
assert a in s
s = s.replace(a, """            ya = R[ra] + (309.5 if ra in 'AEHM' else 10.5)      # узел 5: plate −12 between the two БП1 ends over the СФ post
            yb = R[rb] - (309.5 if rb in 'AEHM' else 10.5)""")
open(p, 'w', encoding='utf-8').write(s)
p = D + 'nodes.py'; s = open(p, encoding='utf-8').read()
a = """        for sy in (-1, 1): weld(g, [x - BW[mp] / 2, y + sy * 5, zt], [0, sy, 0], [0, 0, -1], [1, 0, 0], 6, BW[mp])"""
assert a in s
s = s.replace(a, a + """
        if mp == '30Б1':                                         # узел 5 (user 09.11 «2 балка арасындағы лист»): plate −12 between the two БП1 ends,
            ztp = min(ztop(y - 6), ztop(y + 6)) - 0.5            # over the post web, from the post top to the beam top, flange width
            box(g, [x - BW[mp] / 2, y - 6, zt], [x + BW[mp] / 2, y + 6, ztp])""")
open(p, 'w', encoding='utf-8').write(s); print('ok')
