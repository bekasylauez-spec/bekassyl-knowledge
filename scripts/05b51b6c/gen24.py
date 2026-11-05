"""Лист 2.4 «Схема расположения элементов на отм. +11.400» — балки Бм-15…17, консоли КН-1, колонны (оси 1-6)."""
import sys
import ab, pl_ob, beams_ob as B
from pl_ob import AX, AY, COLX, COLY

WIN = [-1285503, -1749172, -1196403, -1707172]
X1, YA = -1252000.0, -1729469.0
AX6 = AX[:6]
XS = [X1 + v for v in AX6]; YS = [YA + v for v in AY]
P = lambda x, y: (X1 + x, YA + y)
ABK = r'D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК ВАРИАНТ 2.dwg'
T_COL, T_COLH, T_DIM, T_NOTE, T_BEAM, T_SLAB = ['T24:' + h for h in ('344854', '344853', '3448BE', '3450DE', '34E543', '34E542')]
T = '351334'

si = pl_ob.sheetinfo(WIN)
o = pl_ob.Ops('f24_')
o.add({'t': 'sysvar', 'n': 'TILEMODE', 'v': 1})
EB = YA - 2300; EL = X1 - 5331
axh = pl_ob.setup_axes(o, si, XS, YS, EB, EL, YA - 1700, YA - 2400, (X1 - 4131, X1 - 4831))
o.O.insert(1, {'t': 'eraseregion', 'win': WIN, 'keep': si['keep'] + si['title'] + axh + [T]})
o.add({'t': 'import', 'file': ABK, 'h': ['344854', '344853', '3448BE', '3450DE', '34E543', '34E542'], 'base': [0, 0], 'to': [0, 0], 'pre': 'T24:'})

UP = [(x, y) for x in AX6 for y in (0, 12000)] + [(0, 6000), (20000, 6000)]
for x, y in UP:   # lower column outline 700x900, upper column 600x600 hatched
    o.ring(T_SLAB, [P(x - COLX / 2, y - COLY / 2), P(x + COLX / 2, y - COLY / 2), P(x + COLX / 2, y + COLY / 2), P(x - COLX / 2, y + COLY / 2)])
    o.rect(T_COL, X1 + x - 300, YA + y - 300, X1 + x + 300, YA + y + 300, T_COLH)
# consoles КН-1: 700 wide, from the column face to 1050 (crane line 800 + 250)
for x, y in B.CONSOLES:
    s = 1 if y == 0 else -1
    a, b = y + s * COLY / 2, y + s * 1050
    o.ring(T_SLAB, [P(x - 350, min(a, b)), P(x + 350, min(a, b)), P(x + 350, max(a, b)), P(x - 350, max(a, b))])


def half_at(x, y, along_x):
    if (x, y) in UP: return COLX / 2 if along_x else COLY / 2
    for mk, (b, h, lv, segs) in B.B114.items():
        for x0, y0, x1, y1 in segs:
            if along_x and x0 == x1 == x and min(y0, y1) <= y <= max(y0, y1): return b / 2
            if not along_x and y0 == y1 == y and min(x0, x1) <= x <= max(x0, x1): return b / 2
    return 0


for mk, (bw, bh, lv, segs) in B.B114.items():
    for x0, y0, x1, y1 in segs:
        if y0 == y1:
            stops = sorted(set([x0, x1] + [x for x in AX6 if x0 < x < x1]))
            for a, c in zip(stops, stops[1:]):
                a2, c2 = a + half_at(a, y0, True), c - half_at(c, y0, True)
                t = o.tag(); o.add({'t': 'clone', 'h': T_BEAM, 'tag': t})
                o.add({'t': 'plset', 'h': t, 'p': [list(P(a2, y0 - bw / 2)), list(P(c2, y0 - bw / 2)), list(P(c2, y0 + bw / 2)), list(P(a2, y0 + bw / 2))], 'closed': True})
        else:
            stops = sorted(set([y0, y1] + [y for y in AY if y0 < y < y1]))
            for a, c in zip(stops, stops[1:]):
                a2, c2 = a + half_at(x0, a, False), c - half_at(x0, c, False)
                t = o.tag(); o.add({'t': 'clone', 'h': T_BEAM, 'tag': t})
                o.add({'t': 'plset', 'h': t, 'p': [list(P(x0 - bw / 2, a2)), list(P(x0 + bw / 2, a2)), list(P(x0 + bw / 2, c2)), list(P(x0 - bw / 2, c2))], 'closed': True})
# crane runway axes (steel ПБ-1, see КМ): thin lines y = 800 / 11200
for yc in (800, 11200):
    t = o.tag(); o.add({'t': 'clone', 'h': T_BEAM, 'tag': t}); o.add({'t': 'plset', 'h': t, 'p': [list(P(-200, yc - 125)), list(P(20200, yc - 125)), list(P(20200, yc + 125)), list(P(-200, yc + 125))], 'closed': True})

LB = [('Бм-15', (5500, 225), (6000, 2200)), ('Бм-15', (10000, 11775), (10500, 9800)),
      ('Бм-16', (350, 4000), (1000, 4600)), ('Бм-17', (20225, 4000), (20900, 4600)),
      ('КН-1', (3600, 900), (4300, 1700)), ('КН-1', (3600, 11100), (4300, 10300)),
      ('ПБ-1', (14500, 925), (15000, 2200), 'см. КМ'), ('ПБ-1', (14500, 11075), (15000, 9800), 'см. КМ')]
for it in LB:
    o.note(T_NOTE, it[0], P(*it[1]), P(*it[2]), it[3] if len(it) > 3 else None)

# dims: crane line from axis A / В, console size, beams binding
o.dim(T_DIM, (X1 - 1500, YA), (X1 - 1500, YA + 800), (X1 - 1500, YA), True)
o.dim(T_DIM, (X1 - 1500, YA + 11200), (X1 - 1500, YA + 12000), (X1 - 1500, YA + 11200), True)
o.bind(T_DIM, X1 + 7750, 350, YA + 1600)
o.mtext_note = None
o.add({'t': 'mtext', 'at': [X1, YA - 4700], 'h': 250, 'w': 26000, 'layer': 'Размеры',
       's': '1. Консоли КН-1 (700х850, вылет от грани колонны 600, до оси подкрановой балки 800 от оси ряда) - на колоннах Км-4 по осям 2-5, ряды А и В.\\P'
            '2. Подкрановые балки ПБ-1 под кран-балку г/п 3 т - металлические, см. раздел КМ. Колонны выше отм. +11.400 - 600х600.\\P'
            '3. Балки Бм-15…Бм-17 показаны пунктиром, верх балок - отм. +11.400.'})
TTL = 'Схема расположения элементов на отм. +11.400'
for h in si['title']:
    o.add({'t': 'settext', 'h': h, 's': '{\\L' + TTL + '}'})
    o.add({'t': 'moveto', 'h': h, 'idx': 0, 'to': [X1 - 1000, YS[2] + 3600]})
o.add({'t': 'settext', 'h': '351335', 's': TTL})
cells = [[2, 2, 'Балка:']]
for k, mk in enumerate(('Бм-15', 'Бм-16', 'Бм-17')):
    bw, bh, lv, segs = B.B114[mk]
    cells += [[3 + k, 0, mk], [3 + k, 1, 'лист 6.7'], [3 + k, 2, 'Балка %s (%dх%d)' % (mk, bw, bh)], [3 + k, 10, str(len(segs))]]
cells += [[6, 2, 'Консоль:'], [7, 0, 'КН-1'], [7, 1, 'лист 4.2'], [7, 2, 'Консоль КН-1 (в составе колонны Км-4)'], [7, 10, str(len(B.CONSOLES))]]
o.add({'t': 'tset', 'h': T, 'cells': cells})
o.add({'t': 'erase', 'h': [T_COL, T_COLH, T_DIM, T_NOTE, T_BEAM, T_SLAB]})

o.add({'t': 'save'})
print(len(o.O), 'ops')
if len(sys.argv) > 1:
    out = ab.run(o.O, 'g24', 1500)
    print('\n'.join(l for l in out.splitlines() if 'ACAD_TABLE' in l or 'errors' in l or l.startswith('ERR')))
