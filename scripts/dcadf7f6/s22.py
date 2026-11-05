# -*- coding: utf-8 -*-
"""2.2 Схема расположения элементов на отм. +3.500, +4.950"""
from common import *

HID = dict(ltype='HIDDEN2', ltscale=30)

def build(X0, Y0):
    s = Sheet('2.2', 'Схема расположения элементов\\Pна отм. +3.500, +4.950', 'Схема расположения элементов на отм. +3.500, +4.950', X0, Y0, 'A1')
    PX, PY = X0 + 9500, Y0 + 15000
    ch = lambda xs, ye, yd: chain_h([PX + x for x in xs], PY + ye, PY + yd)
    cv = lambda ys, xe, xd: chain_v([PY + y for y in ys], PX + xe, PX + xd)
    # slabs
    rect(PX + PM1[0], PY + PM1[1], PX + PM1[2], PY + PM1[3])
    for r in PM2: rect(PX + r[0], PY + r[1], PX + r[2], PY + r[3])
    # walls / columns under slab (hidden)
    pil = [col_sq(c) for c in COLS_PIL]
    W = walls_geom()
    outline(unary_union(W + pil), PX, PY, layer=L_THIN, **HID)
    for c in COLS_IN + COLS_PAV: outline(col_sq(c), PX, PY, layer=L_THIN, **HID)
    for c in COLS_TOP: outline(col_sq(c, 400), PX, PY, layer=L_THIN, **HID)
    # beams under Пм-1 (hidden), clipped by walls
    wall_u = unary_union(W + pil + [col_sq(c) for c in COLS_IN])
    b1 = unary_union([box(*bar_rect(b, 350)) for b in BM1])
    b2 = unary_union([box(*bar_rect(b, 300)) for b in BM2]).difference(b1)
    outline(b1.difference(wall_u), PX, PY, layer=L_THIN, **HID)
    outline(b2.difference(wall_u), PX, PY, layer=L_THIN, **HID)
    # Рм-1 350x500 between pavilion columns (+4.950): hidden under Пм-2, visible in the opening
    rm = unary_union([box(*bar_rect(b, 350)) for b in RM1]).difference(unary_union([col_sq(c) for c in COLS_PAV] + [col_sq(c, 400) for c in COLS_TOP]))
    slabs = unary_union([box(*r) for r in PM2])
    outline(rm.intersection(slabs), PX, PY, layer=L_THIN, **HID)
    outline(rm.difference(slabs), PX, PY)
    axes(PX, PY, AX, AY, -4600, 46200, -4600, 26600)
    xs = sorted(AX.values()); ys = sorted(AY.values())
    ch([-250, 0, 6600, 6800] + xs[2:] + [44400], -1100, -2000)
    ch(xs, -1100, -2800)
    ch([0, 44200], -1100, -3600)
    cv([-250, 0, 5890, 13810, 19170, 24700, 24950], -1100, -2000)
    cv(ys, -1100, -2800)
    cv([0, 24700], -1100, -3600)
    ch([6800, 8700, 11000, 13350, 16350, 19350, 22350, 25350, 28350, 31350, 34600, 37800, 41000, 44200], 24900, 26300)
    cv([0, 4600, 10950, 13750, 20100, 24700], 44400, 46600)
    cv([6065, 13635], 1200, 1200)
    N = lambda l1, t, d=(400, 400), l2='': note(l1, l2, (PX + t[0] + d[0], PY + t[1] + d[1]), (PX + t[0], PY + t[1]))
    N('Пм-1', (23500, 21500)); N('Пм-2', (3400, 2600)); N('Пм-2', (3400, 21000))
    for mk, bw, bh, segs in RIGS:
        for o, c, a0, e0 in segs:
            if o == 'Y':
                xm = (a0 + e0) / 2 if mk != 'Рм-1' else 10000
                N(mk, (xm, c + bw / 2) if c < 24000 else (xm, c - bw / 2), (400, 400) if c < 24000 else (400, -400))
            else:
                ym = (a0 + e0) / 2 if (e0 - a0) < 12000 else (9500 if mk == 'Рм-2' else 15500)
                if mk == 'Рм-9': ym = 9800
                N(mk, (c + bw / 2, ym))
    for (x, y) in COLS_TOP:
        N('Км-4', (x + 200, y - 200) if y in (13810, 24700) else (x + 200, y + 200), (400, -400) if y in (13810, 24700) else (400, 400))
    plev('+3,500', (PX + 26800, PY + 9300))
    plev('+4,950', (PX + 3400, PY + 4200))
    plev('+4,950', (PX + 3400, PY + 17000))
    section('1', (PX - 5600, PY + 16000), (PX + 48200, PY + 16000))
    section('2', (PX + 22000, PY + 28600), (PX + 22000, PY - 5600))
    tb = tag('tb')
    op(t='clone', h=A_TABLE, base=[10700, 356330], to=[X0 + 65100, Y0 + 56000], tag=tb)
    rows = [(0, 0, '{\\C256;Спецификация элементов на отм. +3.500, +4.950}'),
            (2, 2, 'Плиты перекрытия:'), (3, 0, 'Пм-1'), (3, 1, 'лист 7.1'), (3, 2, 'Плита покрытия Пм-1 (t=200)'), (3, 10, '1'),
            (4, 0, 'Пм-2'), (4, 1, 'лист 7.2'), (4, 2, 'Плита покрытия Пм-2 (t=150)'), (4, 10, '2'),
            (5, 2, 'Ригели:')]
    r = 6
    for mk, bw, bh, segs in RIGS:
        rows += [(r, 0, mk), (r, 1, 'лист 6.1'), (r, 2, 'Ригель %s %dх%d(h)' % (mk, bw, bh)), (r, 10, str(len(segs)))]; r += 1
    rows += [(r, 0, ''), (r, 1, ''), (r, 2, 'Колонны:'), (r, 10, '')]; r += 1
    rows += [(r, 0, 'Км-4'), (r, 1, 'лист 4.1'), (r, 2, 'Колонна Км-4 400х400'), (r, 10, '5')]
    op(t='trows', h=tb, mode='ins', at=11, **{'from': 10}, n=5)
    op(t='tset', h=tb, cells=[[r, c, v] for r, c, v in rows])
    s.notes(['Общие указания см. лист 1.1.', 'Данный лист читать совместно с листами 2.1, 2.3.',
             'Ригели Рм-1...Рм-5 и плиту Пм-1, ригели Рм-6...Рм-9 и плиту Пм-2 бетонировать совместно; высота ригелей дана с учетом толщины плиты.',
             'Балки, стены и колонны под плитой показаны условно штриховой линией.'], x=X0 + 65100, y=Y0 + 6462)
    return s
