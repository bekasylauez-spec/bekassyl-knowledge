# -*- coding: utf-8 -*-
"""Стены по осям: 3 листа на марку (опалубка, армирование, спецификация) в стиле аналога ЖК Галакси См-3."""
import sys, json, math
import lib
from lib import *
from common import spec_table, rowL, rowPM, KG
import ab

Z0 = 0.0          # local: elevation z (mm), 0 = ±0.000
ZF, ZW, ZS = -4000, 3300, 3500     # Фм top, wall top, Пм-1 top
LAP20, LAP16 = 1220, 980
HID = dict(ltype='HIDDEN2', ltscale=20)

# mark, title-axis text, count, piece (s0, s1) along wall, axes [(name, s)], ends ('corner'|'tee'), joins [(s, side)] = crossing walls
WALLS = {
    'См-1': dict(ax='А (Д)', pre='оси', cnt=2, s0=6600, s1=44400, axes=[('2', 6800), ('3', 13350), ('4', 19350), ('5', 25350), ('6', 31350), ('7', 37800), ('8', 44200)], joins=[(6800, 200), (44200, 200)]),
    'См-2': dict(ax='2', pre='оси', cnt=1, s0=200, s1=24500, axes=[('А', 0), ('Б', 6200), ('В', 12350), ('Г', 18500), ('Д', 24700)], joins=[(10500, 200), (14200, 200), (5890, 250), (13810, 250), (19170, 250)]),
    'См-3': dict(ax='8', pre='оси', cnt=1, s0=200, s1=24500, axes=[('А', 0), ('Б', 6200), ('В', 12350), ('Г', 18500), ('Д', 24700)], joins=[(4600, 200), (10950, 200), (13750, 200), (20100, 200)]),
    'См-4': dict(ax='В', pre='оси', cnt=1, s0=8900, s1=37600, axes=[('3', 13350), ('4', 19350), ('5', 25350), ('6', 31350), ('7', 37800)], joins=[]),
    'См-5': dict(ax='7', pre='оси', cnt=1, s0=4400, s1=20300, axes=[('Б', 6200), ('В', 12350), ('Г', 18500)], joins=[(10950, 200), (12350, 200), (13750, 200)]),
    'См-6': dict(ax='7-8', pre='осям', cnt=4, s0=38000, s1=44000, axes=[('7', 37800), ('8', 44200)], joins=[]),
    'См-7': dict(ax='2-3', pre='осям', cnt=1, s0=10300, s1=14400, axes=[('В', 12350)], joins=[(12350, 200)]),
    'См-8': dict(ax='2-3', pre='осям', cnt=2, s0=7000, s1=8500, axes=[('2', 6800)], joins=[]),
}


def tx_c(center, X0, s):
    hw = 0.36 * 300 * len(s)
    return max(center, X0 + 2500 + hw)


def brk_v(x, z0, z1):
    zm = (z0 + z1) / 2
    pl([(x, z0 - 60), (x, zm - 60), (x - 40, zm - 20), (x + 40, zm + 20), (x, zm + 60), (x, z1 + 60)], layer=L_THIN)


def elev_base(EX, EZ, w, slab_hatch=True, hidden_bands=False):
    """wall elevation: Фм-1 band, wall outline, Пм-1 band, crossing walls strips; EX/EZ model origin of s=0 / z=0"""
    s0, s1 = w['s0'], w['s1']
    X = lambda s: EX + s; Z = lambda z: EZ + z
    e0, e1 = s0 - 600, s1 + 600
    # bands
    for za, zb in ((ZF - 700, ZF), (ZW, ZS)):
        pl([(X(e0), Z(za)), (X(e1), Z(za))]); pl([(X(e0), Z(zb)), (X(e1), Z(zb))])
        brk_v(X(e0), Z(za), Z(zb)); brk_v(X(e1), Z(za), Z(zb))
        if slab_hatch: hatch([[(X(e0), Z(za)), (X(e1), Z(za)), (X(e1), Z(zb)), (X(e0), Z(zb))]], sc=20)
    pl([(X(s0), Z(ZF)), (X(s0), Z(ZW))]); pl([(X(s1), Z(ZF)), (X(s1), Z(ZW))])
    for j, hw in w['joins']:
        for d in (-hw, hw):
            if s0 < j + d < s1: pl([(X(j + d), Z(ZF)), (X(j + d), Z(ZW))], layer=L_THIN)
    return X, Z


def axes_dims(X, Z, w, zax, sc=100):
    for name, s in w['axes']:
        axis(name, (X(s), Z(ZF - 900)), (X(s), Z(zax)), sc, True)
    xs = sorted(set([w['s0'], w['s1']] + [s for _, s in w['axes']]))
    chain_h([X(s) for s in xs], Z(ZF - 700), Z(ZF - 1500), sc)
    dim((X(w['s0']), Z(ZF - 700)), (X(w['s1']), Z(ZF - 700)), (X(w['s0']), Z(ZF - 2300)), 0, sc, tx=(X((w['s0'] + w['s1']) / 2) + 1400, Z(ZF - 2300) + 90))


def levels(X, Z, w, side_x):
    for z in (ZW, ZF):
        lev(Z(0), (X(w['s0'] - 600), Z(z)), 100, side='L', ext=1500)
    for z in (ZS, ZF - 700):
        lev(Z(0), (X(w['s1'] + 600), Z(z)), 100, side='R', ext=1500)
    chain_v([Z(ZF - 700), Z(ZF), Z(ZW), Z(ZS)], X(w['s0'] - 600), X(w['s0'] - 1000))


def sheet_opal(num, mk, w, X0, Y0):
    s = Sheet(num, 'Опалубочный чертеж монолитной\\Pстены по %s %s стена %s' % (w['pre'], w['ax'], mk),
              None, X0, Y0, 'A2')
    EX = X0 + 8500 - w['s0']; EZ = Y0 + 30000
    X, Z = elev_base(EX, EZ, w)
    levels(X, Z, w, X(w['s0'] - 1700))
    axes_dims(X, Z, w, ZF - 3300)
    ttl_x = tx_c((X(w['s0']) + X(w['s1'])) / 2, X0, 'Горизонтальное армирование монолитной стены по %s %s стена %s (тол.400мм)' % (w['pre'], w['ax'], mk))
    s.text(title_u('Опалубочный чертеж монолитной стены по %s %s стена %s (тол.400мм)' % (w['pre'], w['ax'], mk)), ttl_x, Z(ZS) + 1800, 300, att=8, layer='0')
    section('1', (X(w['s0']) - 2600, Z(1800)), (X(w['s0']) - 1700, Z(1800)))
    section('1', (X(w['s1']) + 2600, Z(1800)), (X(w['s1']) + 1700, Z(1800)))
    # plan 1-1 (опалубка)
    PZ = Y0 + 12000
    PX = lambda s_: EX + s_
    rect(PX(w['s0']), PZ - 200, PX(w['s1']), PZ + 200)
    hatch([[(PX(w['s0']), PZ - 200), (PX(w['s1']), PZ - 200), (PX(w['s1']), PZ + 200), (PX(w['s0']), PZ + 200)]], sc=20)
    for j in w['joins']:
        for side in (-1, 1):
            pass
    for name, s_ in w['axes']:
        axis(name, (PX(s_), PZ + 700), (PX(s_), PZ - 2800), 100, True)
    chain_h([PX(s_) for s_ in sorted(set([w['s0'], w['s1']] + [q for _, q in w['axes']]))], PZ - 200, PZ - 1100)
    dim((PX(w['s0']), PZ - 200), (PX(w['s1']), PZ - 200), (PX(w['s0']), PZ - 1900), 0, 100, tx=(PX((w['s0'] + w['s1']) / 2) + 1400, PZ - 1900 + 90))
    dim((PX(w['s0']), PZ - 200), (PX(w['s0']), PZ), (PX(w['s0']) - 700, PZ - 200), 1.5708, 100, tx=(PX(w['s0']) - 790, PZ - 800))
    dim((PX(w['s0']), PZ), (PX(w['s0']), PZ + 200), (PX(w['s0']) - 700, PZ), 1.5708, 100, tx=(PX(w['s0']) - 790, PZ + 800))
    s.text(title_u('Разрез 1 - 1 (Опалубка) М1:100'), ttl_x, PZ + 1700, 300, att=8, layer='0')
    s.notes(['Общие указания см. лист 1.1. Схему расположения стен см. лист 2.1.',
             'Данный лист читать совместно с листами %s.' % w['rng'],
             'Стена %s - монолитная, толщина 400 мм, бетон C30/37 W8 F200; количество - %d шт.' % (mk, w['cnt']),
             'Рабочие швы бетонирования стена/плита Фм-1 и стена/плита Пм-1 - с гидрошпонкой (ПВХ шпонка шириной 250 мм).'],
            x=X0 + 2600, y=Y0 + 962, w=20000)
    return s


def sheet_arm(num, mk, w, X0, Y0, R):
    s = Sheet(num, 'Вертикальное и горизонтальное\\Pармирование стены %s' % mk, None, X0, Y0, 'A2')
    EX = X0 + 8500 - w['s0']
    L = w['s1'] - w['s0']
    # ---- vertical (top)
    EZ = Y0 + 31500
    X, Z = elev_base(EX, EZ, w, slab_hatch=False)
    levels(X, Z, w, X(w['s0'] - 1700))
    ttl_x = tx_c((X(w['s0']) + X(w['s1'])) / 2, X0, 'Горизонтальное армирование монолитной стены по %s %s стена %s (тол.400мм)' % (w['pre'], w['ax'], mk))
    s.text(title_u('Вертикальное армирование монолитной стены по %s %s стена %s (тол.400мм)' % (w['pre'], w['ax'], mk)), ttl_x, Z(ZS) + 1500, 300, att=8, layer='0')
    v0, v1 = w['s0'] + 50, w['s1'] - 50
    for xv in (v0, v0 + 200, v1 - 200, v1):
        top = ZW - 50
        bot = ZF if xv in (v0, v1 - 200) else ZF + 1590
        pl([(X(xv), Z(bot)), (X(xv), Z(top))], layer='ф20_арм', lw=40)
    for xs_, sg in ((v0, -1), (v1, 1)):
        pl([(X(xs_) + sg * 25, Z(ZW - 50 - LAP20)), (X(xs_) + sg * 25, Z(ZW - 50))], layer='ф20_арм', lw=40)
    # dowels (dashed) 1220 / 2810 at the left end
    pl([(X(v0) + 40, Z(ZF)), (X(v0) + 40, Z(ZF + 1220))], layer='ф20_арм', lw=25, **HID)
    pl([(X(v0 + 200) + 40, Z(ZF)), (X(v0 + 200) + 40, Z(ZF + 2810))], layer='ф20_арм', lw=25, **HID)
    dim((X(v0), Z(ZF)), (X(v0), Z(ZF + 1220)), (X(w['s0']) - 350, Z(ZF)), 1.5708, 100)
    dim((X(v0), Z(ZF + 1220)), (X(v0), Z(ZF + 1590)), (X(w['s0']) - 350, Z(ZF + 1220)), 1.5708, 100, tx=(X(w['s0']) - 440, Z(ZF + 1405)))
    dim((X(v0), Z(ZF + 1590)), (X(v0), Z(ZF + 2810)), (X(w['s0']) - 350, Z(ZF + 1590)), 1.5708, 100)
    note('1;2(%%C20)', 'ш.200', (X(w['s1']) + 900, Z(800)), (X(v1), Z(300)))
    note('Ск1(%%C20)', 'ш.200', (X(w['s1']) + 900, Z(ZW - 600)), (X(v1) + 25, Z(ZW - 900)))
    note('Вп поз.1;2;3', 'см. л. 3.10', (X(w['s1']) + 900, Z(ZF + 900)), (X(v1), Z(ZF + 500)))
    mid = (v0 + v1) / 2
    n = int(round((v1 - v0) / 200.0))
    dim((X(v0), Z(ZF - 700)), (X(v1), Z(ZF - 700)), (X(v0), Z(ZF - 1300)), 0, 100, txt='200х%d=%d' % (n, n * 200))
    # ---- horizontal (bottom)
    EZ2 = Y0 + 16000
    X2 = lambda s_: EX + s_; Z2 = lambda z: EZ2 + z
    elev_base(EX, EZ2, w, slab_hatch=False)
    levels(X2, Z2, w, X2(w['s0'] - 1700))
    s.text(title_u('Горизонтальное армирование монолитной стены по %s %s стена %s (тол.400мм)' % (w['pre'], w['ax'], mk)), ttl_x, Z2(ZS) + 1500, 300, att=8, layer='0')
    h0, h1 = ZF + 50, ZW - 50
    nr = int(round((h1 - h0) / 200.0))
    for zz in (h0, h0 + 200, h1 - 200, h1):
        pl([(X2(w['s0'] + 50), Z2(zz)), (X2(w['s1'] - 50), Z2(zz))], layer='ф16_арм', lw=40)
    for sx in (w['s0'] + 30, w['s1'] - 30):
        pl([(X2(sx), Z2(h0)), (X2(sx), Z2(h1))], layer='ф16_арм', lw=40)
    note('3(%%C16)', 'ш.200', (X2(w['s1']) + 1600, Z2(h1 - 200) + 500), (X2(w['s1']) - 30, Z2(h1 - 200)))
    note('Ск2(%%C16)', 'ш.200', (X2(w['s1']) + 1600, Z2(1200)), (X2(w['s1'] - 30), Z2(700)))
    note('Шп1', 'ш.400х400', (X2(w['s1']) + 1600, Z2(-1500)), (X2(w['s1']) - 300, Z2(-1900)))
    chain_v([Z2(ZF), Z2(h0), Z2(h1), Z2(ZW)], X2(w['s0']), X2(w['s0']) - 350, texts=['50', '200х%d=%d' % (nr, nr * 200), '50'])
    for name, s_ in w['axes']:
        axis(name, (X2(s_), Z2(ZF - 900)), (X2(s_), Z2(ZF - 2000)), 100, True)
    # ---- plan 1-1 (армирование), M1:100 strip
    PZ = Y0 + 7300
    rect(X2(w['s0']), PZ - 200, X2(w['s1']), PZ + 200, layer=L_THIN)
    for f in (-150, 150):
        pl([(X2(w['s0'] + 50), PZ + f), (X2(w['s1'] - 50), PZ + f)], layer='ф16_арм', lw=40)
    for sx, sg in ((w['s0'] + 50, 1), (w['s1'] - 50, -1)):
        pl([(X2(sx) + sg * 980, PZ - 120), (X2(sx), PZ - 120), (X2(sx), PZ + 120), (X2(sx) + sg * 980, PZ + 120)], layer='ф16_арм', lw=40)
    s.text(title_u('Разрез 1 - 1 (Армирование) М1:100'), ttl_x, PZ + 900, 300, att=8, layer='0')
    s.notes(['Общие указания см. лист 1.1. Данный лист читать совместно с листами %s.' % w['rng'],
             'Стыки рабочей арматуры внахлестку без сварки, на скрутках из вязальной проволоки не менее 3 шт. на стык. Длина нахлеста 61d (Ø20 - 1220, Ø16 - 980). Стыки располагать вразбежку (0,3L).',
             'Выпуски из фундамента (поз. 1;2;3 Ø20) см. листы 3.9, 3.10; вертикальная арматура стены стыкуется с ними внахлестку.',
             'Расход арматуры в погонных метрах приведен с учетом нахлеста.',
             'Стержни, указанные в "Ведомости деталей", гнуть механическим способом в холодном состоянии с радиусом гиба 3d - 5d.'],
            x=X0 + 2600, y=Y0 + 962, w=20000)
    return s


def calc(w):
    L = w['s1'] - w['s0']
    nv = int(round((L - 100) / 200.0)) + 1                 # per face
    nA, nB = 2 * ((nv + 1) // 2), 2 * (nv // 2)
    nr = int(round((ZW - 50 - (ZF + 50)) / 200.0)) + 1        # rows per face
    Lh = L - 100
    laps = max(0, math.ceil(Lh / 11700.0) - 1)
    pm = round(2 * nr * (Lh + laps * LAP16) / 1000.0, 1)
    nsk2 = 2 * nr
    nsh = int(math.ceil(L * (ZW - ZF) / 160000.0))
    rows = [rowL('Шп1*', 8, 520, nsh, 'A240'), rowL('Ск1*', 20, 2 * LAP20 + 300, nv), rowL('Ск2*', 16, 2 * LAP16 + 300, nsk2),
            rowL('1', 20, ZW - 50 - ZF, nA), rowL('2', 20, ZW - 50 - ZF - 1590, nB), rowPM('3', 16, pm)]
    conc = round(L * 400 * (ZW - ZF) / 1e9, 2)
    return rows, conc


def sheet_spec(num, mk, w, X0, Y0):
    s = Sheet(num, 'Спецификация элементов\\Pстены %s' % mk, None, X0, Y0, 'A3')
    rows, conc = calc(w)
    tot, hh = spec_table(X0 + 2500, Y0 + 28700, 100, 'Спецификация элементов стены %s (на 1 стену; всего %d шт.)' % (mk, w['cnt']), rows)
    s.text('Класс бетона C30/37 W8 F200 на 1 стену - %.2f м³; всего на %d шт. - %.2f м³.' % (conc, w['cnt'], conc * w['cnt']), X0 + 2500, Y0 + 28700 - hh - 300, 250, att=1)
    s.text('Позиции со "*" см. "Ведомость деталей" на данном листе.', X0 + 2500, Y0 + 28700 - hh - 700, 250, att=1)
    # ведомость деталей (простая таблица + эскизы)
    VX, VY = X0 + 23500, Y0 + 28000
    det = [('Шп1', [(0, 0), (320, 0)], 'L=520', '320'), ('Ск1', [(1220, 120), (0, 120), (0, -120), (1220, -120)], 'L=%d' % (2 * LAP20 + 300), '1220 / 300'),
           ('Ск2', [(980, 120), (0, 120), (0, -120), (980, -120)], 'L=%d' % (2 * LAP16 + 300), '980 / 300')]
    s.text(title_u('Ведомость деталей'), VX + 4000, VY + 150, 300, att=8, layer='0')
    rect(VX, VY - 1000 * len(det) - 700, VX + 8000, VY)
    pl([(VX, VY - 700), (VX + 8000, VY - 700)]); pl([(VX + 1500, VY), (VX + 1500, VY - 1000 * len(det) - 700)])
    s.text('Поз.', VX + 750, VY - 350, 250, att=5); s.text('Эскиз', VX + 4750, VY - 350, 250, att=5)
    for i, (p, pts, Ltxt, dtxt) in enumerate(det):
        y = VY - 700 - 1000 * (i + 1)
        pl([(VX, y), (VX + 8000, y)])
        s.text(p, VX + 750, y + 500, 250, att=5)
        sx = 0.002 * 1000 if False else 1.0
        k = 2000.0 / max(abs(q[0]) for q in pts)
        bx, by = VX + 2700, y + 500
        pl([(bx + q[0] * k, by + q[1] * 2.2) for q in pts], layer='ф16_арм', lw=40)
        a_, b_ = (dtxt.split(' / ') + [''])[:2]
        s.text(a_, bx + 1000, by + 230, 200, att=8)
        if b_: s.text(b_, bx - 120, by, 200, att=6, rot=90)
        s.text(Ltxt, VX + 7800, y + 120, 200, att=9)
    # steel summary
    a240 = sum(r[5] for r in rows if 'A240' in r[2]); m20 = sum(r[5] for r in rows if '%%C20' in r[2] or 'C20 ' in r[2])
    m16 = sum(r[5] for r in rows if 'C16' in r[2]); m8 = a240
    s.text('Ведомость расхода стали на 1 стену, кг: А240 Ø8 - %.2f; А500С Ø16 - %.2f, Ø20 - %.2f; всего - %.2f (на %d шт. - %.2f).' % (m8, m16, m20, tot, w['cnt'], tot * w['cnt']),
           X0 + 2500, Y0 + 28700 - hh - 1100, 250, att=1)
    s.notes(['Общие указания см. лист 1.1. Данный лист читать совместно с листами %s.' % w['rng'],
             'Выпуски из фундамента для стены (поз. 1;2;3) учтены в спецификации листа 3.10.'], x=X0 + 2500, y=Y0 + 962, w=18000)
    return s, tot, conc


if __name__ == '__main__':
    mk = sys.argv[1]; X0 = float(sys.argv[2]); n0 = int(sys.argv[3])
    w = WALLS[mk]
    nums = ['5.%d' % (n0 + i) for i in range(3)]
    w['rng'] = '%s ... %s' % (nums[0], nums[2])
    Y0 = 450000
    op(t='eraseregion', win=[X0 - 10, Y0 - 10, X0 + 59400 * 2 + 42000 + 10, Y0 + 42010])
    sheet_opal(nums[0], mk, w, X0, Y0)
    sheet_arm(nums[1], mk, w, X0 + 59400, Y0, None)
    s, tot, conc = sheet_spec(nums[2], mk, w, X0 + 118800, Y0)
    op(t='save')
    print(ab.run(lib.OPS, 'wall_' + mk, 2400)[-300:])
    print('tot', round(tot, 1), 'conc', conc)
