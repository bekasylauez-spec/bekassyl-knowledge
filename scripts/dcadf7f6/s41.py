# -*- coding: utf-8 -*-
"""4.1 Колонны Км-1 ... Км-4 (1:25, A1)"""
from common import *

SC = 25
# mark, b, z0, z1, n bars, d, stirrup d, count, bar length, name
COLS = [('Км-1', 500, -4000, 2800, 12, 25, 10, 8, 8300, 'от низа Фм-1 (лапка 300) до верха балок'),
        ('Км-2', 500, -4000, 3300, 12, 25, 10, 5, 8700, 'пилястра в стене, от низа Фм-1 до верха Пм-1'),
        ('Км-3', 500, -1200, 4800, 12, 25, 10, 5, 7550, 'от низа Фм-2 (лапка 300) до верха Пм-2'),
        ('Км-4', 400, 3500, 4800, 8, 20, 8, 5, 3050, 'с анкеровкой 1200 в стене/пилястре')]


def zones(H):
    mid = int((H - 2100) // 200) * 200
    e = (H - 2000 - mid) / 2.0
    return e, mid


def facade(OX, OZ, c):
    mk, b, z0, z1, n, d, ds, cnt, L, _ = c
    H = z1 - z0
    X = lambda x: OX + x; Z = lambda z: OZ + z
    rect(X(0), Z(z0), X(b), Z(z1))
    cv = 40 + ds + d / 2
    for x in (cv, b - cv): rbar([(X(x), Z(z0 - 300)), (X(x), Z(z1 - 50))], d)
    e, mid = zones(H)
    zs = []
    z = z0 + e
    for i in range(11): zs.append(z + 100 * i)
    z = z0 + e + 1000
    for i in range(1, int(mid / 200) + 1): zs.append(z + 200 * i)
    z = z0 + e + 1000 + mid
    for i in range(1, 11): zs.append(z + 100 * i)
    for z in zs: pl([(X(40), Z(z)), (X(b - 40), Z(z))], layer=LRB[ds], lw=40)
    pts = [z0, z0 + e, z0 + e + 1000, z0 + e + 1000 + mid, z0 + e + 2000 + mid, z1]
    tx = ['%d' % e, '100х10=1000', '200х%d=%d' % (mid / 200, mid), '100х10=1000', '%d' % e]
    chain_v([Z(z) for z in pts], X(b), X(b + 450), SC, texts=tx)
    dim((X(0), Z(z0)), (X(b), Z(z0)), (X(0), Z(z0 - 450)), 0, SC)
    lev(OZ, (X(-200), Z(z0)), SC); lev(OZ, (X(-200), Z(z1)), SC)
    zc = z0 + e + 1000 + mid / 2
    section('%s' % mk[-1], (X(-350), Z(zc)), (X(b + 1000), Z(zc)), SC)
    note('1', '', (X(cv + 150), Z(zc + 900)), (X(cv), Z(zc + 750)), SC)
    note('2', 'ш.100/200', (X(b / 2 + 150), Z(z0 + e + 650)), (X(b / 2), Z(z0 + e + 500)), SC)
    s_ = '{\\L%s}' % mk
    op(t='mtext', at=[X(b / 2), Z(z1 + 350)], h=87.5, att=8, s=s_, style='Isocpeur', layer='0')
    return zs


def xsec(OX, OY, c):
    mk, b, z0, z1, n, d, ds, cnt, L, _ = c
    X = lambda x: OX + x; Y = lambda y: OY + y
    rect(X(0), Y(0), X(b), Y(b))
    hatch_geom(box(0, 0, b, b), OX, OY)
    cv = 40 + ds + d / 2
    rect(X(40 + ds / 2), Y(40 + ds / 2), X(b - 40 - ds / 2), Y(b - 40 - ds / 2), layer=LRB[ds], lw=40)
    per = n // 4 + 1
    ps = set()
    for i in range(per):
        t = cv + (b - 2 * cv) * i / (per - 1)
        for p in ((t, cv), (t, b - cv), (cv, t), (b - cv, t)): ps.add((round(p[0], 1), round(p[1], 1)))
    rdots([(X(x), Y(y)) for x, y in ps], d)
    if per > 2:
        for i in range(1, per - 1):
            t = cv + (b - 2 * cv) * i / (per - 1)
            pl([(X(40), Y(t)), (X(b - 40), Y(t))], layer=LRB[ds], lw=40)
            pl([(X(t), Y(40)), (X(t), Y(b - 40))], layer=LRB[ds], lw=40)
    chain_h([X(0), X(b)], Y(0), Y(-350), SC); chain_v([Y(0), Y(b)], X(b), X(b + 350), SC)
    note('1', '%d%%%%C%d' % (n, d), (X(b + 150), Y(b + 300)), (X(b - cv), Y(b - cv)), SC)
    note('2', '', (X(-450), Y(b + 300)), (X(40 + ds / 2), Y(b - 120)), SC)
    if per > 2: note('3', '', (X(-450), Y(-300)), (X(40), Y(cv + (b - 2 * cv) / (per - 1))), SC)
    op(t='mtext', at=[X(b / 2), Y(b + 600)], h=87.5, att=8, s='{\\L%s-%s}' % (mk[-1], mk[-1]), style='Isocpeur', layer='0')


def build(X0, Y0):
    s = Sheet('4.1', 'Колонны Км-1 ... Км-4', None, X0, Y0, 'A1', SC)
    OZ = Y0 + 4000 + 4000 + 600       # level 0.000 at this Y (top of Км-3 4800 -> Y0+13400)
    xs = [X0 + 1800, X0 + 4700, X0 + 7600, X0 + 10500]
    tb_y = Y0 + 14850 - 500; tot_all = 0
    for i, c in enumerate(COLS):
        zs = facade(xs[i], OZ, c)
        mk, b, z0, z1, n, d, ds, cnt, L, nm = c
        xsec(xs[i] + (0 if i < 3 else 0), Y0 + 1400 if i < 3 else OZ + 1700, c) if False else None
    # cross sections in one row at bottom-left region below Км-4 facade area
    for i, c in enumerate(COLS):
        xsec(X0 + 12700 + (i % 2) * 1700, Y0 + 9800 - (i // 2) * 1800, c)
    for i, c in enumerate(COLS):
        mk, b, z0, z1, n, d, ds, cnt, L, nm = c
        H = z1 - z0; e, mid = zones(H); nst = 21 + int(mid / 200)
        sd = b - 80 + 0; Lst = int(4 * (b - 80) + 200); per = n // 4 + 1
        rows = [rowL('1', d, L, n), rowL('2', ds, Lst, nst, 'A240')]
        if per > 2: rows.append(rowL('3', ds, int(b - 80 + 150), 2 * (per - 2) * nst, 'A240'))
        tot, hgt = spec_table(X0 + 21025 - 125 - 4625, tb_y, SC, 'Спецификация на 1 колонну %s (%d шт.)' % (mk, cnt), rows)
        tb_y -= hgt + 250; tot_all += tot * cnt
    s.notes(['Общие указания см. лист 1.1. Схемы расположения колонн см. листы 2.1, 2.2.',
             'Бетон колонн C30/37 (Км-1, Км-2), C25/30 (Км-3, Км-4); защитный слой до хомутов 40 мм.',
             'Продольная арматура A500C по ГОСТ 34028-2016, хомуты и шпильки A240.',
             'Стыки продольной арматуры - внахлестку 61d вразбежку, не более 50% в одном сечении; в зонах шага 100 стыки не допускаются.',
             'Хомуты с крюками 135 градусов, длина отгиба 10d.', 'Общая масса арматуры колонн %.1f кг.' % tot_all],
            x=X0 + 21025 - 125 - 4625, y=Y0 + 125 + 1375 + 115, w=4625)
    return s
