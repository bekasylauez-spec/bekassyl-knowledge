# -*- coding: utf-8 -*-
"""6.1 Ригели Рм-1...Рм-9, рандбалки Рб-1 (1:25, A1). Правило 04_Ригели: b>300 - 4+4 стержня и 2 хомута (каждый на 3 стержня)."""
import math
from common import *

SC = 25
# section types: key, b, h, slab t, n bottom/top, d, side bars per side, d side, stirrup d, marks
TYPES = [('1-1', 350, 700, 200, 4, 25, 2, 12, 10, ['Рм-1', 'Рм-2']),
         ('2-2', 300, 650, 200, 3, 22, 1, 12, 10, ['Рм-3', 'Рм-4', 'Рм-5']),
         ('3-3', 350, 500, 150, 4, 20, 1, 12, 10, ['Рм-6', 'Рм-7', 'Рм-8', 'Рм-9']),
         ('4-4', 300, 600, 0, 3, 20, 2, 12, 8, ['Рб-1'])]
RB_SEGS = RB1


def seg_len(s):
    return (s[3] - s[2]) / 1000.0


def stirrups(X, Y, b, h, c, ds, xs, cv):
    """b>300: two closed stirrups, each around 3 bars (xs[0..2], xs[1..3]); else one"""
    if len(xs) >= 4:
        for xa, xb in ((xs[0], xs[2]), (xs[1], xs[3])):
            rect(X(xa - cv + c + ds / 2), Y(c + ds / 2), X(xb + cv - c - ds / 2), Y(h - c - ds / 2), layer=LRB[ds], lw=40)
    else:
        rect(X(c + ds / 2), Y(c + ds / 2), X(b - c - ds / 2), Y(h - c - ds / 2), layer=LRB[ds], lw=40)


def xsec(OX, OY, T):
    key, b, h, ts, n, d, ns, dsd, ds, marks = T
    X = lambda x: OX + x; Y = lambda y: OY + y
    if ts:
        pl([(X(-600), Y(h - ts)), (X(0), Y(h - ts)), (X(0), Y(0)), (X(b), Y(0)), (X(b), Y(h - ts)), (X(b + 600), Y(h - ts))])
        pl([(X(-600), Y(h)), (X(b + 600), Y(h))])
        for x in (-600, b + 600): pl([(X(x), Y(h - ts - 40)), (X(x), Y(h + 40))], layer=L_THIN)
        g = box(-600, h - ts, b + 600, h).union(box(0, 0, b, h))
    else:
        rect(X(0), Y(0), X(b), Y(h)); g = box(0, 0, b, h)
    hatch_geom(g, OX, OY)
    c = 30; cv = c + ds + d / 2
    xs = [cv + (b - 2 * cv) * k / (n - 1) for k in range(n)]
    stirrups(X, Y, b, h, c, ds, xs, cv)
    rdots([(X(x), Y(cv)) for x in xs], d); rdots([(X(x), Y(h - cv)) for x in xs], d)
    zs = [cv + (h - 2 * cv) * k / (ns + 1) for k in range(1, ns + 1)]
    rdots([(X(cv), Y(z)) for z in zs] + [(X(b - cv), Y(z)) for z in zs], dsd)
    for z in zs: pl([(X(c), Y(z)), (X(b - c), Y(z))], layer=LRB[ds], lw=40)
    chain_h([X(0), X(b)], Y(0), Y(-350), SC)
    chain_v([Y(0), Y(h)], X(b + (600 if ts else 0)), X(b + (950 if ts else 350)), SC)
    note('1', '%d%%%%C%d' % (n, d), (X(b + 250), Y(-300)), (X(xs[-1]), Y(cv)), SC)
    note('2', '%d%%%%C%d' % (n, d), (X(b + 250 + (600 if ts else 0)), Y(h + 300)), (X(xs[-1]), Y(h - cv)), SC)
    note('3', '%d%%%%C%d' % (2 * ns, dsd), (X(-750), Y(zs[0] + 250)), (X(cv), Y(zs[0])), SC)
    note('4', 'ш.100/200', (X(-750), Y(-300)), (X(c + ds / 2), Y(c + 60)), SC)
    op(t='mtext', at=[X(b / 2), Y(h + 650)], h=87.5, att=8, s='{\\L%s (%s)}' % (key, ', '.join(marks)), style='Isocpeur', layer='0')


def long_rm1(OX, OY):
    X = lambda x: OX + x; Y = lambda y: OY + y
    h, L = 700, 6000
    rect(X(-250), Y(-600), X(250), Y(h), layer=L_THIN); rect(X(L - 250), Y(-600), X(L + 250), Y(h), layer=L_THIN)
    pl([(X(250), Y(0)), (X(L - 250), Y(0))]); pl([(X(-900), Y(h)), (X(L + 900), Y(h))])
    pl([(X(-900), Y(h - 200)), (X(-250), Y(h - 200))]); pl([(X(L + 250), Y(h - 200)), (X(L + 900), Y(h - 200))])
    cv = 30 + 10 + 12.5
    rbar([(X(-900), Y(cv)), (X(L + 900), Y(cv))], 25); rbar([(X(-900), Y(h - cv)), (X(L + 900), Y(h - cv))], 25)
    xs = [300 + 100 * k for k in range(15)] + [1700 + 200 * k for k in range(1, 13)] + [L - 300 - 100 * k for k in range(15)]
    for x in xs: pl([(X(x), Y(30)), (X(x), Y(h - 30))], layer=LRB[10], lw=40)
    chain_h([X(x) for x in (250, 300, 1700, L - 1700, L - 300, L - 250)], Y(-600), Y(-950), SC,
            texts=['50', '100х14=1400', '200х13=2600', '100х14=1400', '50'])
    chain_h([X(0), X(L)], Y(-600), Y(-1350), SC)
    axis('4', (X(0), Y(h + 700)), (X(0), Y(-2100)), SC, True); axis('5', (X(L), Y(h + 700)), (X(L), Y(-2100)), SC, True)
    note('1', '', (X(2100), Y(-350)), (X(1900), Y(cv)), SC); note('2', '', (X(2100), Y(h + 300)), (X(1900), Y(h - cv)), SC)
    note('4', 'ш.100', (X(900), Y(h + 300)), (X(700), Y(h - 30)), SC)
    op(t='mtext', at=[X(L / 2), Y(h + 950)], h=87.5, att=8, s='{\\LРм-1. Фрагмент пролета 4-5 (Рм-2...Рм-9 - аналогично)}', style='Isocpeur', layer='0')


def rows_for(T, Lm, cnt):
    key, b, h, ts, n, d, ns, dsd, ds, marks = T
    lb = Lm * 1.08 + cnt * 2 * 0.6
    nst = int(Lm / 0.2 * 1.3) + 2 * cnt
    nh = 2 if n >= 4 else 1
    if nh == 2:
        cv = 30 + ds + d / 2; wst = (b - 2 * cv) * 2 / 3 + 2 * cv - 60
        Lst = int(2 * wst + 2 * (h - 60) + 200)
    else:
        Lst = int(2 * (b - 60) + 2 * (h - 60) + 200)
    return [rowPM('1', d, round(n * lb, 1)), rowPM('2', d, round(n * lb, 1)), rowPM('3', dsd, round(2 * ns * lb, 1)),
            rowL('4', ds, Lst, nst * nh, 'A240'), rowL('5', ds, int(b - 60 + 150), nst * ns, 'A240')]


def build(X0, Y0):
    s = Sheet('6.1', 'Ригели Рм-1 ... Рм-9,\\Pрандбалки Рб-1', None, X0, Y0, 'A1', SC)
    long_rm1(X0 + 2200, Y0 + 10500)
    for i, T in enumerate(TYPES):
        xsec(X0 + 1500 + i * 2500, Y0 + 4700, T)
    segs = {mk: sg for mk, bw, bh, sg in RIGS}; segs['Рб-1'] = RB_SEGS
    ty = [Y0 + 14850 - 500, Y0 + 14850 - 500]; colx = [X0 + 21025 - 125 - 4625, X0 + 21025 - 125 - 4625 - 250 - 4625]
    tot_all = 0; k = 0
    for T in TYPES:
        for mk in T[9]:
            sg = segs[mk]; Lm = sum(seg_len(x) for x in sg)
            col = 0 if k < 5 else 1
            tot, hh = spec_table(colx[col], ty[col], SC, 'Спецификация арматуры %s (%d шт., %.1f п.м)' % (mk, len(sg), Lm), rows_for(T, Lm, len(sg)))
            ty[col] -= hh + 200; tot_all += tot; k += 1
    s.notes(['Общие указания см. лист 1.1. Схемы расположения см. листы 2.1, 2.2. Ригель от края до края - один элемент.',
             'Ригели Рм-1...Рм-5 бетонировать совместно с плитой Пм-1, Рм-6...Рм-9 - с плитой Пм-2.',
             'Продольная арматура поз. 1, 2 непрерывная через опоры, стыки 61d вразбежку: нижние - над опорами, верхние - в середине пролета; на крайних опорах анкеровка отгибом 500 мм.',
             'При b>300 - два хомута поз. 4, каждый охватывает 3 стержня (средние - общие). Шаг 100 на длине 1500 у опор, 200 - в пролете. Защитный слой 30 мм.',
             'Общая масса арматуры ригелей и рандбалок %.1f кг.' % tot_all], x=X0 + 21025 - 125 - 4625, y=Y0 + 125 + 1375 + 115, w=4625)
    return s
