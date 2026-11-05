# -*- coding: utf-8 -*-
"""3.1 опалубка, 3.2 основная, 3.3 доп. нижняя, 3.4 доп. верхняя Фм-1"""
from common import *

L_R20 = 'ф20_арм'; L_R16 = 'ф16_арм'
HID = dict(ltype='HIDDEN2', ltscale=30)
EDGE = 50          # cover at slab edge

# доп. zones: (dir, x0, y0, x1, y1)  dir X = bars along X
ZX = [(5950, -850, 7850, 25550), (43150, -850, 45050, 25550), (7850, 10500, 9850, 14200), (36800, 4600, 38800, 20100)]
ZY = [(5950, -850, 45050, 1050), (5950, 23650, 45050, 25550), (8700, 11350, 37800, 13350), (6950, 9500, 8700, 11500),
      (6950, 13200, 8700, 15200), (37800, 3600, 44200, 5600), (37800, 9950, 44200, 11950), (37800, 12750, 44200, 14750),
      (37800, 19100, 44200, 21100)]
ZC = [(x - 1200, y - 1200, x + 1200, y + 1200) for x, y in COLS_IN]


def base(s, PX, PY, walls=True):
    rect(PX + FM1[0], PY + FM1[1], PX + FM1[2], PY + FM1[3])
    if walls:
        pil = [col_sq(c) for c in COLS_PIL]
        outline(unary_union(walls_geom() + pil), PX, PY, layer=L_THIN)
        for c in COLS_IN: outline(col_sq(c), PX, PY, layer=L_THIN)
    axes(PX, PY, {k: v for k, v in AX.items() if k != '1'}, AY, -4600, 46200, -4600, 26600)
    xs = sorted(AX.values())[1:]; ys = sorted(AY.values())
    chain_h([PX + x for x in [5900] + xs + [45100]], PY - 900, PY - 2000)
    chain_h([PX + x for x in [5900, 45100]], PY - 900, PY - 2800)
    chain_v([PY + y for y in [-900] + ys + [25600]], PX + 5900, PX + 4800)
    chain_v([PY + y for y in [-900, 25600]], PX + 5900, PX + 4000)


def zone_note(pos, step, z, d, PX, PY, sc=100, layer=L_R20, lab_off=(500, 500), frac=0.5):
    """dashed zone, typical bar in the middle, ticks; note 'pos / ш.step'; dims zone width as 200xN"""
    x0, y0, x1, y1 = z
    rect(PX + x0, PY + y0, PX + x1, PY + y1, layer=L_THIN, **HID)
    if d == 'X':
        ym = y0 + (y1 - y0) * frac; n = int(round((y1 - y0) / step))
        pl([(PX + x0, PY + ym), (PX + x1, PY + ym)], layer=layer, lw=40)
        note(pos, 'ш.%d' % step, (PX + (x0 + x1) / 2 + lab_off[0], PY + ym + lab_off[1]), (PX + (x0 + x1) / 2, PY + ym), sc, arrow='oblique')
        return n + 1, x1 - x0
    else:
        xm = x0 + (x1 - x0) * frac; n = int(round((x1 - x0) / step))
        pl([(PX + xm, PY + y0), (PX + xm, PY + y1)], layer=layer, lw=40)
        note(pos, 'ш.%d' % step, (PX + xm + lab_off[0], PY + (y0 + y1) / 2 + lab_off[1]), (PX + xm, PY + (y0 + y1) / 2), sc, arrow='oblique')
        return n + 1, y1 - y0


def build31(X0, Y0):
    s = Sheet('3.1', 'Опалубочный чертеж\\Pфундамента Фм-1', 'Опалубочный чертеж фундамента Фм-1 на отм. -4.000', X0, Y0, 'A1')
    PX, PY = X0 + 9500, Y0 + 15000
    base(s, PX, PY)
    hatch_geom(unary_union(walls_geom() + [col_sq(c) for c in COLS_PIL]), PX, PY)
    for c in COLS_IN: hatch_geom(col_sq(c), PX, PY)
    chain_h([PX + x for x in (5900, 6600, 7000)], PY + 25600, PY + 26800)
    chain_v([PY + y for y in (-900, -200, 200)], PX + 45100, PX + 46300)
    note('Фм-1', '', (PX + 23400, PY + 3400), (PX + 23000, PY + 3000))
    plev('-4,000', (PX + 24000, PY + 9000))
    section('1', (PX + 2600, PY + 3000), (PX + 9500, PY + 3000))
    section('2', (PX + 20000, PY + 10500), (PX + 20000, PY + 14200))
    s.notes(['Общие указания см. лист 1.1. Схему расположения элементов см. лист 2.1.',
             'Плита днища Фм-1 - монолитная, бетон C30/37 W8 F200, толщина 700 мм, консоль 700 мм за наружную грань стен.',
             'Под плитой выполнить бетонную подготовку из бетона C8/10 толщиной 100 мм.',
             'Стены и колонны показаны условно (тонкой линией), см. листы 4.1, 5.1.', 'Разрезы 1-1, 2-2 см. лист 3.5.'], x=X0 + 65100, y=Y0 + 6462)
    return s


POSL = {1900: '2', 2000: '3', 2400: '4'}     # доп. positions by unique Ø20 + L (rule: same Ø+L top/bottom/both directions = one pos)
DOPD = 20


def build32(X0, Y0):
    s = Sheet('3.2', 'Схема расположения основной\Pарматуры фундамента Фм-1', 'Схема расположения основной арматуры фундамента Фм-1 на отм. -4.000', X0, Y0, 'A1')
    PX, PY = X0 + 9500, Y0 + 15000
    base(s, PX, PY, walls=False)
    x0, y0, x1, y1 = FM1[0] + EDGE, FM1[1] + EDGE, FM1[2] - EDGE, FM1[3] - EDGE
    yb = 7300; xb = 34600
    pl([(PX + x0, PY + yb), (PX + x1, PY + yb)], layer=L_R16, lw=40)
    pl([(PX + xb, PY + y0), (PX + xb, PY + y1)], layer=L_R16, lw=40)
    nx = int((y1 - y0) / 200); ny = int((x1 - x0) / 200)
    note('1', 'ш.200', (PX + 16400, PY + yb + 500), (PX + 16000, PY + yb), arrow='oblique')
    note('1', 'ш.200', (PX + xb + 400, PY + 16900), (PX + xb, PY + 16500), arrow='oblique')
    for (tx, ty, dx, dy) in ((x0, yb, 400, 400), (x1, yb, -1400, 400), (xb, y0, 400, 400), (xb, y1, 400, -400)):
        note('Ск1', 'ш.200', (PX + tx + dx, PY + ty + dy), (PX + tx, PY + ty), arrow='oblique')
    dim((PX + x0, PY + 25600 + 0), (PX + x1, PY + 25600), (PX + x0, PY + 26800), 0.0, 100, txt='200х%d=%d' % (ny, ny * 200))
    dim((PX + 45100, PY + y0), (PX + 45100, PY + y1), (PX + 46300, PY + y0), math.pi / 2, 100, txt='200х%d=%d' % (nx, nx * 200))
    s.notes(['Общие указания см. лист 1.1. Данный лист читать совместно с листами 3.1, 3.3 - 3.7.',
             'Поз. 1 - %%C16 A500C шаг 200 в нижней и верхней сетке в обоих направлениях (основная арматура плиты толщиной 700 мм).',
             'По периметру плиты - П-образная скоба Ск1* %%C16 A500C, высота 620 мм (Hплиты - 80), ноги 400 мм, шаг 200, отступ 20 от грани.',
             'Стыки внахлестку без сварки, длина нахлеста 61d (980 мм); в одном сечении стыковать не более 50% стержней. Расход в пог.м. с учетом нахлеста.',
             'Защитный слой бетона: низ - 50 мм, верх - 40 мм.'], x=X0 + 65100, y=Y0 + 6462)
    return s, nx + 1, ny + 1, x1 - x0, y1 - y0


SHEETS_DOP = {'3.3': (False, 'X'), '3.4': (True, 'X'), '3.5': (False, 'Y'), '3.6': (True, 'Y')}


def build_dop(X0, Y0, num):
    top, fam = SHEETS_DOP[num]
    zn = 'верхней' if top else 'нижней'; ax = 'буквенным' if fam == 'X' else 'цифровым'
    s = Sheet(num, 'Схема расположения доп. арматуры Фм-1\P%s зоны по %s осям' % (zn, ax),
              'Схема расположения дополнительной арматуры фундамента Фм-1 %s зоны по %s осям на отм. -4.000' % (zn, ax), X0, Y0, 'A1')
    PX, PY = X0 + 9500, Y0 + 15000
    base(s, PX, PY)
    lr = 'ф%d_арм' % DOPD
    if fam == 'X':
        for z in ZX:
            lo = (1200, 500) if z[0] < 40000 else (-2400, 500)
            zone_note(POSL[int(z[2] - z[0])], 200, z, 'X', PX, PY, layer=lr, lab_off=lo)
        for z in ZC: zone_note(POSL[2400], 200, z, 'X', PX, PY, layer=lr, lab_off=(1500, 700))
        z = ZX[0]; dim((PX + z[0], PY + 25600), (PX + z[2], PY + 25600), (PX + z[0], PY + 26800), 0.0)
        z = ZC[0]; chain_h([PX + z[0], PX + COLS_IN[0][0], PX + z[2]], PY + z[3], PY + z[3] + 700)
    else:
        for z in ZY: zone_note(POSL[int(z[3] - z[1])], 200, z, 'Y', PX, PY, layer=lr, lab_off=(500, 1200))
        for z in ZC: zone_note(POSL[2400], 200, z, 'Y', PX, PY, layer=lr, lab_off=(700, 1500))
        z = ZY[0]; dim((PX + 45100, PY + z[1]), (PX + 45100, PY + z[3]), (PX + 46300, PY + z[1]), math.pi / 2)
        z = ZC[0]; chain_v([PY + z[1], PY + COLS_IN[0][1], PY + z[3]], PX + z[2], PX + z[2] + 700)
    s.notes(['Общие указания см. лист 1.1. Данный лист читать совместно с листами 3.1 - 3.7.',
             'Дополнительные стержни %%C%d A500C укладывать в одном уровне с основной арматурой %s сетки, посередине между основными стержнями (шаг 200 со смещением 100).' % (DOPD, zn),
             'Зоны дополнительного армирования показаны штриховой линией; в каждой зоне показан один стержень. Количество - см. спецификацию на листе 3.7.',
             'Стыки рабочей арматуры выполнять без сварки внахлестку.'], x=X0 + 65100, y=Y0 + 6462)
    return s


def dop_counts():
    """all доп. positions: {pos: [L, n]} over 4 faces/directions"""
    cnt = {}
    def add(k, n, L):
        c = cnt.setdefault(k, [L, 0]); c[1] += n
    for face in (0, 1):
        for z in ZX: L = int(z[2] - z[0]); add(POSL[L], int(round((z[3] - z[1]) / 200)) + 1, L)
        for z in ZY: L = int(z[3] - z[1]); add(POSL[L], int(round((z[2] - z[0]) / 200)) + 1, L)
        for z in ZC: add(POSL[2400], 2 * 13, 2400)
    return cnt
