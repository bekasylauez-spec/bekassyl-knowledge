"""Лист 2.2 «Схема расположения элементов на отм. 0.000» — плита по грунту Пм-1, колонны."""
import sys
import ab, pl_ob
from pl_ob import AX, AY, COLX, COLY

WIN = [-1463703, -1749172, -1374603, -1707172]
DX = WIN[0] - (-1552803)
X1, YA = -1524253.0 + DX, -1729469.0
XS = [X1 + v for v in AX]; YS = [YA + v for v in AY]
ABK = r'D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК ВАРИАНТ 2.dwg'
T_COL, T_COLH, T_DIM, T_NOTE, T_OUT = 'T22:344854', 'T22:344853', 'T22:3448BE', 'T22:3450DE', 'T22:3C428F'

si = pl_ob.sheetinfo(WIN)
o = pl_ob.Ops('f22_')
o.add({'t': 'sysvar', 'n': 'TILEMODE', 'v': 1})
EB = YA - 2300; EL = X1 - 5331
axh = pl_ob.setup_axes(o, si, XS, YS, EB, EL, YA - 1700, YA - 2400, (X1 - 4131, X1 - 4831))
o.O.insert(1, {'t': 'eraseregion', 'win': WIN, 'keep': si['keep'] + si['title'] + axh})
o.add({'t': 'import', 'file': ABK, 'h': ['344854', '344853', '3448BE', '3450DE', '3C428F'], 'base': [0, 0], 'to': [0, 0], 'pre': 'T22:'})

# slab on grade Пм-1: between the outer faces of the edge columns
SX0, SX1, SY0, SY1 = XS[0] - COLX / 2, XS[-1] + COLX / 2, YS[0] - COLY / 2, YS[-1] + COLY / 2
o.ring(T_OUT, [(SX0, SY0), (SX1, SY0), (SX1, SY1), (SX0, SY1)])
for i, x in enumerate(XS):
    for j, y in enumerate(YS):
        o.rect(T_COL, x - COLX / 2, y - COLY / 2, x + COLX / 2, y + COLY / 2, T_COLH)
        if j != 2:
            o.bind(T_DIM, x, COLX / 2, y + COLY / 2 + 700)
        if i != 7:
            o.bind(T_DIM, y, COLY / 2, x + COLX / 2 + 700, vertical=True)
# slab edge dims: top chain and right chain
o.chain(T_DIM, XS, SY1 + 900)
o.dim(T_DIM, (SX0, SY1 + 900), (XS[0], SY1 + 900), (SX0, SY1 + 900), tx=(SX0 - 450, SY1 + 900 + 187))
o.dim(T_DIM, (XS[-1], SY1 + 900), (SX1, SY1 + 900), (XS[-1], SY1 + 900), tx=(SX1 + 450, SY1 + 900 + 187))
o.dim(T_DIM, (SX0, SY1 + 900), (SX1, SY1 + 900), (SX0, SY1 + 1600), txt=None)
o.chain(T_DIM, [SY0] + YS + [SY1], SX1 + 1500, vertical=True)
o.dim(T_DIM, (SX1 + 1500, SY0), (SX1 + 1500, SY1), (SX1 + 2200, SY0), vertical=True)
o.note(T_NOTE, 'Пм-1', (XS[6] + 3000, YS[0] + 3000), (XS[6] + 3700, YS[0] + 3800))

TTL = 'Схема расположения элементов на отм. 0.000'
for h in si['title']:
    o.add({'t': 'settext', 'h': h, 's': '{\\L' + TTL + '}'})
    o.add({'t': 'moveto', 'h': h, 'idx': 0, 'to': [X1 - 1000, YS[2] + 3600]})
st = [h for h in si['stamp']]
T = si['table'][0]
o.add({'t': 'tset', 'h': T, 'cells': [[3, 0, 'Пм-1'], [3, 1, 'лист 7.1'], [3, 2, 'Плита по грунту Пм-1'], [3, 10, '1']]})
o.add({'t': 'txtrep', 'win': WIN, 'pairs': [['Схема расположения элементов на отм. -0.000', TTL], ['на отм. -0.000', 'на отм. 0.000']]})
o.add({'t': 'erase', 'h': [T_COL, T_COLH, T_DIM, T_NOTE, T_OUT]})
o.add({'t': 'save'})
print(len(o.O), 'ops', si['title'], si['stamp'])
if len(sys.argv) > 1:
    out = ab.run(o.O, 'g22', 1500)
    print('\n'.join(l for l in out.splitlines() if not l.startswith('clone') and not l.startswith('AXIS'))[-1500:])
