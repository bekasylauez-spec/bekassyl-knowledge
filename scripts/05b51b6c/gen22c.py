"""Лист 2.2 «0.000» — v3 по правилам Bekassyl."""
import sys
import ab, pl_ob, pl2
from pl_ob import AX, AY, COLX, COLY

WIN = [-1463703, -1749172, -1374603, -1707172]
X1, YA = -1524253.0 + (WIN[0] + 1552803), -1729469.0
XS = [X1 + v for v in AX]; YS = [YA + v for v in AY]
P = lambda x, y: (X1 + x, YA + y)
ABK = r'D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК ВАРИАНТ 2.dwg'
IMP = ['344854', '344853', '3448BE', '3450DE', '3C428F']
T_COL, T_COLH, T_DIM, T_NOTE, T_OUT = ['T22c:' + h for h in IMP]
TABLE = '3483D4'
sx0, sy0, sx1, sy1 = -350, -450, 32350, 12450

si = pl_ob.sheetinfo(WIN)
o = pl2.Ops('g22c_')
o.add({'t': 'sysvar', 'n': 'TILEMODE', 'v': 1})
r1y, r1x, EB, EL, used = pl2.rows(o, si, XS, YS, X1 + sx0, YA + sy0, True, True, ytop=YA + sy1 + 600, xright=X1 + sx1 + 600)
o.O.insert(1, {'t': 'eraseregion', 'win': WIN, 'keep': si['keep'] + ['349ED9'] + used + [TABLE]})
o.add({'t': 'import', 'file': ABK, 'h': IMP, 'base': [0, 0], 'to': [0, 0], 'pre': 'T22c:'})
o.ring(T_OUT, [P(sx0, sy0), P(sx1, sy0), P(sx1, sy1), P(sx0, sy1)])
CXm = X1 + 21000
for i, x in enumerate(XS):
    for j, y in enumerate(YS):
        o.rect(T_COL, x - COLX / 2, y - COLY / 2, x + COLX / 2, y + COLY / 2, T_COLH)
        o.bind2(T_DIM, x, COLX / 2, y + COLY / 2 + 700, out=1, org=y + COLY / 2)
        sx = 1 if x < CXm else -1
        o.bind2(T_DIM, y, COLY / 2, x + sx * (COLX / 2 + 700), vertical=True, out=sx, org=x + sx * COLX / 2)
o.chain2(T_DIM, [X1 + sx0, XS[0]], r1y, origin=YA + sy0, out=-1)
o.chain2(T_DIM, [XS[-1], X1 + sx1], r1y, origin=YA + sy0, out=-1)
o.chain2(T_DIM, [YA + sy0, YS[0]], r1x, vertical=True, origin=X1 + sx0, out=-1)
o.chain2(T_DIM, [YS[-1], YA + sy1], r1x, vertical=True, origin=X1 + sx0, out=-1)
o.mark(T_NOTE, 'Пм-1', P(23500, 9000), 1, 1, 600)
TTL = 'Схема расположения элементов на отм. 0.000'
for h in ['349ED9']:
    o.add({'t': 'settext', 'h': h, 's': '{\\L' + TTL + '}'}); o.add({'t': 'moveto', 'h': h, 'idx': 0, 'to': [X1 - 1000, YA + sy1 + 2500]})
o.add({'t': 'mtext', 'at': [-1393603, -1736439 + 250 + 1400], 'h': 250, 'w': 17800, 'layer': 'Размеры',
       's': '1. Плита по грунту Пм-1 t=120, верх 0.000, см. лист 7.1. Колонны - см. лист 2.1.'})
o.add({'t': 'erase', 'h': ['T22c:' + h for h in IMP]})
o.add({'t': 'save'})
print(len(o.O), 'ops')
if len(sys.argv) > 1:
    out = ab.run(o.O, 'g22c', 1500)
    print('\n'.join(l for l in out.splitlines() if 'errors' in l or l.startswith('ERR') or 'no prop' in l)[-1500:])
