"""Лист 2.3 «Схема расположения элементов на отм. +6.200» — плита Пм-2, балки Бм-1…Бм-14, колонны."""
import sys
import ab, pl_ob, beams_ob as B
from pl_ob import AX, AY, COLX, COLY

WIN = [-1374603, -1749172, -1285503, -1707172]
DX = WIN[0] - (-1552803)
X1, YA = -1524253.0 + DX, -1729469.0
XS = [X1 + v for v in AX]; YS = [YA + v for v in AY]
P = lambda x, y: (X1 + x, YA + y)
ABK = r'D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК ВАРИАНТ 2.dwg'
T_COL, T_COLH, T_DIM, T_NOTE = 'T23:344854', 'T23:344853', 'T23:3448BE', 'T23:3450DE'
T_BEAM, T_SLAB = 'T23:34E543', 'T23:34E542'          # analog 2.3: beam (HIDDEN) and slab outline

SHEETOF = {'Бм-1': '6.1', 'Бм-2': '6.1', 'Бм-3': '6.1', 'Бм-4': '6.2', 'Бм-5': '6.2', 'Бм-6': '6.2', 'Бм-7': '6.3', 'Бм-8': '6.3',
           'Бм-9': '6.4', 'Бм-10': '6.4', 'Бм-11': '6.5', 'Бм-12': '6.5', 'Бм-13': '6.6', 'Бм-14': '6.6'}

si = pl_ob.sheetinfo(WIN)
o = pl_ob.Ops('f23_')
o.add({'t': 'sysvar', 'n': 'TILEMODE', 'v': 1})
EB = YA - 2300; EL = X1 - 5331
axh = pl_ob.setup_axes(o, si, XS, YS, EB, EL, YA - 1700, YA - 2400, (X1 - 4131, X1 - 4831))
o.O.insert(1, {'t': 'eraseregion', 'win': WIN, 'keep': si['keep'] + si['title'] + axh})
o.add({'t': 'import', 'file': ABK, 'h': ['344854', '344853', '3448BE', '3450DE', '34E543', '34E542'], 'base': [0, 0], 'to': [0, 0], 'pre': 'T23:'})


def half_at(x, y, along_x):
    """half-width of what a beam end at (x, y) runs into"""
    if x in AX and y in AY:
        return COLX / 2 if along_x else COLY / 2
    for mk, (b, h, lv, segs) in B.B62.items():
        for x0, y0, x1, y1 in segs:
            if along_x and x0 == x1 == x and min(y0, y1) <= y <= max(y0, y1): return b / 2
            if not along_x and y0 == y1 == y and min(x0, x1) <= x <= max(x0, x1): return b / 2
    return 0


# slab Пм-2 outline (to the outer column faces) and openings (clear between beam faces) with one diagonal
sx0, sy0, sx1, sy1 = B.SLAB62
o.ring(T_SLAB, [P(sx0, sy0), P(sx1, sy0), P(sx1, sy1), P(sx0, sy1)])
OP = {'О-1': (250, 2800, 2950, 5800), 'О-2': (3550, 7975, 16400, 10225), 'О-3': (18000, 7800, 18400, 10200)}
for k, (a, b, c, d) in OP.items():
    o.ring(T_SLAB, [P(a, b), P(c, b), P(c, d), P(a, d)])
    t = o.tag(); o.add({'t': 'clone', 'h': T_SLAB, 'tag': t}); o.add({'t': 'plset', 'h': t, 'p': [list(P(a, b)), list(P(c, d))], 'closed': False})

# beams (hidden lines), clipped at column faces / supporting beam faces
for mk, (bw, bh, lv, segs) in B.B62.items():
    for seg in segs:
        for x0, y0, x1, y1 in B.pieces(seg):
            if y0 == y1:
                a = x0 + half_at(x0, y0, True); c = x1 - half_at(x1, y1, True)
                o.add({'t': 'clone', 'h': T_BEAM, 'tag': o.tag()}); o.add({'t': 'plset', 'h': 'f23_%d' % o.n, 'p': [list(P(a, y0 - bw / 2)), list(P(c, y0 - bw / 2)), list(P(c, y0 + bw / 2)), list(P(a, y0 + bw / 2))], 'closed': True})
            else:
                a = y0 + half_at(x0, y0, False); c = y1 - half_at(x1, y1, False)
                o.add({'t': 'clone', 'h': T_BEAM, 'tag': o.tag()}); o.add({'t': 'plset', 'h': 'f23_%d' % o.n, 'p': [list(P(x0 - bw / 2, a)), list(P(x0 + bw / 2, a)), list(P(x0 + bw / 2, c)), list(P(x0 - bw / 2, c))], 'closed': True})

# columns (cut)
for x in XS:
    for y in YS:
        o.rect(T_COL, x - COLX / 2, y - COLY / 2, x + COLX / 2, y + COLY / 2, T_COLH)

# marks: (mark, target, origin) in local mm
LB = [('Бм-1', (5500, 225), (6000, 900)), ('Бм-1', (10000, 11775), (10500, 11000)),
      ('Бм-2', (10000, 6200), (10500, 6900)),
      ('Бм-3', (29000, 225), (29500, 900)), ('Бм-3', (29000, 6225), (29500, 6900)), ('Бм-3', (29000, 11775), (29500, 11000)),
      ('Бм-4', (10000, 3200), (10500, 3700)), ('Бм-5', (23000, 3200), (23500, 3700)),
      ('Бм-6', (1600, 2500), (600, 1500)),
      ('Бм-7', (4400, 7575), (4600, 7000)), ('Бм-7', (4400, 10625), (4600, 11200)),
      ('Бм-8', (23000, 7500), (23500, 7000)), ('Бм-8', (23000, 10500), (23500, 11000)),
      ('Бм-9', (250, 9000), (900, 9500)), ('Бм-10', (3550, 4500), (4150, 5000)), ('Бм-11', (8050, 4500), (8650, 5000)),
      ('Бм-12', (12600, 4500), (13150, 5000)), ('Бм-12', (17100, 4500), (17650, 5000)),
      ('Бм-13', (20225, 4500), (20900, 5000)), ('Бм-13', (26225, 4500), (26900, 5000)), ('Бм-13', (31775, 4500), (30500, 5000)),
      ('Бм-14', (17700, 7950), (17300, 7100)),
      ('Пм-2', (28000, 4500), (28700, 5000)), ('О-1', (2600, 4000), (1300, 6900)), ('О-2', (13800, 9800), (13300, 11100)), ('О-3', (18200, 9000), (18650, 11300))]
for mk, tg, og in LB:
    o.note(T_NOTE, mk, P(*tg), P(*og))

# dims: slab edges (top / right), openings
SX0, SX1, SY0, SY1 = [X1 + sx0, X1 + sx1, YA + sy0, YA + sy1]
o.chain(T_DIM, XS, SY1 + 900)
o.dim(T_DIM, (SX0, SY1 + 900), (XS[0], SY1 + 900), (SX0, SY1 + 900), tx=(SX0 - 450, SY1 + 900 + 187))
o.dim(T_DIM, (XS[-1], SY1 + 900), (SX1, SY1 + 900), (XS[-1], SY1 + 900), tx=(SX1 + 450, SY1 + 900 + 187))
o.dim(T_DIM, (SX0, SY1 + 900), (SX1, SY1 + 900), (SX0, SY1 + 1600))
o.chain(T_DIM, [SY0] + YS + [SY1], SX1 + 1500, vertical=True)
o.dim(T_DIM, (SX1 + 1500, SY0), (SX1 + 1500, SY1), (SX1 + 2200, SY0), vertical=True)
o.dim(T_DIM, P(250, 3400), P(2950, 3400), P(250, 3400))
o.dim(T_DIM, P(800, 2800), P(800, 5800), P(800, 2800), True)
o.dim(T_DIM, P(3550, 8500), P(16400, 8500), P(3550, 8500))
o.dim(T_DIM, P(15000, 7975), P(15000, 10225), P(15000, 7975), True)
o.dim(T_DIM, P(18000, 11000), P(18400, 11000), P(18000, 11000), tx=P(17500, 11000 + 187))
o.dim(T_DIM, P(19200, 7800), P(19200, 10200), P(19200, 7800), True)

TTL = 'Схема расположения элементов на отм. +6.200'
for h in si['title']:
    o.add({'t': 'settext', 'h': h, 's': '{\\L' + TTL + '}'})
    o.add({'t': 'moveto', 'h': h, 'idx': 0, 'to': [X1 - 1000, YS[2] + 3600]})
o.add({'t': 'mtext', 'at': [X1, YA - 4700], 'h': 250, 'w': 30000, 'style': 'ISOCPEUR', 'layer': 'Размеры',
       's': '1. Верх плиты Пм-2 в осях 1-6 - отм. +6.200; в осях 6-8 плита покрытия с уклоном 4% к оси 8 (верх +6.200 по оси 6, +5.700 по оси 8).\\P'
            '2. Балки Бм показаны пунктиром, верх балок - по верху плиты. Колонны Км - см. лист 2.1.\\P'
            '3. Отверстия О-1 (лестница), О-2 (над резервуарами), О-3 - в свету между гранями обрамляющих балок Бм-2, Бм-6, Бм-7, Бм-8, Бм-9…Бм-14.'})
T = '34CCAD'
# rows already inserted (run once): o.add({'t': 'trows', 'h': T, 'mode': 'ins', 'at': 5, 'from': 4, 'n': 12})
cells = [[2, 2, 'Балка:']]
for k in range(14):
    mk = 'Бм-%d' % (k + 1); bw, bh, lv, segs = B.B62[mk]
    cells += [[3 + k, 0, mk], [3 + k, 1, 'лист ' + SHEETOF[mk]], [3 + k, 2, 'Балка %s (%dх%d)' % (mk, bw, bh)], [3 + k, 10, str(len(segs))]]
cells += [[18, 2, 'Плита:'], [19, 0, 'Пм-2'], [19, 1, 'лист 7.2'], [19, 2, 'Плита Пм-2 (t=200)'], [19, 10, '1']]
o.add({'t': 'tset', 'h': T, 'cells': cells})
o.add({'t': 'erase', 'h': [T_COL, T_COLH, T_DIM, T_NOTE, T_BEAM, T_SLAB]})
o.add({'t': 'list', 'win': [-1304000, -1749000, -1285503, -1707172]})
o.add({'t': 'save'})
print(len(o.O), 'ops')
if len(sys.argv) > 1:
    out = ab.run(o.O, 'g23', 1500)
    print('\n'.join(l for l in out.splitlines() if not l.startswith('clone') and not l.startswith('AXIS'))[-1500:])
