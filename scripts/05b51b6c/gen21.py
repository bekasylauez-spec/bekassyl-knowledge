"""Лист 2.1 «Схема расположения элементов на отм. -0.500» (фундаменты Фм-1, балки Фб, колонны)."""
import sys, os
import ab, geo_ob, pl_ob
from pl_ob import AX, AY, COLX, COLY

WIN = [-1552803, -1749172, -1463703, -1707172]
X1, YA = -1524253.0, -1729469.0
XS = [X1 + v for v in AX]; YS = [YA + v for v in AY]
KEEP = ['342058', '342059', '342152', '34209C', '344830']
VAX = ['3444AD', '3444AE', '3444AF', '3444B0', '3444B1', '3444B2', '3444B3', '3444B4']
HAX = ['34467D', '344687', '3446D3']
CH = ['3444D8', '344502', '34452C', '344556', '344580', '3445AA', '3445D4']
LEFT = ['3446A9', '3446DD', '344688']
T_OUT, T_COL, T_COLH, T_DIM, T_NOTE = '3C428F', '344854', '344853', '3448BE', '3450DE'
TEMPL = [T_OUT, T_COL, T_COLH, T_DIM, T_NOTE]

o = pl_ob.Ops('e21_')
o.add({'t': 'sysvar', 'n': 'TILEMODE', 'v': 1})
o.add({'t': 'eraseregion', 'win': WIN, 'keep': KEEP + VAX + HAX + CH + LEFT + ['3444B7'] + TEMPL})
o.add({'t': 'erase', 'h': ['3444B5', '3444B6', '344652', '3445FE', '344628', '34465C']})

# axes (marker end shifted 600 down / left, pads are 1500 deep)
EB = YA - 2860; EL = X1 - 5331
for i, h in enumerate(VAX):
    o.add({'t': 'axis', 'h': h, 's': [XS[i], YS[2]], 'e': [XS[i], EB], 'val': str(i + 1)})
for j, h in enumerate(HAX):
    o.add({'t': 'axis', 'h': h, 's': [XS[-1], YS[j]], 'e': [EL, YS[j]]})
for i, h in enumerate(CH):
    o.add({'t': 'dimset2', 'h': h, 'p1': [XS[i], EB], 'p2': [XS[i + 1], EB], 'dl': [XS[i], YA - 2257], 'tx': [(XS[i] + XS[i + 1]) / 2, YA - 2257 + 187]})
o.add({'t': 'dimset2', 'h': '3444B7', 'p1': [XS[0], EB], 'p2': [XS[-1], EB], 'dl': [XS[0], YA - 2957], 'tx': [(XS[0] + XS[-1]) / 2, YA - 2957 + 187]})
for h, (a, b), xl in (('3446A9', (0, 1), X1 - 4131), ('3446DD', (1, 2), X1 - 4131), ('344688', (0, 2), X1 - 4831)):
    o.add({'t': 'dimset2', 'h': h, 'p1': [EL, YS[a]], 'p2': [EL, YS[b]], 'dl': [xl, YS[a]], 'tx': [xl - 188, (YS[a] + YS[b]) / 2 + (1500 if (a, b) == (0, 2) else 0)]})

# foundation outline (pads 2000x3000 + beams 350)
F = geo_ob.found()
for poly in (F.geoms if hasattr(F, 'geoms') else [F]):
    for r in [poly.exterior] + list(poly.interiors):
        o.ring(T_OUT, [(X1 + x, YA + y) for x, y in list(r.coords)[:-1]])

# columns, binding dims, marks
for i, x in enumerate(XS):
    for j, y in enumerate(YS):
        o.rect(T_COL, x - COLX / 2, y - COLY / 2, x + COLX / 2, y + COLY / 2, T_COLH)
        o.chain(T_DIM, [x - COLX / 2, x, x + COLX / 2], y + COLY / 2 + 350)
        o.chain(T_DIM, [y - COLY / 2, y, y + COLY / 2], x + COLX / 2 + 350, vertical=True)
        o.note(T_NOTE, pl_ob.colmark(i, j), (x + COLX / 2, y + COLY / 2), (x + 1300, y + 1900))
# pad dims: x chain in bay Б–В, y chain left of axis 1
o.chain(T_DIM, [x + d for x in XS for d in (-1000, 0, 1000)], YS[1] + 3000)
o.chain(T_DIM, [y + d for y in YS for d in (-1500, 0, 1500)], X1 - 1800, vertical=True)
# foundation beam binding (175|175) once per direction
o.chain(T_DIM, [XS[1] - 175, XS[1], XS[1] + 175], YA + 2600)
o.chain(T_DIM, [YS[1] - 175, YS[1], YS[1] + 175], XS[1] + 1625, vertical=True)
# Фм-1 marks on row Б pads (axes 2..8), Фб marks
for i in range(1, 8):
    x, y = XS[i], YS[1]
    o.note(T_NOTE, 'Фм-1', (x - 1000, y - 1100), (x - 2300, y - 2200))
done = set()
for mk, x0, y0, x1, y1 in pl_ob.fbeams():
    if mk in done: continue
    if mk == 'Фб-4':
        if x0 != AX[1]: continue
        o.note(T_NOTE, mk, (X1 + x0 + 175, YA + (y0 + y1) / 2), (X1 + x0 + 900, YA + (y0 + y1) / 2 + 700))
    else:
        if y0 != AY[1]: continue
        xm = X1 + (x0 + x1) / 2
        o.note(T_NOTE, mk, (xm, YS[1] - 175), (xm + 200, YS[1] - 2300))
    done.add(mk)

# titles, table
TTL = 'Схема расположения элементов на отм. -0.500'
o.add({'t': 'settext', 'h': '344830', 's': '{\\L' + TTL + '}'})
o.add({'t': 'moveto', 'h': '344830', 'idx': 0, 'to': [X1 - 1000, YS[2] + 3600]})
o.add({'t': 'settext', 'h': '342152', 's': TTL})
cnt = {}
for i in range(8):
    for j in range(3):
        cnt[pl_ob.colmark(i, j)] = cnt.get(pl_ob.colmark(i, j), 0) + 1
fb = {}
for b in pl_ob.fbeams(): fb[b[0]] = fb.get(b[0], 0) + 1
T = '34209C'
o.add({'t': 'trows', 'h': T, 'mode': 'ins', 'at': 4, 'from': 3, 'n': 4})      # Фб-1..4 after Фм-1
o.add({'t': 'trows', 'h': T, 'mode': 'ins', 'at': 10, 'from': 9, 'n': 5})     # Км-2..6 after Км-1
o.add({'t': 'trows', 'h': T, 'mode': 'del', 'at': 15, 'n': 2})                # Стена / См-1
rows = [(3, 'Фм-1', 'лист 3.1', 'Фундамент Фм-1', 24)]
rows += [(4 + k, 'Фб-%d' % (k + 1), 'лист 3.4', 'Фундаментная балка Фб-%d' % (k + 1), fb['Фб-%d' % (k + 1)]) for k in range(4)]
rows += [(9 + k, 'Км-%d' % (k + 1), 'лист 4.%d' % (1 if k < 3 else 2), 'Колонна Км-%d' % (k + 1), cnt['Км-%d' % (k + 1)]) for k in range(6)]
cells = [[8, 2, 'Колонна:']]
for r, mk, sh, nm, n in rows:
    cells += [[r, 0, mk], [r, 1, sh], [r, 2, nm], [r, 10, str(n)]]
o.add({'t': 'tset', 'h': T, 'cells': cells})
o.add({'t': 'erase', 'h': TEMPL})
o.add({'t': 'save'})
print(len(o.O), 'ops', cnt, fb)
if len(sys.argv) > 1:
    out = ab.run(o.O, 'g21', 1500)
    open('w/g21.log', 'w', encoding='utf-8').write(out)
    import re
    print('\n'.join(l for l in out.splitlines() if not l.startswith('clone') and not l.startswith('AXIS'))[-2500:])
