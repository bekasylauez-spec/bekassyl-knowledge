# -*- coding: utf-8 -*-
"""Парақ 6 (пилот): Опалубочный чертеж фундамента Фм-1. Разрез 1-1 (опалубка). Аналог л.7."""
import math
import s1_lib as L
from s1_geo import *


def half_loop(sgn, cx, y0, k, top, bot):
    return [(cx + sgn * r * k, y0 + z * k) for r, z in top] + [(cx + sgn * r * k, y0 + z * k) for r, z in bot]


def build():
    sh = L.Sheet('3.1', 'Опалубочный чертеж фундамента Фм-1. Разрез 1-1')
    P = sh.P
    # ---------------- план 1:100 ----------------
    C = P(17500, 26800)
    L.title('Опалубочный чертеж фундамента Фм-1', C[0], sh.Y0 + 40500)
    L.circle(C, R_OUT)                                   # ернеу сырты
    L.circle(C, R_WO, layer=L.L_THIN); L.circle(C, R_WI, layer=L.L_THIN)   # қабырға (См-1) қырлары
    L.circle(C, R_HT, layer=L.L_THIN)                    # вут табаны
    L.circle(C, R_PT)                                    # приямок жиегі
    L.circle(C, R_PB)                                    # приямок түбі
    L.circle(C, R_COL_O); L.circle(C, R_COL_I)           # орталық тірек Км-1
    L.hatch([L.ring_pts(C, R_COL_O), L.ring_pts(C, R_COL_I)])
    # осьтер (аналог: ГОСТ 2.303 5, lts 100, шеңбер r=350 сол жақта және төменде)
    ax = dict(layer=L.L_DIM, ltype='ГОСТ 2.303 5', ltscale=100, lw=9)
    L.line((C[0] - 12700, C[1]), (C[0] + 11900, C[1]), **ax)
    L.line((C[0], C[1] - 11500), (C[0], C[1] + 11500), **ax)
    L.circle((C[0] - 13050, C[1]), 350, layer=L.L_DIM, lw=25)
    L.circle((C[0], C[1] - 11850), 350, layer=L.L_DIM, lw=25)
    # диаметрлер
    L.ddim(C, R_OUT, 135); L.ddim(C, R_WO, 122); L.ddim(C, R_WI, 109)
    L.ddim(C, R_HT, 60, tx_out=-1500)
    L.ddim(C, R_PT, 35, tx_out=1100); L.ddim(C, R_PB, 160, tx_out=2400); L.ddim(C, R_COL_O, -35, tx_out=2300)
    # разрез 1-1 (осьтік)
    L.section(1, (C[0] - 11600, C[1]), (C[0] + 11600, C[1]))
    L.note('Стена См-1', '', (C[0] + 6200, C[1] - 9900), (C[0] + 10175 * math.cos(math.radians(-55)), C[1] + 10175 * math.sin(math.radians(-55))))
    L.note('Приямок', '', (C[0] + 3300, C[1] - 3300), (C[0] + 1630 * math.cos(math.radians(-60)), C[1] + 1630 * math.sin(math.radians(-60))))
    L.note('Км-1', '', (C[0] + 1500, C[1] + 3300), (C[0] + 550 * math.cos(math.radians(70)), C[1] + 550 * math.sin(math.radians(70))))

    # ---------------- Разрез 1-1 (опалубка) 1:100 ----------------
    cx, y0 = C[0], sh.Y0 + 12300
    L.title('Разрез 1-1 (Опалубка)', cx, sh.Y0 + 13500)
    def S(r, z): return (cx + r, y0 + z)
    loop = [S(r, z) for r, z in TOP] + [S(r, z) for r, z in BOT] + [S(-r, z) for r, z in reversed(BOT[:-1])] + [S(-r, z) for r, z in reversed(TOP[1:])]
    L.pl(loop, closed=True)
    L.hatch([loop])
    podl = [S(r, z) for r, z in POD] + [S(-r, z) for r, z in reversed(POD[:-1])]
    L.pl(podl, layer=L.L_THIN)
    edge = [S(R_OUT, Z_BOT)] + [S(r, z) for r, z in BOT] + [S(-r, z) for r, z in reversed(BOT[:-1])] + [S(-R_OUT, Z_BOT)]
    L.hatch([podl + list(reversed(edge))], pat='AR-CONC', sc=2)
    for sg in (1, -1):
        # қабырға (См-1) басталуы
        L.line(S(sg * R_WI, Z_JOINT), S(sg * R_WI, Z_JOINT + 420), layer=L.L_THIN); L.line(S(sg * R_WO, Z_JOINT), S(sg * R_WO, Z_JOINT + 420), layer=L.L_THIN)
        L.brk(S(sg * (R_WI - 120), Z_JOINT + 420), S(sg * (R_WO + 120), Z_JOINT + 420))
        # Км-1 басталуы
        L.line(S(sg * R_COL_O, Z_PB), S(sg * R_COL_O, Z_PB + 900), layer=L.L_THIN); L.line(S(sg * R_COL_I, Z_PB), S(sg * R_COL_I, Z_PB + 900), layer=L.L_THIN)
    L.brk(S(-R_COL_O - 120, Z_PB + 900), S(R_COL_O + 120, Z_PB + 900))
    L.line(S(0, Z_B3 - 500), S(0, Z_JOINT + 700), layer=L.L_DIM, ltype='ГОСТ 2.303 5', ltscale=100, lw=9)
    # размерлер: төменгі тізбек + жалпы
    yd = y0 + Z_B3 - 1750
    xs = [cx + v for v in (-R_OUT, -R_WO, -R_HT, -R_PT, -R_PB, 0, R_PB, R_PT, R_HT, R_WO, R_OUT)]
    L.chain_h(xs, y0 + Z_B3 - 250, yd)
    L.dim((cx - R_OUT, y0 + Z_B3 - 250), (cx + R_OUT, y0 + Z_B3 - 250), (cx, yd - 700))
    # отметкалар
    L.lev(Z_FL, S(R_OUT, Z_FL), 'R', ext=1300)
    L.lev(Z_B3, S(R_B3, Z_B3), 'R', ext=R_OUT - R_B3 + 1300)
    L.lev(Z_BOT, S(-R_OUT, Z_BOT), 'L', ext=1300)
    L.lev(Z_JOINT, S(-R_WO, Z_JOINT), 'L', ext=1800)
    # еңіс
    for sg in (1, -1):
        rm = 5600; a = math.atan2((Z_HT - Z_PT), (R_HT - R_PT)) * sg
        L.mtext('i=1:12', cx + sg * rm, y0 + z_top(rm) + 330, 250, att=8, layer=L.L_DIM, rot=a)
    # фрагмент белгілері
    L.circle(S(R_WO - 250, -1750), 1150, layer=L.L_THIN)
    L.note('Фрагмент 1', '', S(R_WO + 1500, -100), (cx + R_WO - 250 + 1150 * math.cos(math.radians(60)), y0 - 1750 + 1150 * math.sin(math.radians(60))))
    L.circle(S(0, -3350), 2600, layer=L.L_THIN)
    L.note('Фрагмент 2', '', S(-4200, -1150), (cx - 2600 * math.cos(math.radians(40)), y0 - 3350 + 2600 * math.sin(math.radians(40))))

    # ---------------- Фрагмент 1 (ернеу, вут), сурет ×4, dimlfac 0.25 ----------------
    k = 4.0; f1x, f1y = sh.X0 + 47300 - 10000 * k, sh.Y0 + 31300 + 2300 * k     # r=10000 → x 47300; z=-2300 → y 31300
    def F(r, z): return (f1x + r * k, f1y + z * k)
    L.title('Фрагмент 1', sh.X0 + 47300, sh.Y0 + 40500)
    rc = 9150.0
    lp = [F(rc, z_top(rc)), F(R_HT, Z_HT), F(R_WI, Z_JOINT), F(R_WO, Z_JOINT), F(R_WO, Z_FL), F(R_OUT, Z_FL), F(R_OUT, Z_BOT), F(R_B1, Z_B1), F(rc, z_bot(rc))]
    L.pl(lp[:], closed=False)
    L.hatch([lp])
    L.brk(F(rc, z_top(rc) + 60), F(rc, z_bot(rc) - 160))
    zp = lambda r: z_bot(r) - 100 if r < 10044 else Z_BOT - 100
    pod1 = [F(R_POD, Z_BOT), F(R_POD, Z_BOT - 100), F(10044, Z_BOT - 100), F(rc, zp(rc) + 0.3)]
    L.pl([F(R_OUT, Z_BOT)] + pod1, layer=L.L_THIN)
    L.hatch([[F(R_OUT, Z_BOT)] + pod1 + [F(rc, z_bot(rc)), F(R_B1, Z_B1)]], pat='AR-CONC', sc=2)
    L.line(F(R_WI, Z_JOINT), F(R_WI, Z_JOINT + 330), layer=L.L_THIN); L.line(F(R_WO, Z_JOINT), F(R_WO, Z_JOINT + 330), layer=L.L_THIN)
    L.brk(F(R_WI - 40, Z_JOINT + 330), F(R_WO + 40, Z_JOINT + 330))
    yd = f1y + (Z_BOT - 100) * k - 900
    L.chain_h([F(v, 0)[0] for v in (R_HT, R_WI, R_WO, R_OUT, R_POD)], f1y + (Z_BOT - 100) * k - 200, yd, lfac=0.25)
    L.chain_h([F(v, 0)[0] for v in (R_B1, R_OUT)], f1y + (Z_BOT - 100) * k - 200, yd - 700, lfac=0.25)
    xv = F(R_POD, 0)[0] + 900
    L.chain_v([F(0, v)[1] for v in (Z_BOT, Z_FL, Z_JOINT)], F(R_POD, 0)[0] + 150, xv, lfac=0.25)
    L.lev(Z_JOINT, F(R_WO, Z_JOINT), 'R', ext=F(R_POD, 0)[0] + 1500 - F(R_WO, 0)[0])
    L.lev(Z_FL, F(R_OUT, Z_FL), 'R', ext=F(R_POD, 0)[0] + 1500 - F(R_OUT, 0)[0])
    L.lev(Z_BOT, F(R_POD, Z_BOT), 'R', ext=1500)
    L.lev(Z_HT, F(R_HT, Z_HT), 'L', ext=F(R_HT, 0)[0] - F(rc, 0)[0] + 700)
    # вут өлшемдері 500×500 (ішкі жағынан)
    L.dim(F(R_HT, Z_JOINT + 60), F(R_WI, Z_JOINT + 60), F(R_HT, Z_JOINT + 220), 0.0, 0.25)
    L.dim(F(R_HT - 60, Z_HT), F(R_HT - 60, Z_JOINT), F(R_HT - 200, Z_HT), math.pi / 2, 0.25)
    # днище қалыңдығы 500 (еңіске перпендикуляр)
    rt = 9300.0; nx, nz = (Z_HT - Z_PT) / 7500.0, -1.0; nl = math.hypot(nx, nz); nx, nz = nx / nl, nz / nl
    p1 = (rt, z_top(rt)); p2 = (rt + nx * 500, z_top(rt) + nz * 500)
    L.note('t=500', '', F(9350, -1150), F(9400, z_top(9400) - 250))
    L.note('Подготовка из бетона', 'толщиной 100 мм', F(9250, -2950), F(9600, zp(9600) + 50))
    L.note('Рабочий шов', '', F(10700, -900), F(10250, Z_JOINT))

    # ---------------- Фрагмент 2 (приямок), сурет ×4, dimlfac 0.25 ----------------
    f2x, f2y = sh.X0 + 47000, sh.Y0 + 14300 + 4625 * k
    def G(r, z): return (f2x + r * k, f2y + z * k)
    L.title('Фрагмент 2', f2x, sh.Y0 + 27500)
    rc = 2450.0
    lp = [G(-rc, z_top(rc)), G(-R_PT, Z_PT), G(-R_PB, Z_PB), G(R_PB, Z_PB), G(R_PT, Z_PT), G(rc, z_top(rc)), G(rc, z_bot(rc)), G(R_B2, Z_B2), G(R_B3, Z_B3), G(-R_B3, Z_B3), G(-R_B2, Z_B2), G(-rc, z_bot(rc))]
    L.pl(lp[:6]); L.pl(lp[6:])
    L.hatch([lp])
    for sg in (1, -1):
        L.brk(G(sg * rc, z_top(rc) + 60), G(sg * rc, z_bot(rc) - 160))
        L.line(G(sg * R_COL_O, Z_PB), G(sg * R_COL_O, Z_PB + 700), layer=L.L_THIN); L.line(G(sg * R_COL_I, Z_PB), G(sg * R_COL_I, Z_PB + 700), layer=L.L_THIN)
    L.brk(G(-R_COL_O - 40, Z_PB + 700), G(R_COL_O + 40, Z_PB + 700))
    L.line(G(0, -4625 - 150), G(0, Z_PT + 250), layer=L.L_DIM, ltype='ГОСТ 2.303 5', ltscale=100, lw=9)
    pod2 = [G(-rc, z_bot(rc) - 100), G(-2404, -2937), G(-1656, -4625), G(1656, -4625), G(2404, -2937), G(rc, z_bot(rc) - 100)]
    L.pl(pod2, layer=L.L_THIN)
    L.hatch([pod2 + [G(rc, z_bot(rc)), G(R_B2, Z_B2), G(R_B3, Z_B3), G(-R_B3, Z_B3), G(-R_B2, Z_B2), G(-rc, z_bot(rc))]], pat='AR-CONC', sc=2)
    yb = f2y - 4625 * k
    L.chain_h([G(v, 0)[0] for v in (-R_B2, -R_B3, 0, R_B3, R_B2)], yb - 200, yb - 900, lfac=0.25)
    yt = G(0, Z_PT)[1]
    L.chain_h([G(v, 0)[0] for v in (-R_PT, -R_PB, -R_COL_O, -R_COL_I, 0, R_COL_I, R_COL_O, R_PB, R_PT)], yt + 500, yt + 1100, lfac=0.25)
    xr = G(rc, 0)[0] + 900
    L.chain_v([G(0, v)[1] for v in (-4625, Z_B3, Z_PB, Z_PT)], G(rc, 0)[0] + 150, xr, lfac=0.25)
    L.lev(Z_B3, G(-R_B3, Z_B3), 'L', ext=G(-R_B3, 0)[0] - G(-rc, 0)[0] + 900)
    L.lev(Z_PT, G(-R_PT, Z_PT), 'L', ext=None)
    L.lev(Z_PB, G(-R_PB + 60, Z_PB), 'R', ext=250)
    L.note('Км-1', '', G(1250, -3050), G(550, -3500))

    sh.notes(['Общие указания см. л. 1.1.',
              'Данный лист читать совместно с л. 2.3, 3.2, 3.3.',
              'Под фундаментом выполнить подготовку из бетона толщиной 100 мм.',
              'Рабочий шов бетонирования стены См-1 выполнить на отм. -1,242 (верх вута).'])
    return sh


if __name__ == '__main__':
    import s1_run
    s1_run.go(build, 'p31')
