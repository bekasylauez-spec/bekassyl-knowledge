"""Лист 2.1 — rebuild of the content (axes/chains already set by gen21.py)."""
import sys
import ab, geo_ob, pl_ob
from pl_ob import AX, AY, COLX, COLY

WIN = [-1552803, -1749172, -1463703, -1707172]
X1, YA = -1524253.0, -1729469.0
XS = [X1 + v for v in AX]; YS = [YA + v for v in AY]
KEEP = ['342058', '342059', '342152', '34209C', '344830', '3444AD', '3444AE', '3444AF', '3444B0', '3444B1', '3444B2', '3444B3', '3444B4',
        '34467D', '344687', '3446D3', '3444D8', '344502', '34452C', '344556', '344580', '3445AA', '3445D4', '3446A9', '3446DD', '344688', '3444B7']
ABK = r'D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК ВАРИАНТ 2.dwg'
TPL = ['3C428F', '344854', '344853', '3448BE', '3450DE']
T_OUT, T_COL, T_COLH, T_DIM, T_NOTE = ['T21:' + h for h in TPL]

o = pl_ob.Ops('f21_')
o.add({'t': 'sysvar', 'n': 'TILEMODE', 'v': 1})
o.add({'t': 'eraseregion', 'win': WIN, 'keep': KEEP})
o.add({'t': 'import', 'file': ABK, 'h': TPL, 'base': [0, 0], 'to': [0, 0], 'pre': 'T21:'})

F = geo_ob.found()
for poly in (F.geoms if hasattr(F, 'geoms') else [F]):
    for r in [poly.exterior] + list(poly.interiors):
        o.ring(T_OUT, [(X1 + x, YA + y) for x, y in list(r.coords)[:-1]])

for i, x in enumerate(XS):
    for j, y in enumerate(YS):
        o.rect(T_COL, x - COLX / 2, y - COLY / 2, x + COLX / 2, y + COLY / 2, T_COLH)
        o.bind(T_DIM, x, COLX / 2, (y + 2000) if j != 1 else (y - 2000))   # 350|350 above (row A) / below the pad
        o.bind(T_DIM, y, COLY / 2, x + 1000 + 500, vertical=True)            # 450|450 right of the pad
        if j != 1:
            o.note(T_NOTE, pl_ob.colmark(i, j), (x + COLX / 2, y + COLY / 2), (x + 1500, y + 2700))
        else:
            o.note(T_NOTE, pl_ob.colmark(i, j), (x - COLX / 2, y + COLY / 2), (x - 1500, y + 2700))

o.chain(T_DIM, [x + d for x in XS for d in (-1000, 0, 1000)], YS[1] + 3800)          # pads along X
o.chain(T_DIM, [y + d for y in YS for d in (-1500, 0, 1500)], X1 - 1800, vertical=True)  # pads along Y
o.bind(T_DIM, XS[2], 175, YA + 3300)                                                  # beam 175|175
o.bind(T_DIM, YS[1], 175, XS[6] + 3000, vertical=True, out=400)

o.note(T_NOTE, 'Фм-1', (XS[6] - 1000, YS[1] - 1100), (XS[6] - 2300, YS[1] - 2200))
for mk, i in (('Фб-1', 0), ('Фб-2', 2), ('Фб-3', 6)):
    xm = (XS[i] + XS[i + 1]) / 2
    o.note(T_NOTE, mk, (xm, YS[1] - 175), (xm + 200, YS[1] - 2550))
o.note(T_NOTE, 'Фб-4', (XS[1] + 175, YA + 3000), (XS[1] + 900, YA + 3700))

o.add({'t': 'erase', 'h': [T_OUT, T_COL, T_COLH, T_DIM, T_NOTE]})
o.add({'t': 'list', 'win': [-1483000, -1743300, -1463900, -1700000]})
o.add({'t': 'save'})
print(len(o.O), 'ops')
if len(sys.argv) > 1:
    out = ab.run(o.O, 'g21b', 1500)
    open('w/g21b.log', 'w', encoding='utf-8').write(out)
    print('\n'.join(l for l in out.splitlines() if not l.startswith('clone') and not l.startswith('sel '))[-2500:])
