# -*- coding: utf-8 -*-
"""3.5 Разрезы 1-1, 2-2 фундамента Фм-1 (1:25) + спецификация арматуры Фм-1"""
import math
from common import *
import s3x

KG = {8: 0.395, 10: 0.617, 12: 0.888, 14: 1.208, 16: 1.578, 18: 1.998, 20: 2.466, 22: 2.984, 25: 3.853, 28: 4.834}
SC = 25
LR = {20: 'ф20_арм', 16: 'ф16_арм', 12: 'ф12_арм', 10: 'ф10_арм', 8: 'ф8_арм'}


def rbar(pts, d=20):
    pl(pts, layer=LR[d], lw=40)


def dots(xs, z, d=20):
    for x in xs: op(t='circle', c=[x, z], r=d / 2.0 + 2, layer=LR[d], lw=40)


def brk_v(x, z0, z1):
    """zigzag break line (vertical)"""
    zm = (z0 + z1) / 2
    pl([(x, z0 - 60), (x, zm - 60), (x - 40, zm - 20), (x + 40, zm + 20), (x, zm + 60), (x, z1 + 60)], layer=L_THIN)


def brk_h(z, x0, x1):
    xm = (x0 + x1) / 2
    pl([(x0 - 60, z), (xm - 60, z), (xm - 20, z + 40), (xm + 20, z - 40), (xm + 60, z), (x1 + 60, z)], layer=L_THIN)


def N25(l1, l2, t, d=(150, 150)):
    note(l1, l2, (t[0] + d[0], t[1] + d[1]), t, SC)


def sec_edge(OX, OZ):
    """1-1: slab edge at outer wall (axis 2), x local = plan x, z = level"""
    X = lambda x: OX + x; Z = lambda z: OZ + z
    xe = 5900; xw0, xw1 = 6600, 7000; xr = 8600
    # concrete
    g = box(xe, -4700, xr, -4000).union(box(xw0, -4000, xw1, -2900))
    p = [(X(x), Z(z)) for x, z in list(g.exterior.coords)[:-1]]
    pl([(X(xr), Z(-4700)), (X(xe), Z(-4700)), (X(xe), Z(-4000)), (X(xw0), Z(-4000)), (X(xw0), Z(-2900))])
    pl([(X(xw1), Z(-2900)), (X(xw1), Z(-4000)), (X(xr), Z(-4000))])
    brk_v(X(xr), Z(-4700), Z(-4000)); brk_h(Z(-2900), X(xw0), X(xw1))
    rect(X(xe - 100), Z(-4800), X(xr), Z(-4700), layer=L_THIN)
    # meshes: X bars (lines), Y bars (dots)
    zb, zt = -4700 + 50 + 10, -4000 - 40 - 10
    rbar([(X(xe + 50), Z(zb)), (X(xr), Z(zb))]); rbar([(X(xe + 50), Z(zt)), (X(xr), Z(zt))])
    xs = [X(xe + 50 + 100 + 200 * i) for i in range(int((xr - xe - 150) / 200) + 1)]
    dots(xs, Z(zb + 20)); dots(xs, Z(zt - 20))
    # доп 3 (bottom) / 6 (top) L=1900
    rbar([(X(xe + 50), Z(zb - 25)), (X(xe + 1950), Z(zb - 25))]); rbar([(X(xe + 50), Z(zt + 25)), (X(xe + 1950), Z(zt + 25))])
    # Ск1
    rbar([(X(xe + 1060), Z(zt - 45)), (X(xe + 60), Z(zt - 45)), (X(xe + 60), Z(zb + 45)), (X(xe + 1060), Z(zb + 45))], 16)
    # wall dowels Вп-1 (both faces) with 200 foot on bottom mesh
    for xv, sgn in ((xw0 + 50, -1), (xw1 - 50, 1)):
        rbar([(X(xv + sgn * 200), Z(zb + 45)), (X(xv), Z(zb + 45)), (X(xv), Z(-2900 + 40))])
    dim((X(xe), Z(-4800)), (X(xw0), Z(-4800)), (X(xe), Z(-5450)), 0, SC)
    dim((X(xw0), Z(-4800)), (X(xw1), Z(-4800)), (X(xw0), Z(-5450)), 0, SC)
    dim((X(xe), Z(-4700)), (X(xe), Z(-4000)), (X(xe - 400), Z(-4700)), math.pi / 2, SC)
    dim((X(xe), Z(-4800)), (X(xe), Z(-4700)), (X(xe - 400), Z(-4800)), math.pi / 2, SC)
    dim((X(xw1), Z(-4000)), (X(xw1), Z(-2780)), (X(xw1 + 450), Z(-4000)), math.pi / 2, SC, txt='1220')
    lev(Z(0), (X(xe - 1000), Z(-4000)), SC); lev(Z(0), (X(xe - 1000), Z(-4700)), SC)
    N25('1', 'ш.200', (X(8000), Z(zt)), (150, 250)); N25('1', 'ш.200', (X(8000), Z(zb)), (150, -300))
    N25('6', 'ш.200', (X(6300), Z(zt + 25)), (150, 400)); N25('3', 'ш.200', (X(6300), Z(zb - 25)), (150, -450))
    N25('Ск1', 'ш.200', (X(xe + 60), Z(-4350)), (-600, 150))
    N25('Вп-1', 'ш.200', (X(xw1 - 50), Z(-3300)), (250, 150))
    N25('Фм-1', '', (X(8100), Z(-4400)), (150, 150))
    N25('Подбетонка C8/10', 't=100', (X(7600), Z(-4800)), (150, -350))
    return X(xe - 1700), Z(-2600)


def sec_mid(OX, OZ):
    """2-2: slab under partition Y=12.35 (local x = plan y)"""
    X = lambda x: OX + x; Z = lambda z: OZ + z
    c = 12350; xl, xr = c - 1700, c + 1700
    pl([(X(xl), Z(-4700)), (X(xr), Z(-4700))])
    pl([(X(xl), Z(-4000)), (X(c - 200), Z(-4000)), (X(c - 200), Z(-2900))])
    pl([(X(c + 200), Z(-2900)), (X(c + 200), Z(-4000)), (X(xr), Z(-4000))])
    brk_v(X(xl), Z(-4700), Z(-4000)); brk_v(X(xr), Z(-4700), Z(-4000)); brk_h(Z(-2900), X(c - 200), X(c + 200))
    rect(X(xl), Z(-4800), X(xr), Z(-4700), layer=L_THIN)
    zb, zt = -4640, -4050
    rbar([(X(xl), Z(zb)), (X(xr), Z(zb))]); rbar([(X(xl), Z(zt)), (X(xr), Z(zt))])
    xs = [X(xl + 100 + 200 * i) for i in range(int((xr - xl - 100) / 200) + 1)]
    dots(xs, Z(zb + 20)); dots(xs, Z(zt - 20))
    rbar([(X(c - 1000), Z(zb - 25)), (X(c + 1000), Z(zb - 25))]); rbar([(X(c - 1000), Z(zt + 25)), (X(c + 1000), Z(zt + 25))])
    for xv, sgn in ((c - 150, -1), (c + 150, 1)):
        rbar([(X(xv + sgn * 200), Z(zb + 45)), (X(xv), Z(zb + 45)), (X(xv), Z(-2900 + 40))])
    chain_h([X(c - 1000), X(c - 200), X(c), X(c + 200), X(c + 1000)], Z(-4800), Z(-5450), SC)
    dim((X(xr), Z(-4700)), (X(xr), Z(-4000)), (X(xr + 400), Z(-4700)), math.pi / 2, SC)
    axis('В', (X(c), Z(-2700)), (X(c), Z(-5700)), SC, True)
    N25('4', 'ш.200', (X(c - 600), Z(zb - 25)), (-900, -450)); N25('7', 'ш.200', (X(c - 600), Z(zt + 25)), (-900, 400))
    N25('1', 'ш.200', (X(c + 1300), Z(zt)), (150, 250)); N25('Вп-1', 'ш.200', (X(c + 150), Z(-3300)), (250, 150))
    return X(xl), Z(-2600)


def spec_rows(nx, ny, Lx, Ly, cnt_b, cnt_t):
    lap = 1220
    def run(L):
        nl = max(0, math.ceil(L / 11700.0) - 1); return (L + nl * lap) / 1000.0
    pm1 = 2 * (nx * run(Lx) + ny * run(Ly))
    rows = [('1', '%%C20 A500C (п.м)', pm1, KG[20])]
    nsk = 2 * (nx + ny); rows.append(('Ск1', '%%C16 A500C, L=2620', nsk, round(2.62 * KG[16], 2)))
    for c in (cnt_b, cnt_t):
        for pos in sorted(c):
            L, n = c[pos]
            rows.append((str(pos), '%%C20 A500C, L=' + str(int(L)), n, round(L / 1000.0 * KG[20], 2)))
    nkr = int(1039 / 1.44) + 1
    rows.append(('КР-1', 'Каркас фиксирующий %%C16, L=2800', nkr, round(2.8 * KG[16], 2)))
    nvp = 2 * int((2 * 24700 + 2 * 37400 + 15500 + 29100 + 4 * 6400 + 2 * 3700 + 2 * 1900) / 200)
    rows.append(('Вп-1', 'Выпуск %%C20 A500C, L=2060', nvp, round(2.06 * KG[20], 2)))
    rows.append(('Вп-2', 'Выпуск колонн Км-2 %%C25 A500C, L=1550', 20, round(1.55 * 3.853, 2)))
    rows.append(('Вп-3', 'Выпуск колонн Км-2 %%C25 A500C, L=2150', 20, round(2.15 * 3.853, 2)))
    return rows


def build(X0, Y0):
    s = Sheet('3.5', 'Разрезы 1-1, 2-2 фундамента Фм-1.\\PСпецификация', None, X0, Y0, 'A2', SC)
    # sections
    t1 = sec_edge(X0 + 1500 - 5900 + 1700, Y0 + 8600)
    s.text(title_u('Разрез 1-1'), t1[0] + 1800, t1[1] + 250, 75, att=8, layer='0')
    t2 = sec_mid(X0 + 6200 - 12350 + 1700 + 200, Y0 + 8600)
    s.text(title_u('Разрез 2-2'), t2[0] + 1700, t2[1] + 250, 75, att=8, layer='0')
    _, nx, ny, Lx, Ly = (None, 133, 196, 39100, 26400)
    import importlib
    cnt_b = s3x.dop_counts(False); cnt_t = s3x.dop_counts(True)
    rows = spec_rows(nx, ny, Lx, Ly, cnt_b, cnt_t)
    tb = tag('tb')
    op(t='clone', h=A_TABLE, base=[10700, 356330], to=[X0 + 14850 - 125 - 4625, Y0 + 10500 - 400], s=0.25, tag=tb)
    need = 4 + len(rows)
    if need > 12: op(t='trows', h=tb, mode='ins', at=11, **{'from': 10}, n=need - 12)
    cells = [[0, 0, '{\\C256;Спецификация арматуры фундамента Фм-1}'], [1, 11, 'Масса ед. кг'], [1, 12, 'Масса всего, кг']]
    r = 2; tot = 0
    cells += [[r, 0, ''], [r, 1, ''], [r, 2, 'Детали:'], [r, 10, ''], [r, 11, ''], [r, 12, '']]; r += 1
    for pos, name, q, m in rows:
        if name.endswith('(п.м)'):
            mt = q * m; qs = '%.1f п.м' % q; ms = '%.3f' % m
        else:
            mt = q * m; qs = str(int(q)); ms = '%.2f' % m
        tot += mt
        cells += [[r, 0, pos], [r, 1, 'ГОСТ 34028-2016'], [r, 2, name], [r, 10, qs], [r, 11, ms], [r, 12, '%.1f' % mt]]; r += 1
    cells += [[r, 0, ''], [r, 1, ''], [r, 2, 'Итого, кг'], [r, 10, ''], [r, 11, ''], [r, 12, '%.1f' % tot]]
    op(t='tset', h=tb, cells=cells)
    op(t='ttext', h=tb, th=62.5, rh=158.25, rh1=375)
    s.notes(['Разрезы читать совместно с листами 3.1 - 3.4. Общие указания см. лист 1.1.',
             'Защитный слой бетона: низ - 50 мм, верх - 40 мм, торцы - 50 мм.',
             'Выпуски Вп-1 %%C20 ш.200 у обеих граней стен; длина выпуска над плитой 1220 мм (61d), анкеровка - лапкой 200 мм на нижнюю сетку.',
             'Рабочий шов плита/стена - с гидрошпонкой (ПВХ шпонка ширина 250 мм) по оси стены.'],
            x=X0 + 14850 - 125 - 4625, y=Y0 + 125 + 1375 + 115, w=4625)
    return s, tot
