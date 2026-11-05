# -*- coding: utf-8 -*-
"""3.9 Схема расположения выпусков из фундамента Фм-1 (copy of 3.1 + dowels)."""
import sys, json, math
import lib
from lib import *
from geo import *
from shapely.geometry import box, Point
from shapely.ops import unary_union
import ab

SRC_X0 = 321600                    # 3.1 frame origin (current)
X0N = float(sys.argv[1]) if len(sys.argv) > 1 else 1400000.0
Y0 = 450000
DX = X0N - SRC_X0
PX, PY = 323120 + DX, 462470       # plan origin (axis 1 / A) on the copy
P = 'V39:'
R = lambda h: P + h

ops = lib.OPS
op(t='eraseregion', win=[X0N - 10, Y0 - 10, X0N + 59410, Y0 + 42010])
op(t='copywin', win=[SRC_X0 - 1, Y0 - 1, SRC_X0 + 59401, Y0 + 42001], d=[DX, 0], pre=P)
# drop formwork-only objects
op(t='erase', h=[R(h) for h in ['12D768', '12D769', '12D76A', '12D76B', '12D76C', '12D76D', '12D76E', '12D76F', '12D770',
                                 '12D7A9', '12D7AB', '12D7AC', '12D7AD']])
op(t='settext', h=R('12D67B'), s='{\\LСхема расположения выпусков из фундамента Фм-1 на отм. -4.000}')
op(t='settext', h=R('12D677'), s='Схема расположения выпусков\\Pиз фундамента Фм-1')
op(t='settext', h=R('12D679'), s='3.9')

# ---- walls: two rows of dowels (50 from faces, step 100 = поз.1;2 ш.200 + поз.3 ш.200 between)
walls = WALLS_OUT + WALLS_IN
cols = [box(x - 250, y - 250, x + 250, y + 250) for x, y in COLS_IN + COLS_PIL]
colu = unary_union(cols)
wall_geo = [box(*wall_rect(w)) for w in walls]
allw = unary_union(wall_geo + cols)
dots = []


def keep(p):
    q = Point(p)
    if colu.buffer(-1).contains(q) or colu.distance(q) < 60: return False
    if not allw.buffer(-45).contains(q): return False
    for d in dots[-400:]:
        if abs(d[0] - p[0]) < 60 and abs(d[1] - p[1]) < 60: return False
    return True


runs = []
for w in walls:
    o, c, a, b = w
    x0, y0, x1, y1 = wall_rect(w)
    for face in (-1, 1):
        cc = c + face * (TW / 2 - 50)
        lo, hi = a - TW / 2 + 50, b + TW / 2 - 50
        n = int(round((hi - lo) / 100.0))
        pts = []
        for i in range(n + 1):
            s_ = lo + i * (hi - lo) / n
            p = (cc, s_) if o == 'X' else (s_, cc)
            if keep(p): dots.append(p); pts.append(p)
        runs.append((w, face, pts))
for x, y in dots:
    op(t='circle', c=[PX + x, PY + y], r=30, layer='ф20_арм', lw=40)

# ---- columns Км-1, Км-2: 8Ø25 + X1 square + X2 diamond
for x, y in COLS_IN + COLS_PIL:
    e = 250 - 40 - 12.5
    for dx_, dy_ in ((-e, -e), (0, -e), (e, -e), (e, 0), (e, e), (0, e), (-e, e), (-e, 0)):
        op(t='circle', c=[PX + x + dx_, PY + y + dy_], r=40, layer='ф25_арм' if False else 'ф20_арм', lw=40)
    h = 250 - 40 + 4
    pl([(PX + x - h, PY + y - h), (PX + x + h, PY + y - h), (PX + x + h, PY + y + h), (PX + x - h, PY + y + h)], layer='ф8_арм', closed=True, lw=25)
    pl([(PX + x, PY + y - h), (PX + x + h, PY + y), (PX + x, PY + y + h), (PX + x - h, PY + y)], layer='ф8_арм', closed=True, lw=25)

# ---- notes (explicit, shelf to the right of origin; never across walls / other notes)
F = 150  # dot row offset from wall axis (400 wall, 50 from face)
WN = [  # target (x,y) on a dot row, origin
    ((23000, 12350 + F), (23700, 13300)),          # ось В
    ((25000, 0 + F), (25700, 1100)),               # ось А
    ((25000, 24700 - F), (25700, 23600)),          # ось Д
    ((6800 + F, 3000), (7700, 3700)),              # ось 2
    ((44200 + F, 8000), (45400, 8800)),            # ось 8 (outer row, from outside)
    ((37800 + F, 7500), (38700, 8300)),            # x=37800
    ((41000, 4600 + F), (41700, 5500)),            # y=4600
    ((41000, 10950 + F), (41700, 11800)),          # y=10950
    ((41000, 13750 + F), (41700, 14600)),          # y=13750
    ((41000, 20100 + F), (41700, 21000)),          # y=20100
    ((7700, 14200 + F), (8200, 15100)),            # pit y=14200 (from the tank side)
    ((7700, 10500 - F), (8200, 9600)),             # pit y=10500 (from the tank side)
    ((8700 + F, 11400), (9500, 10600)),            # pit x=8700 (outside, under В)
]
for t_, o_ in WN:
    note('1;2;3', 'ш.100', (PX + o_[0], PY + o_[1]), (PX + t_[0], PY + t_[1]), arrow='arrow')
for x, y in COLS_IN + COLS_PIL:
    if (x, y) == (6800, 13810): org, tg = (7300, 12500), (x + 250, y - 250)
    elif (x, y) == (6800, 24700): org, tg = (7600, 23300), (x + 250, y - 250)
    else: org, tg = (x + 800, y + 800), (x + 250, y + 250)
    note('Вп-1', '', (PX + org[0], PY + org[1]), (PX + tg[0], PY + tg[1]), arrow='arrow')

notes = ['Общие указания см. лист 1.1. Данный лист читать совместно с листами 3.1, 3.10, 4.1, 4.2, 5.1 ... 5.24.',
         'Выпуски стен поз. 1;2 - %%C20 A500C ш.200 у обеих граней, стыки вразбежку (выпуск над плитой 1220 и 2810 мм); поз. 3 - %%C20 ш.200 между ними, нижняя зона стены (до отм. -1.000).',
         'Выпуски колонн Км-1, Км-2 - Вп-1 (8%%C25), в теле фундамента хомуты Х1, Х2 %%C8 ш.200 (2 ряда сверху и 2 снизу), см. лист 3.10.',
         'Выпуски заводятся до нижней сетки Фм-1, горизонтальная нога 200 мм под нижней сеткой; координаты выпусков 1:1 с вертикальной арматурой стен и колонн.',
         'При пересечении с арматурой плиты выпуск не смещать - стержни плиты обходить с уклоном 1:6.']
s = '\\pxi-3.3333,l3.3333,ql,t3.3333;' + '\\P'.join('%d.\t%s' % (i + 1, l) for i, l in enumerate(notes))
op(t='settext', h=R('12D7AE'), s=s)
op(t='save')
print('dots', len(dots), 'ops', len(ops))
r = ab.run(ops, 'v39', 2400)
print('\n'.join(l for l in r.splitlines() if 'err' in l.lower() or 'copywin' in l or 'fail' in l.lower())[-2000:])
