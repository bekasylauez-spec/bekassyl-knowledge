"""Лист 2.3 «+6.200» — v3 по правилам Bekassyl."""
import sys
import ab, pl_ob, pl2, beams_ob as B
from pl_ob import AX, AY, COLX, COLY

WIN = [-1374603, -1749172, -1285503, -1707172]
X1, YA = -1524253.0 + (WIN[0] + 1552803), -1729469.0
XS = [X1 + v for v in AX]; YS = [YA + v for v in AY]
P = lambda x, y: (X1 + x, YA + y)
ABK = r'D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК ВАРИАНТ 2.dwg'
IMP = ['344854', '344853', '3448BE', '3450DE', '34E543', '34E542', '3C3717']
T_COL, T_COLH, T_DIM, T_NOTE, T_BEAM, T_SLAB, T_THIN = ['T23c:' + h for h in IMP]
TABLE = '34CCAD'

si = pl_ob.sheetinfo(WIN)
o = pl2.Ops('g23c_')
o.add({'t': 'sysvar', 'n': 'TILEMODE', 'v': 1})
sx0, sy0, sx1, sy1 = B.SLAB62
r1y, r1x, EB, EL, used = pl2.rows(o, si, XS, YS, X1 + sx0, YA + sy0, True, True, ytop=YA + sy1 + 600, xright=X1 + sx1 + 600)
keep = si['keep'] + si['title'] + used + [TABLE]
o.O.insert(1, {'t': 'eraseregion', 'win': WIN, 'keep': keep})
o.add({'t': 'import', 'file': ABK, 'h': IMP, 'base': [0, 0], 'to': [0, 0], 'pre': 'T23c:'})

# slab, openings (template broken line)
o.ring(T_SLAB, [P(sx0, sy0), P(sx1, sy0), P(sx1, sy1), P(sx0, sy1)])
OP = {'О-1': (250, 2800, 2950, 5800), 'О-2': (3550, 7975, 16400, 10225), 'О-3': (18000, 7800, 18400, 10200)}
for k, (a, b, c, d) in OP.items():
    o.opening(T_SLAB, T_THIN, X1 + a, YA + b, X1 + c, YA + d)


def half_at(x, y, along_x):
    if x in AX and y in AY: return COLX / 2 if along_x else COLY / 2
    for mk, (bw, bh, lv, segs) in B.B62.items():
        for x0, y0, x1, y1 in segs:
            if along_x and x0 == x1 == x and min(y0, y1) <= y <= max(y0, y1): return bw / 2
            if not along_x and y0 == y1 == y and min(x0, x1) <= x <= max(x0, x1): return bw / 2
    return 0


for mk, (bw, bh, lv, segs) in B.B62.items():
    for seg in segs:
        for x0, y0, x1, y1 in B.pieces(seg):
            t = o.tag(); o.add({'t': 'clone', 'h': T_BEAM, 'tag': t})
            if y0 == y1:
                a = x0 + half_at(x0, y0, True); c = x1 - half_at(x1, y1, True)
                pts = [P(a, y0 - bw / 2), P(c, y0 - bw / 2), P(c, y0 + bw / 2), P(a, y0 + bw / 2)]
            else:
                a = y0 + half_at(x0, y0, False); c = y1 - half_at(x1, y1, False)
                pts = [P(x0 - bw / 2, a), P(x0 + bw / 2, a), P(x0 + bw / 2, c), P(x0 - bw / 2, c)]
            o.add({'t': 'plset', 'h': t, 'p': [list(p) for p in pts], 'closed': True})
for x in XS:
    for y in YS:
        o.rect(T_COL, x - COLX / 2, y - COLY / 2, x + COLX / 2, y + COLY / 2, T_COLH)

# marks: (text, target, dx, dy, offset)
M = [('Бм-1', (5500, 225), 1, 1, 600), ('Бм-1', (10000, 11775), 1, -1, 700), ('Бм-2', (10000, 6200), 1, 1, 600),
     ('Бм-3', (29000, 225), -1, 1, 600), ('Бм-3', (29000, 6225), -1, 1, 600), ('Бм-3', (29000, 11775), -1, -1, 700),
     ('Бм-4', (5500, 3200), 1, 1, 600), ('Бм-5', (23000, 3200), -1, 1, 600), ('Бм-6', (2400, 2500), -1, -1, 600),
     ('Бм-7', (5000, 7575), 1, -1, 700), ('Бм-7', (5000, 10625), 1, 1, 600),
     ('Бм-8', (23000, 7500), -1, -1, 600), ('Бм-8', (23000, 10500), -1, 1, 600),
     ('Бм-9', (250, 9000), 1, 1, 600), ('Бм-10', (3550, 4500), 1, 1, 600), ('Бм-11', (8050, 4500), 1, 1, 600),
     ('Бм-12', (12600, 4500), 1, 1, 600), ('Бм-12', (17100, 4500), 1, 1, 600),
     ('Бм-13', (19775, 1500), -1, 1, 600), ('Бм-13', (25775, 4500), -1, 1, 600), ('Бм-13', (31775, 4500), -1, 1, 600),
     ('Пм-2', (28000, 9000), 1, 1, 600), ('О-1', (2950, 5000), -1, -1, 600), ('О-2', (14000, 10225), -1, -1, 900),
     ]
for txt, tg, dx, dy, off in M:
    o.mark(T_NOTE, txt, P(*tg), dx, dy, off)
h = o.tag(); o.add({'t': 'clone', 'h': T_NOTE, 'tag': h}); o.add({'t': 'moveto', 'h': h, 'idx': 1, 'to': list(P(18200, 7800))})
o.add({'t': 'mcset', 'h': h, 'set': {'FirstLine': 'О-3', 'Origin': list(P(18550, 7000)), 'Angle': 0.0, 'Arrow': 'Arrow'}})
# Бм-14: narrow bay between the trimmer and axis 6 -> steep leader
h = o.tag(); o.add({'t': 'clone', 'h': T_NOTE, 'tag': h}); o.add({'t': 'moveto', 'h': h, 'idx': 1, 'to': list(P(17700, 9000))})
o.add({'t': 'mcset', 'h': h, 'set': {'FirstLine': 'Бм-14', 'Origin': list(P(16200, 9600)), 'Angle': 3.141592653589793, 'Arrow': 'Arrow'}})

# outer chains: row 1 = slab edges / axes (bottom), slab edges + О-1 faces (left)
o.chain2(T_DIM, [X1 + sx0, XS[0]], r1y, origin=YA + sy0, out=-1)
o.chain2(T_DIM, [XS[-1], X1 + sx1], r1y, origin=YA + sy0, out=-1)
o.chain2(T_DIM, [YA + v for v in (12000, sy1)], r1x, vertical=True, origin=X1 + sx0, out=-1)
o.chain2(T_DIM, [YA + v for v in (sy0, 0, 2800, 5800, 6000)], r1x, vertical=True, origin=X1 + sx0, out=-1,
         origins={round(YA + 2800, 1): X1 + 250, round(YA + 5800, 1): X1 + 250})
# О-1 width inside the opening (axis -> face -> size -> face -> axis), small values inside next to their faces
o.chain2(T_DIM, [X1 + v for v in (0, 250, 2950, 3250)], YA + 3300, out=-1, txo={0: P(650, 2950), 2: P(2550, 2950)})
# О-2 inside the opening
o.chain2(T_DIM, [X1 + v for v in (3250, 3550, 16400, 16750)], YA + 8400, out=1, txo={0: P(4000, 8850), 2: P(15950, 8850)})
o.chain2(T_DIM, [YA + v for v in (6000, 7975, 10225, 12000)], X1 + 9000, vertical=True, out=1)
# О-3: horizontal below it (between Бм-2 and Бм-8), vertical right of axis 6
o.chain2(T_DIM, [X1 + v for v in (18000, 18400, 20000)], YA + 11000, out=1,
         origins={round(X1 + 18000, 1): YA + 10200, round(X1 + 18400, 1): YA + 10200})
o.chain2(T_DIM, [YA + v for v in (6000, 7800, 10200, 12000)], X1 + 21000, vertical=True, out=1,
         origins={round(YA + 7800, 1): X1 + 18400, round(YA + 10200, 1): X1 + 18400})
# beam widths: once per mark (b/2|b/2) near the label
for mk, c, at, vert in (('Бм-9', 0, 10900, False), ('Бм-10', 3250, 10900, False), ('Бм-11', 7750, 3700, False),
                        ('Бм-12', 12250, 3700, False), ('Бм-13', 26000, 3700, False),
                        ('Бм-1', 0, 4500, True), ('Бм-2', 6000, 14500, True), ('Бм-3', 0, 30500, True)):
    bw = (B.B62.get(mk) or B.B114.get(mk))[0]
    if vert: o.bind2(T_DIM, YA + c, bw / 2, X1 + at, vertical=True, out=1)
    else: o.bind2(T_DIM, X1 + c, bw / 2, YA + at, out=1)
cnt = [[3 + k, 10, str(len(B.B62['Бм-%d' % (k + 1)][3]))] for k in range(14)]
o.add({'t': 'tset', 'h': TABLE, 'cells': cnt})

TTL = 'Схема расположения элементов на отм. +6.200'
for h in si['title']:
    o.add({'t': 'settext', 'h': h, 's': '{\\L' + TTL + '}'}); o.add({'t': 'moveto', 'h': h, 'idx': 0, 'to': [X1 - 1000, YA + sy1 + 2200]})
o.add({'t': 'mtext', 'at': [-1304403, -1728539 + 250 + 3400], 'h': 250, 'w': 17800, 'layer': 'Размеры',
       's': '1. Верх плиты Пм-2 в осях 1-6 - отм. +6.200; в осях 6-8 плита покрытия с уклоном 4% к оси 8 (+6.200 по оси 6, +5.700 по оси 8).\\P'
            '2. Балки Бм показаны пунктиром, верх балок - по верху плиты. Колонны - см. лист 2.1.\\P'
            '3. Отверстия О-1 (лестница), О-2 (над резервуарами), О-3 - в свету между гранями обрамляющих балок.'})
o.add({'t': 'erase', 'h': ['T23c:' + h for h in IMP]})
o.add({'t': 'save'})
print(len(o.O), 'ops')
if len(sys.argv) > 1:
    out = ab.run(o.O, 'g23c', 1500)
    print('\n'.join(l for l in out.splitlines() if 'errors' in l or l.startswith('ERR') or 'no prop' in l)[-1500:])
