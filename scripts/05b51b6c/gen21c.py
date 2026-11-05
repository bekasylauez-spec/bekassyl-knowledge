"""Лист 2.1 «Схема расположения элементов на отм. -0.500» — v3 по правилам Bekassyl (Obsidian)."""
import sys
import ab, geo_ob, pl_ob, pl2
from pl_ob import AX, AY, COLX, COLY

WIN = [-1552803, -1749172, -1463703, -1707172]
X1, YA = -1524253.0, -1729469.0
XS = [X1 + v for v in AX]; YS = [YA + v for v in AY]
ABK = r'D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК ВАРИАНТ 2.dwg'
T_OUT, T_PODG, T_COL, T_COLH, T_DIM, T_NOTE = ['T21c:' + h for h in ('3C428F', '3C3717', '344854', '344853', '3448BE', '3450DE')]
TABLE, TITLE = '34209C', '344830'
FIRST = len(sys.argv) > 2 and sys.argv[2] == 'first'

si = pl_ob.sheetinfo(WIN)
o = pl2.Ops('g21c_')
o.add({'t': 'sysvar', 'n': 'TILEMODE', 'v': 1})
CX0, CY0, CX1, CY1 = X1 - 1100, YA - 1600, XS[-1] + 1100, YS[-1] + 1600      # outer contour (подготовка)
r1y, r1x, EB, EL, used = pl2.rows(o, si, XS, YS, CX0, CY0, True, True, ytop=CY1 + 300, xright=CX1 + 300)
o.O.insert(1, {'t': 'eraseregion', 'win': WIN, 'keep': si['keep'] + [TITLE] + used})
o.add({'t': 'import', 'file': ABK, 'h': ['3C428F', '3C3717', '344854', '344853', '3448BE', '3450DE'], 'base': [0, 0], 'to': [0, 0], 'pre': 'T21c:'})

F = geo_ob.found()
P = F.buffer(100, join_style=2)
for g, t in ((F, T_OUT), (P, T_PODG)):
    for poly in (g.geoms if hasattr(g, 'geoms') else [g]):
        for r in [poly.exterior] + list(poly.interiors):
            o.ring(t, [(X1 + x, YA + y) for x, y in list(r.coords)[:-1]])

CXm = X1 + 21000
for i, x in enumerate(XS):
    for j, y in enumerate(YS):
        o.rect(T_COL, x - COLX / 2, y - COLY / 2, x + COLX / 2, y + COLY / 2, T_COLH)
        o.bind2(T_DIM, x, COLX / 2, y + 2200, out=1, org=y + COLY / 2)                 # 350|350 above the pad
        left = x < CXm
        sx = 1 if left else -1
        o.bind2(T_DIM, y, COLY / 2, x + sx * 1500, vertical=True, out=sx, org=x + sx * COLX / 2)   # 450|450 beside the pad
        sy = -1 if j == 2 else 1                                                        # marks toward the plan centre
        tgt = (x + sx * COLX / 2, y + sy * COLY / 2)
        o.mark(T_NOTE, pl_ob.colmark(i, j), tgt, sx, sy, off=1350 if j != 2 else 1500)
# Фм-1 on row Б pads (axes 2..8), pad edge facing the centre
for i in (2, 3, 4, 6, 7):
    x, y = XS[i], YS[1]
    o.mark(T_NOTE, 'Фм-1', (x - 1000, y - 1100), -1, -1, off=900)
# outer chains: pads (row 1 bottom / left), extension origins on the pad contour
o.chain2(T_DIM, [x + d for x in XS for d in (-1000, 0, 1000)], r1y, origin=YA - 1500, out=-1)
o.chain2(T_DIM, [y + d for y in YS for d in (-1500, 0, 1500)], r1x, vertical=True, origin=X1 - 1000, out=-1)
# beam width once (Фм-1 lenta 350): one place per direction
o.bind2(T_DIM, XS[2], 175, YA + 3000, out=1)
o.bind2(T_DIM, YS[1], 175, XS[6] + 3000, vertical=True, out=1)
o.add({'t': 'mtext', 'at': [-1482603, -1734872 + 250 + 2600], 'h': 250, 'w': 17800, 'layer': 'Размеры',
       's': '1. Фундамент Фм-1 - монолитный: подушки 2000х3000х1000 под колоннами, связанные фундаментными балками 350х600 по всем осям. Верх -0.500.\\P'
            '2. Под фундаментом - бетонная подготовка С8/10 t=100, подушка из уплотненного суглинка t=1000 и раскатные сваи, см. листы 1.3, 1.4.'})
TTL = 'Схема расположения элементов на отм. -0.500'
o.add({'t': 'settext', 'h': TITLE, 's': '{\\L' + TTL + '}'})
o.add({'t': 'moveto', 'h': TITLE, 'idx': 0, 'to': [X1 - 1000, CY1 + 1950]})
if FIRST:
    o.add({'t': 'trows', 'h': TABLE, 'mode': 'del', 'at': 4, 'n': 4})
    o.add({'t': 'tset', 'h': TABLE, 'cells': [[3, 2, 'Фундамент Фм-1'], [3, 10, '1']]})
o.add({'t': 'erase', 'h': [T_OUT, T_PODG, T_COL, T_COLH, T_DIM, T_NOTE]})
o.add({'t': 'save'})
print(len(o.O), 'ops')
if len(sys.argv) > 1:
    out = ab.run(o.O, 'g21c', 1500)
    print('\n'.join(l for l in out.splitlines() if 'errors' in l or l.startswith('ERR') or 'no prop' in l)[-1500:])
