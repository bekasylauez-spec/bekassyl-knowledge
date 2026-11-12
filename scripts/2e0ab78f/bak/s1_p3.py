# -*- coding: utf-8 -*-
"""3.2 осн. арматура Фм-1 (план, узел стыковки); 3.3 фрагменттер (арм.), Кр-1; 3.5 выпуски; 3.6 Фм-2; 4.1 Км-1."""
import math, sys
import s1_lib as L, s1_draw as D, s1_qty as Q
from s1_geo import *
from s1_p34 import NOTES

AN = r"D:\_claude_work\otst\src\analog.dwg"
AN07 = (195778.0, -1593693.0); AN08 = (255178.0, -1593693.0)
RE = R_OUT - 50


def off(pts, d):
    """полилинияны сол жаққа d-ге ығыстыру (қарапайым miter)"""
    out = []
    n = len(pts)
    for i in range(n):
        if i == 0: a, b = pts[0], pts[1]
        elif i == n - 1: a, b = pts[n - 2], pts[n - 1]
        else: a, b = pts[i - 1], pts[i + 1]
        dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy)
        nx, ny = -dy / l, dx / l
        if 0 < i < n - 1:
            d1 = (pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); d2 = (pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
            l1 = math.hypot(*d1); l2 = math.hypot(*d2)
            n1 = (-d1[1] / l1, d1[0] / l1); n2 = (-d2[1] / l2, d2[0] / l2)
            mx, my = n1[0] + n2[0], n1[1] + n2[1]; ml = math.hypot(mx, my); c = (n1[0] * mx + n1[1] * my) / ml
            out.append((pts[i][0] + mx / ml * d / c, pts[i][1] + my / ml * d / c))
        else: out.append((pts[i][0] + nx * d, pts[i][1] + ny * d))
    return out


def along(p, q, step, first=0.0):
    l = math.hypot(q[0] - p[0], q[1] - p[1]); n = int((l - first) // step) + 1
    return [(p[0] + (q[0] - p[0]) * (first + i * step) / l, p[1] + (q[1] - p[1]) * (first + i * step) / l) for i in range(n)]


def b32():
    sh = L.Sheet('3.2', 'Схема расположения основной арматуры фундамента Фм-1')
    C = sh.P(18500, 22500)
    L.title('Схема расположения основной арматуры фундамента Фм-1', C[0] + 2500, sh.Y0 + 40500)
    L.circle(C, R_OUT, layer=L.L_THIN); L.circle(C, R_PT, layer=L.L_THIN); L.circle(C, R_B2, layer=L.L_THIN, ltype='HIDDEN', ltscale=30)
    L.circle(C, R_COL_O, layer=L.L_THIN); L.circle(C, R_COL_I, layer=L.L_THIN); L.hatch([L.ring_pts(C, R_COL_O), L.ring_pts(C, R_COL_I)])
    D.axes(C)
    L.ddim(C, R_OUT, 140)
    def ch(y): return math.sqrt(RE * RE - y * y)
    for yy in (-6000, -6100):
        x = ch(yy); D.bar([(C[0] - x, C[1] + yy), (C[0] + x, C[1] + yy)])
    for xx in (5000, 5100):
        y = ch(xx); D.bar([(C[0] + xx, C[1] - y), (C[0] + xx, C[1] + y)])
    L.note('1', 'ш.100', (C[0] + 1800, C[1] - 5000), (C[0] + 2600, C[1] - 6000))
    L.note('1', 'ш.100', (C[0] + 6200, C[1] + 3600), (C[0] + 5100, C[1] + 2900))
    # жиек скобалары (поз.5) — хорда ұштарында
    x = ch(-6000)
    for sg in (1, -1):
        D.bar([(C[0] + sg * x, C[1] - 6240), (C[0] + sg * (x - 1100), C[1] - 6240)])
        L.note('5', 'ш.100', (C[0] + sg * (x + 700), C[1] - 7400), (C[0] + sg * (x - 500), C[1] - 6240))
    y = ch(5000)
    for sg in (1, -1):
        D.bar([(C[0] + 5240, C[1] + sg * y), (C[0] + 5240, C[1] + sg * (y - 1100))])
        L.note('5', 'ш.100', (C[0] + 6600, C[1] + sg * (y + 300)), (C[0] + 5240, C[1] + sg * (y - 500)))
    L.note('Армирование приямка', 'см. лист 3.3', (C[0] - 5200, C[1] + 3600), (C[0] - 1700, C[1] + 1100))
    L.note('Выпуски в стену См-1', 'см. лист 3.5', (C[0] - 9800, C[1] + 9600), (C[0] + 10175 * math.cos(math.radians(140)), C[1] + 10175 * math.sin(math.radians(140))))
    L.section(1, (C[0] - 11700, C[1]), (C[0] + 11700, C[1]))
    # узел стыковки — аналог л.8-ден клон
    bx, by = AN07[0] + 22500, AN07[1] + 1800
    tx, ty = sh.X0 + 38000, sh.Y0 + 20500
    L.op(t='import', file=AN, base=[bx, by], to=[tx, ty], wins=[[bx, by, bx + 16800, by + 8000]], pre='N32:')
    L.op(t='txtrep', win=[tx - 100, ty - 100, tx + 17000, ty + 8200], pairs=[['71d', '61d'], ['106.5d', '91.5d'], ['106,5d', '91,5d'], ['верхей', 'верхней']])
    L.op(t='eraseregion', win=[tx + 4600, ty + 800, tx + 5900, ty + 2000], mode='inside')
    L.title('Узел стыковки одиночных арматур внахлест (без сварки)', tx + 8000, ty + 9300)
    L.mtext('Стыки стержней поз. 1 - внахлестку 61d = 1100 мм, вразбежку,\\Pне более 50% стержней в одном сечении.', tx + 300, ty - 600, 250, att=1, w=16000)
    sh.notes(['Общие указания см. л. 1.1.', 'Данный лист читать совместно с л. 3.1, 3.3, 3.4.'] + NOTES[1:] +
             ['Основные сетки (поз. 1): верхняя и нижняя, стержни %%C18 А500С с шагом 100 в двух направлениях; в зоне приямка стержни прерываются и стыкуются с радиальными стержнями поз. 3.'.replace('%%C', 'Ø')])
    return sh


def edge_arm(F, k, rc, with_wall=True):
    """ернеу/вут армированиесі (фрагмент 1): F — (r,z)→парақ"""
    # төменгі тор
    bot = [(RE, Z_BOT + 50), (R_B1, Z_BOT + 50), (rc, z_bot(rc) + 50)]
    D.bar([F(*p) for p in bot])
    top = [(rc, z_top(rc) - 50), (R_HT, Z_HT - 50), (RE, Z_FL - 50)]
    D.bar([F(*p) for p in top])
    for r in [RE - 50 - 100 * i for i in range(int((RE - 50 - rc) // 100) + 1)]:
        zb = (Z_BOT + 50 if r >= R_B1 else z_bot(r) + 50) + 18; D.dot(F(r, zb), 9 * k)
        zt = (Z_FL - 50 - (R_OUT - 50 - r) * 42.0 / 1300 if r >= R_HT else z_top(r) - 50) - 18; D.dot(F(r, zt), 9 * k)
    # П-скоба 5
    D.bar([F(RE - 1100, Z_FL - 72), F(RE - 12, Z_FL - 72), F(RE - 12, Z_BOT + 72), F(RE - 1100, Z_BOT + 72)])
    # вут стержені 6 + сақиналар 7
    p1 = (9460.0, -1852.0); p2 = (9960.0, -1352.0)
    D.bar([F(p1[0] - 648, p1[1] - 54), F(*p1), F(*p2), F(p2[0], p2[1] + 650)])
    for t in (0.2, 0.5, 0.8): D.dot(F(p1[0] + 500 * t + 14, p1[1] + 500 * t - 14), 9 * k)
    if with_wall:
        xi, xo = R_WI + 49, R_WO - 49
        D.bar([F(xi, Z_JOINT + 330), F(xi, Z_BOT + 90), F(xo, Z_BOT + 90), F(xo, Z_JOINT + 330)])


def b33():
    sh = L.Sheet('3.3', 'Разрезы фундамента Фм-1 (армирование)')
    k = 4.0
    # ---------------- Фрагмент 1 ----------------
    f1x, f1y = sh.X0 + 20000 - 10000 * k, sh.Y0 + 29500 + 2300 * k
    def F(r, z): return (f1x + r * k, f1y + z * k)
    L.title('Фрагмент 1 (армирование)', sh.X0 + 18000, sh.Y0 + 40500)
    rc = 8600.0
    lp = [F(rc, z_top(rc)), F(R_HT, Z_HT), F(R_WI, Z_JOINT), F(R_WO, Z_JOINT), F(R_WO, Z_FL), F(R_OUT, Z_FL), F(R_OUT, Z_BOT), F(R_B1, Z_B1), F(rc, z_bot(rc))]
    L.pl(lp, layer=L.L_THIN); L.brk(F(rc, z_top(rc) + 60), F(rc, z_bot(rc) - 160))
    L.line(F(R_WI, Z_JOINT), F(R_WI, Z_JOINT + 330), layer=L.L_THIN); L.line(F(R_WO, Z_JOINT), F(R_WO, Z_JOINT + 330), layer=L.L_THIN)
    L.brk(F(R_WI - 40, Z_JOINT + 330), F(R_WO + 40, Z_JOINT + 330))
    edge_arm(F, k, rc)
    yd = f1y + Z_BOT * k - 900
    L.chain_h([F(v, 0)[0] for v in (R_HT, R_WI, R_WO, R_OUT)], f1y + Z_BOT * k - 200, yd, lfac=0.25)
    L.chain_h([F(v, 0)[0] for v in (RE - 1100, RE, R_OUT)], f1y + Z_BOT * k - 200, yd - 700, lfac=0.25)
    xv = F(R_OUT, 0)[0] + 900
    L.chain_v([F(0, v)[1] for v in (Z_BOT, Z_BOT + 50, Z_FL - 50, Z_FL)], F(R_OUT, 0)[0] + 150, xv, lfac=0.25)
    L.lev(Z_FL, F(R_OUT, Z_FL), 'R', ext=2600); L.lev(Z_BOT, F(R_OUT, Z_BOT), 'R', ext=2600); L.lev(Z_JOINT, F(R_WI, Z_JOINT), 'L', ext=1500)
    L.note('1', 'ш.100', F(8900, -1150), F(9000, z_top(9000) - 50)); L.note('1', 'ш.100', F(8850, -2900), F(9000, z_bot(9000) + 50))
    L.note('5', 'ш.100', F(11250, -1150), F(RE - 12, -1900)); L.note('6', 'ш.100', F(9300, -850), F(9700, -1612))
    L.note('7', '', F(9500, -500), F(9724, -1602)); L.note('Вп1', 'ш.100, см. л. 3.5', F(10800, -600), F(R_WO - 49, -1100))
    L.note('Кр-1', 'ш.1200х1200', F(9150, -3250), F(9300, -2050))
    # Кр-1 шартты (екі тік + горизонталь)
    for r in (9200.0, 9450.0):
        L.pl([F(r, z_bot(r) + 70), F(r, z_top(r) - 70)], layer='ф16_арм', lw=40)
    # ---------------- Фрагмент 2 ----------------
    f2x, f2y = sh.X0 + 43800, sh.Y0 + 22500 + 4625 * k
    def G(r, z): return (f2x + r * k, f2y + z * k)
    L.title('Фрагмент 2 (армирование)', f2x, sh.Y0 + 40500)
    rc = 3150.0
    lp = [G(-rc, z_top(rc)), G(-R_PT, Z_PT), G(-R_PB, Z_PB), G(R_PB, Z_PB), G(R_PT, Z_PT), G(rc, z_top(rc))]
    lb = [G(rc, z_bot(rc)), G(R_B2, Z_B2), G(R_B3, Z_B3), G(-R_B3, Z_B3), G(-R_B2, Z_B2), G(-rc, z_bot(rc))]
    L.pl(lp, layer=L.L_THIN); L.pl(lb, layer=L.L_THIN)
    for sg in (1, -1):
        L.brk(G(sg * rc, z_top(rc) + 60), G(sg * rc, z_bot(rc) - 160))
        L.line(G(sg * R_COL_O, Z_PB), G(sg * R_COL_O, Z_PB + 900), layer=L.L_THIN); L.line(G(sg * R_COL_I, Z_PB), G(sg * R_COL_I, Z_PB + 900), layer=L.L_THIN)
        # радиал 3: ішкі қабат
        inn = off([(R_PB - 430, Z_PB), (R_PB, Z_PB), (R_PT, Z_PT), (R_PT + 1100, z_top(R_PT + 1100))], -68 if True else 0)
        D.bar([G(sg * r, z) for r, z in inn])
        out = off([(R_B3 - 430, Z_B3), (R_B3, Z_B3), (R_B2, Z_B2), (R_B2 + 1100 if R_B2 + 1100 < rc else rc, z_bot(min(R_B2 + 1100, rc)))], 68)
        D.bar([G(sg * r, z) for r, z in out])
        # сақина 4 нүктелері
        for a, b, dd in (((R_PB, Z_PB), (R_PT, Z_PT), -86), ((R_B3, Z_B3), (R_B2, Z_B2), 86)):
            o = off([a, b], dd)
            for p in along(o[0], o[1], 100, 50): D.dot(G(sg * p[0], p[1]), 9 * k)
        # днище торлары (поз.1) жалғасы
        D.bar([G(sg * (R_PT + 150), z_top(R_PT + 150) - 50), G(sg * rc, z_top(rc) - 50)]); D.bar([G(sg * (R_B2 + 150), z_bot(R_B2 + 150) + 50), G(sg * rc, z_bot(rc) + 50)])
        # Км-1 выпуск
        for r, fo in ((651, 1), (449, -1)):
            D.bar([G(sg * (r + fo * 400), Z_B3 + 110), G(sg * r, Z_B3 + 110), G(sg * r, Z_PB + 900)])
    L.brk(G(-R_COL_O - 40, Z_PB + 900), G(R_COL_O + 40, Z_PB + 900))
    L.line(G(0, Z_B3 - 150), G(0, Z_PT + 250), **D.AX)
    # приямок түбі (поз.2)
    D.bar([G(-1541, Z_B3 + 50), G(1541, Z_B3 + 50)]); D.bar([G(-1541, Z_PB - 50), G(1541, Z_PB - 50)])
    for i in range(31):
        r = -1500 + 100 * i; D.dot(G(r, Z_B3 + 68), 9 * k); D.dot(G(r, Z_PB - 68), 9 * k)
    yb = f2y + Z_B3 * k
    L.chain_h([G(v, 0)[0] for v in (-R_B2, -R_B3, 0, R_B3, R_B2)], yb - 200, yb - 900, lfac=0.25)
    xr = G(rc, 0)[0] + 900
    L.chain_v([G(0, v)[1] for v in (Z_B3, Z_B3 + 50, Z_PB - 50, Z_PB)], G(rc, 0)[0] + 150, xr, lfac=0.25)
    L.lev(Z_B3, G(-R_B3, Z_B3), 'L', ext=G(-R_B3, 0)[0] - G(-rc, 0)[0] + 900); L.lev(Z_PT, G(-R_PT, Z_PT), 'L'); L.lev(Z_PB, G(R_PB - 60, Z_PB), 'L', ext=250)
    L.note('2', 'ш.100', G(900, -4850), G(600, Z_B3 + 50)); L.note('2', 'ш.100', G(-1000, -3600), G(-1050, Z_PB - 50))
    L.note('3', 'ш.100', G(2500, -3900), G(1870, -3760)); L.note('3', 'ш.100', G(900, -2700), G(1700, -3210))
    L.note('4', 'ш.100', G(-2650, -4100), G(-1830, -3830)); L.note('4', 'ш.100', G(-900, -2800), G(-1740, -3100))
    L.note('1', 'ш.100', G(2700, -1900), G(2800, z_top(2800) - 50)); L.note('1', 'ш.100', G(3000, -3500), G(2900, z_bot(2900) + 50))
    L.note('Выпуски Км-1 поз. 1', 'см. л. 4.1', G(-1300, -2300), G(-651, -3300))
    # ---------------- Каркас Кр-1 — аналог л.9-дан клон ----------------
    bx, by = AN08[0] + 2500, AN08[1] + 1000
    tx, ty = sh.X0 + 3500, sh.Y0 + 9000
    L.op(t='import', file=AN, base=[bx, by], to=[tx, ty], wins=[[bx, by, bx + 16500, by + 7800]], pre='N33:')
    sh.notes(['Общие указания см. л. 1.1.', 'Данный лист читать совместно с л. 3.1, 3.2, 3.4.', 'Защитный слой бетона для арматуры фундамента - 50 мм.',
              'Каркасы Кр-1 устанавливать с шагом 1200х1200 для фиксации верхней сетки.'])
    return sh


def b35():
    sh = L.Sheet('3.5', 'Схема расположения выпусков из фундамента Фм-1')
    C = sh.P(18500, 21500)
    L.title('Схема расположения выпусков из фундамента Фм-1', C[0] + 2500, sh.Y0 + 40500)
    L.circle(C, R_OUT, layer=L.L_THIN); L.circle(C, R_WO, layer=L.L_THIN); L.circle(C, R_WI, layer=L.L_THIN)
    L.circle(C, R_COL_O, layer=L.L_THIN); L.circle(C, R_COL_I, layer=L.L_THIN); L.circle(C, R_PT, layer=L.L_THIN)
    D.axes(C)
    nu = Q.NU
    for i in range(nu):
        a = 2 * math.pi * i / nu
        for r in (R_WI + 49, R_WO - 49): L.circle((C[0] + r * math.cos(a), C[1] + r * math.sin(a)), 45, layer='ф18_арм', lw=40)
    for r, n in ((651, Q.NVO), (449, Q.NVI)):
        for i in range(n):
            a = 2 * math.pi * i / n; L.circle((C[0] + r * math.cos(a), C[1] + r * math.sin(a)), 45, layer='ф18_арм', lw=40)
    L.ddim(C, R_WI, 150, tx_out=2000); L.ddim(C, R_WO, 162, tx_out=1300)
    L.note('Вп1', 'ш.100 (%d шт.)' % nu, (C[0] + 5000, C[1] - 12300), (C[0] + 10301 * math.cos(math.radians(-70)), C[1] + 10301 * math.sin(math.radians(-70))))
    L.note('Выпуски Км-1 (поз. 1)', 'ш.100, см. л. 4.1', (C[0] + 3000, C[1] - 3300), (C[0] + 651 * math.cos(math.radians(-45)), C[1] + 651 * math.sin(math.radians(-45))))
    L.circle((C[0] + 10175 * math.cos(math.radians(30)), C[1] + 10175 * math.sin(math.radians(30))), 1500, layer=L.L_THIN)
    L.note('Фрагмент 1', '', (C[0] + 11500, C[1] + 8500), (C[0] + 10175 * math.cos(math.radians(30)) + 1060, C[1] + 10175 * math.sin(math.radians(30)) + 1060))
    L.section('А', (C[0] - 800, C[1] + 9300), (C[0] - 800, C[1] + 11500))
    # ---------- Фрагмент 1 (план ×4) ----------
    k = 4.0; fc = sh.P(41000, 30500)
    L.title('Фрагмент 1', fc[0] + 2000, sh.Y0 + 40500)
    a0, a1 = math.radians(84), math.radians(96)
    def PP(r, a): return (fc[0] + (r * math.cos(a)) * k, fc[1] + (r * math.sin(a) - 10175) * k)
    for r in (R_WI, R_WO):
        L.pl([PP(r, a0 + (a1 - a0) * i / 24.0) for i in range(25)], layer=L.L_THIN)
    L.brk(PP(R_WI - 60, a0), PP(R_WO + 60, a0)); L.brk(PP(R_WI - 60, a1), PP(R_WO + 60, a1))
    da = 2 * math.pi / nu
    for i in range(-10, 11):
        a = math.pi / 2 + i * da
        D.dot(PP(R_WI + 49, a), 9 * k); D.dot(PP(R_WO - 49, a), 9 * k)
        L.line(PP(R_WI + 49, a), PP(R_WO - 49, a), layer=L.L_THIN, ltype='HIDDEN', ltscale=20)
    xm = fc[0]
    L.chain_h([xm - 10175 * 0 + v for v in (0,)], 0, 0) if False else None
    yv = PP(R_WO, math.pi / 2)[1]
    L.chain_v([PP(R_WI, math.pi / 2)[1], PP(R_WI + 40, math.pi / 2)[1], PP(R_WO - 40, math.pi / 2)[1], PP(R_WO, math.pi / 2)[1]], PP(R_WO, a0)[0] + 400, PP(R_WO, a0)[0] + 1300, lfac=0.25)
    p0 = PP(R_WO - 49, math.pi / 2); p1 = PP(R_WO - 49, math.pi / 2 - da)
    L.dim(p0, p1, (p0[0], yv + 900), 0.0, 0.25)
    L.note('Вп1', 'ш.100', (fc[0] - 3300, yv + 1500), PP(R_WO - 49, math.pi / 2 + 4 * da))
    # ---------- А-А (×4, қабырға үзіліспен) ----------
    ax, ay = sh.X0 + 45500 - 10175 * k, sh.Y0 + 13200 + 2300 * k
    L.title('А - А', sh.X0 + 45500, sh.Y0 + 26500)
    def A(r, z): return (ax + r * k, ay + z * k)
    rc = 9150.0; zc = -700.0
    lp = [A(rc, z_top(rc)), A(R_HT, Z_HT), A(R_WI, Z_JOINT), A(R_WI, zc)]
    lq = [A(R_WO, zc), A(R_WO, Z_FL), A(R_OUT, Z_FL), A(R_OUT, Z_BOT), A(R_B1, Z_B1), A(rc, z_bot(rc))]
    L.pl(lp, layer=L.L_THIN); L.pl(lq, layer=L.L_THIN); L.brk(A(rc, z_top(rc) + 60), A(rc, z_bot(rc) - 160)); L.brk(A(R_WI - 40, zc), A(R_WO + 40, zc))
    L.line(A(R_WI, Z_JOINT), A(R_WO, Z_JOINT), layer=L.L_THIN, ltype='HIDDEN', ltscale=20)
    xi, xo = R_WI + 49, R_WO - 49
    D.bar([A(xi, zc), A(xi, Z_BOT + 90), A(xo, Z_BOT + 90), A(xo, zc)])
    L.chain_h([A(v, 0)[0] for v in (R_WI, R_WI + 40, R_WO - 40, R_WO)], ay + zc * k + 300, ay + zc * k + 1000, lfac=0.25)
    L.chain_v([A(0, v)[1] for v in (Z_BOT, Z_BOT + 90, Z_FL)], A(R_OUT, 0)[0] + 150, A(R_OUT, 0)[0] + 900, lfac=0.25)
    L.lev(Z_FL, A(R_OUT, Z_FL), 'R', ext=2600); L.lev(Z_BOT, A(R_OUT, Z_BOT), 'R', ext=2600); L.lev(Z_JOINT, A(R_WI, Z_JOINT), 'L', ext=1500)
    L.note('Вп1 %%C18 А500С', 'ш.100, до отм. +2,260', A(10900, -900), A(xo, -1000))
    L.details(sh.X0 + 3000, sh.Y0 + 8300, [('Вп1', [(0, -1500, '4450'), (700, 0, '250'), (0, 1500, '4450')], '')], rh=3200, w1=9000)
    sh.notes(['Общие указания см. л. 1.1.', 'Данный лист читать совместно с л. 3.2, 3.3, 5.2.',
              'Выпуски Вп1 (U-образные стержни Ø18 А500С, шаг 100 по наружной грани) являются вертикальной арматурой стены См-1 на всю высоту и учтены в спецификации стены См-1 (лист 5.4).',
              'Выпуски в центральную опору Км-1 учтены в спецификации Км-1 (лист 4.1).', NOTES[3]])
    return sh


def b36():
    sh = L.Sheet('3.6', 'Фундамент Фм-2')
    A2, B2 = Q.A2, Q.B2; k = 2.0
    # ---------- опалубка (план, ×2) ----------
    ox, oy = sh.X0 + 4500, sh.Y0 + 21500
    L.title('Опалубочный чертеж фундамента Фм-2', ox + A2 * k / 2, sh.Y0 + 40500)
    def P(a, b): return (ox + a * k, oy + b * k)       # a — резервуардан сыртқа (0…4100), b — ұзын бағыт (0…7600)
    L.pl([P(0, 0), P(A2, 0), P(A2, B2), P(0, B2)], closed=True)
    outer = [P(0, 500), P(3600, 500), P(3600, 7100), P(0, 7100)]; c1 = [P(300, 800), P(3300, 800), P(3300, 3650), P(300, 3650)]; c2 = [P(300, 3950), P(3300, 3950), P(3300, 6800), P(300, 6800)]
    L.pl(outer, closed=True, layer=L.L_THIN); L.pl(c1, closed=True, layer=L.L_THIN); L.pl(c2, closed=True, layer=L.L_THIN); L.hatch([outer, c1, c2])
    L.chain_h([P(v, 0)[0] for v in (0, 300, 3300, 3600, 4100)], oy - 300, oy - 1000, lfac=0.5)
    L.dim(P(0, 0), P(A2, 0), (ox, oy - 1700), 0.0, 0.5)
    L.chain_v([P(0, v)[1] for v in (0, 500, 800, 3650, 3950, 6800, 7100, 7600)], ox + A2 * k + 300, ox + A2 * k + 1000, lfac=0.5)
    L.dim(P(A2, 0), P(A2, B2), (ox + A2 * k + 2300, oy), math.pi / 2, 0.5)
    L.note('Грань у резервуара', '(деформационный шов)', (ox - 2600, oy + 9000), P(0, 4300))
    L.note('См-2', '', P(1700, 8100), P(1500, 7000))
    L.section(1, P(-700, 2200), P(A2 + 1700, 2200))
    # ---------- армирование (план, ×2) ----------
    rx = sh.X0 + 22500
    L.title('Армирование фундамента Фм-2', rx + A2 * k / 2, sh.Y0 + 40500)
    def R(a, b): return (rx + a * k, oy + b * k)
    L.pl([R(0, 0), R(A2, 0), R(A2, B2), R(0, B2)], closed=True, layer=L.L_THIN)
    for b in (2500, 2600): D.bar([R(50, b), R(A2 - 50, b)])
    for a in (1500, 1600): D.bar([R(a, 50), R(a, B2 - 50)])
    L.note('1', 'ш.100', R(2700, 3300), R(2400, 2600)); L.note('1', 'ш.100', R(2500, 5600), R(1600, 5200))
    for (p, q, o, t) in (((62, 2850), (1162, 2850), (700, 1700), (600, 2850)), ((A2 - 62, 2850), (A2 - 1162, 2850), (A2 + 800, 1700), (A2 - 600, 2850)),
                         ((1850, 62), (1850, 1162), (2900, 900), (1850, 600)), ((1850, B2 - 62), (1850, B2 - 1162), (2900, B2 - 700), (1850, B2 - 600))):
        D.bar([R(*p), R(*q)]); L.note('5', 'ш.100', R(*o), R(*t))
    L.chain_h([R(v, 0)[0] for v in (0, 50, A2 - 50, A2)], oy - 300, oy - 1000, lfac=0.5, texts=None)
    L.chain_v([R(0, v)[1] for v in (0, 50, B2 - 50, B2)], rx + A2 * k + 300, rx + A2 * k + 1000, lfac=0.5)
    # ---------- Разрез 1-1 (×4) ----------
    k4 = 4.0; sx, sy = sh.X0 + 4500, sh.Y0 + 9500
    L.title('Разрез 1-1', sx + 8200, sh.Y0 + 16500)
    def S(a, z): return (sx + a * k4, sy + (z + 2700) * k4)
    lp = [S(0, -2700), S(A2, -2700), S(A2, -2200), S(3600, -2200), S(3600, -1500)]; lq = [S(3300, -1500), S(3300, -2200), S(300, -2200), S(300, -1500)]; lr = [S(0, -1500), S(0, -2700)]
    L.pl(lp, layer=L.L_THIN); L.pl(lq, layer=L.L_THIN); L.pl(lr, layer=L.L_THIN)
    L.brk(S(-40, -1500), S(340, -1500)); L.brk(S(3260, -1500), S(3640, -1500))
    pd = [S(0, -2700), S(0, -2800), S(A2 + 100, -2800), S(A2 + 100, -2700)]; L.pl(pd, layer=L.L_THIN); L.hatch([pd], pat='AR-CONC', sc=2)
    D.bar([S(50, -2650), S(A2 - 50, -2650)]); D.bar([S(50, -2250), S(A2 - 50, -2250)])
    for i in range(40):
        a = 100 + 100 * i; D.dot(S(a, -2632), 9 * k4); D.dot(S(a, -2268), 9 * k4)
    for a0, sg in ((62, 1), (A2 - 62, -1)): D.bar([S(a0 + sg * 1100, -2272), S(a0, -2272), S(a0, -2628), S(a0 + sg * 1100, -2628)])
    for a in (49, 251, 3349, 3551): pass
    for (xa, xb) in ((49, 251), (3349, 3551)): D.bar([S(xa, -1500), S(xa, -2610), S(xb, -2610), S(xb, -1500)])
    L.chain_h([S(v, 0)[0] for v in (0, 300, 3300, 3600, A2)], sy - 600, sy - 1300, lfac=0.25)
    L.chain_v([S(0, v)[1] for v in (-2700, -2650, -2250, -2200)], S(A2, 0)[0] + 300, S(A2, 0)[0] + 1000, lfac=0.25)
    L.lev(-2200, S(A2, -2200), 'R', ext=2700); L.lev(-2700, S(A2 + 100, -2700), 'R', ext=2300)
    L.note('1', 'ш.100', S(1700, -1800), S(1500, -2250)); L.note('1', 'ш.100', S(1400, -3050), S(1900, -2650))
    L.note('5', 'ш.100', S(4450, -1800), S(A2 - 62, -2450)); L.note('Вп2', 'ш.100, см. л. 5.6', S(700, -1150), S(251, -1700))
    L.note('Кр-1', 'ш.1200х1200', S(2500, -1500), S(2300, -2400))
    for a in (2200.0, 2450.0): L.pl([S(a, -2630), S(a, -2270)], layer='ф16_арм', lw=40)
    # ---------- кестелер ----------
    rows = Q.Q['Фм-2']; V = Q.V
    tb, yb = L.spec(sh.X0 + 58900 - 18500, sh.Y0 + 41500, 'Фундамент Фм-2', rows, [L.BETON + (V['Фм-2'],), L.PODG + (V['Подготовка Фм-2'],)], bent=('5',))
    L.steel(sh.X0 + 58900 - 24584, yb - 1500, 'Фундамент Фм-2', rows)
    L.details(sh.X0 + 40500, yb - 10500, [('5', [(1100, 0, '1100'), (0, -420, '420'), (-1100, 0, '1100')], '')], w1=9000)
    sh.notes(['Общие указания см. л. 1.1.', 'Фундамент Фм-2 отделен от фундамента Фм-1 деформационным швом; грань плиты со стороны резервуара - в одной плоскости с гранью стены камеры.'] + NOTES[1:])
    return sh


def b41():
    sh = L.Sheet('4.1', 'Центральная опора Км-1')
    k = 4.0; H = Q.H_KM
    cx, y0 = sh.X0 + 9500, sh.Y0 + 6500 + 4625 * k       # z → y0 + z*k
    L.title('Центральная опора Км-1 (армирование)', cx + 1500, sh.Y0 + 40500)
    def S(r, z): return (cx + r * k, y0 + z * k)
    zb = Z_B3
    for sg in (1, -1):
        L.pl([S(sg * 1500, Z_PB), S(sg * R_COL_O, Z_PB), S(sg * R_COL_O, Z_TOPW), S(0, Z_TOPW)], layer=L.L_THIN)
        L.pl([S(sg * R_COL_I, Z_PB), S(sg * R_COL_I, Z_TOPW - 262), S(0, Z_TOPW - 262)], layer=L.L_THIN)
        L.pl([S(sg * 1500, zb), S(0, zb)], layer=L.L_THIN); L.brk(S(sg * 1500, Z_PB + 60), S(sg * 1500, zb - 60))
        for r, fo in ((651, 1), (449, -1)):
            D.bar([S(sg * (r + fo * 400), zb + 110), S(sg * r, zb + 110), S(sg * r, Z_TOPW - 40)])
        nr = int(math.ceil(H / 100)) + 1
        for i in range(nr):
            z = Z_PB + 50 + i * (H - 100) / (nr - 1)
            D.dot(S(sg * 669, z), 9 * k); D.dot(S(sg * 431, z), 9 * k)
        for i in range(0, 16):
            z = Z_PB + 250 + i * 400
            if z < Z_TOPW - 300: L.pl([S(sg * 431, z), S(sg * 669, z)], layer='ф8_арм', lw=35)
    # оголовок П-стержені
    D.bar([S(-660, Z_TOPW - 340), S(-660, Z_TOPW - 40), S(660, Z_TOPW - 40), S(660, Z_TOPW - 340)])
    for i in range(14): D.dot(S(-650 + 100 * i, Z_TOPW - 58), 9 * k)
    L.line(S(0, zb - 200), S(0, Z_TOPW + 300), **D.AX)
    L.chain_h([S(v, 0)[0] for v in (-700, -400, 0, 400, 700)], y0 + Z_TOPW * k + 300, y0 + Z_TOPW * k + 1000, lfac=0.25)
    xr = S(1500, 0)[0] + 800
    L.chain_v([S(0, v)[1] for v in (zb, Z_PB, Z_TOPW - 262, Z_TOPW)], S(1500, 0)[0] + 100, xr, lfac=0.25)
    L.lev(Z_TOPW, S(R_COL_O, Z_TOPW), 'R', ext=3600); L.lev(Z_PB, S(1500, Z_PB), 'R', ext=1900); L.lev(zb, S(-1500, zb), 'L', ext=900)
    L.note('1', 'ш.100', S(-1800, 0), S(-651, -300)); L.note('2', 'ш.100', S(-1800, -1200), S(-669, -1620)); L.note('3', 'ш.100', S(1500, -2300), S(431, -2700))
    L.note('4', 'ш.100', S(1500, 2700), S(300, Z_TOPW - 40)); L.note('Шп1', 'ш.400х400', S(1500, 900), S(550, 575))
    L.section(1, S(-1300, 1300), S(1300, 1300))
    # ---------- 1-1 ----------
    C = (sh.X0 + 27500, sh.Y0 + 30500)
    L.title('1 - 1', C[0], sh.Y0 + 36500)
    L.circle(C, R_COL_O * k, layer=L.L_THIN); L.circle(C, R_COL_I * k, layer=L.L_THIN)
    L.circle(C, 669 * k, layer='ф18_арм', lw=40); L.circle(C, 431 * k, layer='ф18_арм', lw=40)
    for r, n in ((651, Q.NVO), (449, Q.NVI)):
        for i in range(n):
            a = 2 * math.pi * i / n; D.dot((C[0] + r * k * math.cos(a), C[1] + r * k * math.sin(a)), 9 * k)
    for i in range(8):
        a = 2 * math.pi * i / 8 + 0.2; L.pl([(C[0] + 431 * k * math.cos(a), C[1] + 431 * k * math.sin(a)), (C[0] + 669 * k * math.cos(a), C[1] + 669 * k * math.sin(a))], layer='ф8_арм', lw=35)
    L.ddim(C, R_COL_O * k, 150, lfac=0.25, tx_out=1500); L.ddim(C, R_COL_I * k, 30, lfac=0.25, tx_out=2600)
    L.note('1', 'ш.100 (%d шт.)' % Q.NVO, (C[0] + 3500, C[1] - 3200), (C[0] + 651 * k * math.cos(-0.6), C[1] + 651 * k * math.sin(-0.6)))
    L.note('1', 'ш.100 (%d шт.)' % Q.NVI, (C[0] - 4200, C[1] - 3300), (C[0] + 449 * k * math.cos(-2.4), C[1] + 449 * k * math.sin(-2.4)))
    L.note('2', '', (C[0] + 3600, C[1] + 2600), (C[0] + 669 * k * math.cos(0.6), C[1] + 669 * k * math.sin(0.6)))
    L.note('3', '', (C[0] - 3800, C[1] + 2700), (C[0] + 431 * k * math.cos(2.5), C[1] + 431 * k * math.sin(2.5)))
    # ---------- кестелер ----------
    rows = Q.Q['Км-1']
    tb, yb = L.spec(sh.X0 + 58900 - 18500, sh.Y0 + 41500, 'Центральная опора Км-1', rows, [L.BETON + (Q.V['Км-1'],)], bent=('1', '2', '3', '4', 'Шп1'))
    L.steel(sh.X0 + 58900 - 24584, yb - 1500, 'Опора Км-1', rows)
    r2 = [r for r in rows if r['pos'] == '2'][0]['L']; r3 = [r for r in rows if r['pos'] == '3'][0]['L']
    L.details(sh.X0 + 19500, sh.Y0 + 23500, [
        ('1', [(400, 0, '400'), (0, 6740, '6740')], ''),
        ('2', [(700, 0, ''), (500, 500, ''), (0, 700, ''), (-500, 500, ''), (-700, 0, 'Ø1338, L=%d' % r2), (-500, -500, ''), (0, -700, ''), (500, -500, '')], 'нахлест 1100'),
        ('3', [(500, 0, ''), (350, 350, ''), (0, 500, ''), (-350, 350, ''), (-500, 0, 'Ø862, L=%d' % r3), (-350, -350, ''), (0, -500, ''), (350, -350, '')], 'нахлест 1100'),
        ('4', [(0, -300, '300'), (1320, 0, '1320'), (0, 300, '300')], ''),
        ('Шп1', [(70, -70, '100'), (220, 0, '220'), (70, 70, '100')], '')], w1=11500, rh=3300)
    sh.notes(['Общие указания см. л. 1.1.', 'Защитный слой бетона для арматуры опоры - 40 мм.',
              'Вертикальные стержни поз. 1 выполняются Г-образными на всю высоту опоры с заделкой в днище приямка.'] + NOTES[1:])
    return sh


B = {'3.2': b32, '3.3': b33, '3.5': b35, '3.6': b36, '4.1': b41}
if __name__ == '__main__':
    import s1_run
    for n in sys.argv[1].split(','): s1_run.go(B[n], 'p' + n.replace('.', ''), dpi=100)
