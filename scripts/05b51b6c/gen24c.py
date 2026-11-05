"""Лист 2.4 «+11.400» — v3 по правилам Bekassyl."""
import sys
import ab, pl_ob, pl2, beams_ob as B
from pl_ob import AX, AY, COLX, COLY

WIN = [-1285503, -1749172, -1196403, -1707172]
X1, YA = -1252000.0, -1729469.0
AX6 = AX[:6]
XS = [X1 + v for v in AX6]; YS = [YA + v for v in AY]
P = lambda x, y: (X1 + x, YA + y)
ABK = r'D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК ВАРИАНТ 2.dwg'
IMP = ['344854', '344853', '3448BE', '3450DE', '34E543', '34E542']
T_COL, T_COLH, T_DIM, T_NOTE, T_BEAM, T_SLAB = ['T24c:' + h for h in IMP]
TABLE, TITLE, STAMP = '351334', '352C32', '351335'

si = pl_ob.sheetinfo(WIN)
o = pl2.Ops('g24c_')
o.add({'t': 'sysvar', 'n': 'TILEMODE', 'v': 1})
xmin, ymin, xmax, ymax = -450, -450, 20450, 12450
r1y, r1x, EB, EL, used = pl2.rows(o, si, XS, YS, X1 + xmin, YA + ymin, False, True, ytop=YA + ymax + 1600, xright=X1 + xmax + 600)
o.O.insert(1, {'t': 'eraseregion', 'win': WIN, 'keep': si['keep'] + [TITLE, STAMP, TABLE] + used})
o.add({'t': 'import', 'file': ABK, 'h': IMP, 'base': [0, 0], 'to': [0, 0], 'pre': 'T24c:'})

UP = [(x, y) for x in AX6 for y in (0, 12000)] + [(0, 6000), (20000, 6000)]
for x, y in UP:
    o.ring(T_SLAB, [P(x - COLX / 2, y - COLY / 2), P(x + COLX / 2, y - COLY / 2), P(x + COLX / 2, y + COLY / 2), P(x - COLX / 2, y + COLY / 2)])
    o.rect(T_COL, X1 + x - 300, YA + y - 300, X1 + x + 300, YA + y + 300, T_COLH)
for x, y in B.CONSOLES:
    s = 1 if y == 0 else -1
    a, b = y + s * COLY / 2, y + s * 1050
    o.ring(T_SLAB, [P(x - 350, min(a, b)), P(x + 350, min(a, b)), P(x + 350, max(a, b)), P(x - 350, max(a, b))])


def half_at(x, y, along_x):
    if (x, y) in UP: return COLX / 2 if along_x else COLY / 2
    for mk, (bw, bh, lv, segs) in B.B114.items():
        for x0, y0, x1, y1 in segs:
            if along_x and x0 == x1 == x and min(y0, y1) <= y <= max(y0, y1): return bw / 2
            if not along_x and y0 == y1 == y and min(x0, x1) <= x <= max(x0, x1): return bw / 2
    return 0


for mk, (bw, bh, lv, segs) in B.B114.items():
    for x0, y0, x1, y1 in segs:
        if y0 == y1:
            st = sorted(set([x0, x1] + [x for x in AX6 if x0 < x < x1]))
            for a, c in zip(st, st[1:]):
                a2, c2 = a + half_at(a, y0, True), c - half_at(c, y0, True)
                t = o.tag(); o.add({'t': 'clone', 'h': T_BEAM, 'tag': t})
                o.add({'t': 'plset', 'h': t, 'p': [list(P(a2, y0 - bw / 2)), list(P(c2, y0 - bw / 2)), list(P(c2, y0 + bw / 2)), list(P(a2, y0 + bw / 2))], 'closed': True})
        else:
            st = sorted(set([y0, y1] + [y for y in AY if y0 < y < y1]))
            for a, c in zip(st, st[1:]):
                a2, c2 = a + half_at(x0, a, False), c - half_at(x0, c, False)
                t = o.tag(); o.add({'t': 'clone', 'h': T_BEAM, 'tag': t})
                o.add({'t': 'plset', 'h': t, 'p': [list(P(x0 - bw / 2, a2)), list(P(x0 + bw / 2, a2)), list(P(x0 + bw / 2, c2)), list(P(x0 - bw / 2, c2))], 'closed': True})
for yc in (800, 11200):   # crane runway ПБ-1 (КМ)
    t = o.tag(); o.add({'t': 'clone', 'h': T_BEAM, 'tag': t})
    o.add({'t': 'plset', 'h': t, 'p': [list(P(-200, yc - 125)), list(P(20200, yc - 125)), list(P(20200, yc + 125)), list(P(-200, yc + 125))], 'closed': True})

M = [('Бм-15', (5500, -225), 1, -1, 600), ('Бм-15', (5500, 12225), 1, 1, 600), ('Бм-16', (350, 9000), 1, 1, 600), ('Бм-17', (19775, 4000), -1, 1, 600)]
for x, y in B.CONSOLES:
    M.append(('КН-1', (x + 350, 1050 if y == 0 else 10950), 1, 1 if y == 0 else -1, 600))
for txt, tg, dx, dy, off in M:
    o.mark(T_NOTE, txt, P(*tg), dx, dy, off)
o.mark(T_NOTE, 'ПБ-1', P(14500, 925), 1, 1, 600, 'см. КМ')
o.mark(T_NOTE, 'ПБ-1', P(14500, 11075), 1, -1, 900, 'см. КМ')
# left row 1: crane runway position from the axes
o.chain2(T_DIM, [YA + v for v in (0, 800, 11200, 12000)], r1x, vertical=True, origin=X1 - 200, out=-1,
         origins={round(YA, 1): X1 - 350, round(YA + 12000, 1): X1 - 350}, txo={1: (r1x, YA + 3500)})
# widths once per mark; upper column 600 once
o.bind2(T_DIM, X1, 350, YA + 3000, out=1)                                 # Бм-16
o.bind2(T_DIM, X1 + 20000, 225, YA + 3000, out=1)                         # Бм-17
o.bind2(T_DIM, X1 + 3250, 300, YA + 12000 + 1300, out=1, org=YA + 12300)  # upper column 600
o.bind2(T_DIM, YA + 6000, 300, X1 + 1300, vertical=True, out=1, org=X1 + 300)
TTL = 'Схема расположения элементов на отм. +11.400'
o.add({'t': 'settext', 'h': TITLE, 's': '{\\L' + TTL + '}'}); o.add({'t': 'moveto', 'h': TITLE, 'idx': 0, 'to': [X1 - 1000, YA + 12000 + 3000]})
o.add({'t': 'settext', 'h': STAMP, 's': TTL})
o.add({'t': 'mtext', 'at': [-1215303, -1736439 + 250 + 2600], 'h': 250, 'w': 17800, 'layer': 'Размеры',
       's': '1. Консоли КН-1 700х850 (вылет 600 от грани колонны) - в составе колонн Км-4. Колонны выше +11.400 - 600х600 по центру осей.\\P'
            '2. Подкрановые балки ПБ-1 под кран-балку г/п 3 т - см. раздел КМ.\\P3. Балки Бм-15…Бм-17 - пунктиром, верх - отм. +11.400.'})
o.add({'t': 'erase', 'h': ['T24c:' + h for h in IMP]})
o.add({'t': 'save'})
print(len(o.O), 'ops')
if len(sys.argv) > 1:
    out = ab.run(o.O, 'g24c', 1500)
    print('\n'.join(l for l in out.splitlines() if 'errors' in l or l.startswith('ERR') or 'no prop' in l)[-1500:])
