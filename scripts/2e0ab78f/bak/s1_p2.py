# -*- coding: utf-8 -*-
"""1.3 котлован мен свая схемасы; 2.1, 2.2 схемалар; 2.3 разрездер."""
import math, sys
import s1_lib as L, s1_draw as D, s1_qty as Q
from s1_geo import *

N0 = 'Общие указания см. л. 1.1.'


def el_table(x, ytop, title, rows):
    """Спецификация элементов (схема): rows — [(марка, лист, атауы, саны)] не ('—', тақырып)"""
    th = L.tag('th'); tb = L.tag('tb')
    L.op(t='clone', h='CW:67A317', base=[20200, 722204], to=[x, ytop], tag=th)
    L.op(t='tset', h=th, cells=[[0, 0, title]])
    L.op(t='clone', h='CW:679DB6', base=[20200, 719904], to=[x, ytop - 2300], tag=tb)
    n = len(rows)
    # донор: R0 (тақырып жолы, аты біріктірілген) + 12 жол; тек R0 типті жол керек → R0-ден мұралап қосамыз, қалғанын өшіреміз
    L.op(t='trows', h=tb, mode='del', at=1, n=12)
    if n > 1: L.op(t='trows', h=tb, mode='ins', at=1, **{'from': 0}, n=n - 1)
    cells = []
    for i, r in enumerate(rows):
        if len(r) == 2: cells += [[i, 0, ''], [i, 1, ''], [i, 2, r[1]], [i, 10, ''], [i, 11, ''], [i, 12, '']]
        else: cells += [[i, 0, r[0]], [i, 1, r[1]], [i, 2, r[2]], [i, 10, str(r[3])], [i, 11, ''], [i, 12, '']]
    L.op(t='tset', h=tb, cells=cells)
    return ytop - 2300 - 800 * n


def b13():
    sh = L.Sheet('1.3', 'Схема расположения котлована и раскатных свай')
    C = sh.P(20500, 19800)
    L.title('Схема расположения котлована и раскатных свай', C[0] + 6000, sh.Y0 + 40500)
    ZG, ZK1, ZK2 = Q.Z_GR, Q.Z_K1, Q.Z_K2; RC = Q.R_CUSH; RT = RC + 0.5 * (ZG - ZK1)
    L.circle(C, R_OUT, layer=L.L_THIN); L.circle(C, R_WO, layer=L.L_THIN); L.circle(C, R_WI, layer=L.L_THIN)
    L.circle(C, RC); L.circle(C, RT, layer=L.L_THIN, ltype='HIDDEN', ltscale=50)
    L.circle(C, 2700, layer=L.L_THIN); L.circle(C, 2700 + 0.5 * (ZK1 - ZK2), layer=L.L_THIN, ltype='HIDDEN', ltscale=50)
    D.axes(C, 13900, 13500)
    D.camera_plan(C, slab=True, walls=True, hatch=False)
    # камера котлованы: подушка плитадан 1000 шығады
    L.pl(D.rect_uv(C, D.U0, D.U0 + 4100 + 1000, -4800, 4800), layer=L.L_CONT)
    for x, y, m in D.pile_points():
        p = (C[0] + x, C[1] + y)
        L.circle(p, 250, layer=L.L_CONT)
        if m == 'Св1': L.op(t='hatch', pat='SOLID', layer=L.L_DIM, lw=0, loops=[[list(q) for q in L.ring_pts(p, 250, 16)]])
    L.ddim(C, RC, 150, tx_out=1500); L.ddim(C, RT, 165, tx_out=1500); L.ddim(C, 10175, 120, tx_out=2500)
    L.dim((C[0], C[1] - 13000), (C[0] + 2000, C[1] - 13000), (C[0], C[1] - 13400)); L.dim((C[0] + 2000, C[1] - 13000), (C[0] + 4000, C[1] - 13000), (C[0], C[1] - 13400))
    L.note('Св1 %%C500', 'L=11000, шаг не более 1000', (C[0] + 11500, C[1] - 9500), (C[0] + 10175 * math.cos(math.radians(-40)) + 180, C[1] + 10175 * math.sin(math.radians(-40)) - 180))
    L.note('Св2 %%C500', 'L=9000, шаг 2000х2000', (C[0] - 9000, C[1] - 12300), (C[0] - 4000, C[1] - 6000 - 250))
    L.note('Св1 %%C500', 'L=11000 (7 шт.)', (C[0] + 3200, C[1] + 3600), (C[0] + 950 * math.cos(math.radians(60)), C[1] + 950 * math.sin(math.radians(60)) + 250))
    L.note('Граница подушки', '(дно котлована)', (C[0] - 12500, C[1] + 11800), (C[0] + RC * math.cos(math.radians(135)), C[1] + RC * math.sin(math.radians(135))))
    L.note('Бровка котлована', '', (C[0] - 13500, C[1] + 9800), (C[0] + RT * math.cos(math.radians(150)), C[1] + RT * math.sin(math.radians(150))))
    L.mtext('-3,950', C[0] - 6500, C[1] + 3000, 250, att=5, layer=L.L_DIM); L.mtext('-5,650', C[0] + 600, C[1] - 1900, 250, att=5, layer=L.L_DIM)
    L.mtext('-3,950', *D.uv(C, D.U0 + 4650, 2500), 250, att=5, layer=L.L_DIM)
    # шартты белгілер
    lx, ly = sh.X0 + 42000, sh.Y0 + 36000
    L.mtext('{\\LУсловные обозначения}', lx + 6000, ly + 1500, 350, att=2, layer=L.L_DIM)
    p = (lx + 400, ly); L.circle(p, 250); L.op(t='hatch', pat='SOLID', layer=L.L_DIM, lw=0, loops=[[list(q) for q in L.ring_pts(p, 250, 16)]])
    L.mtext('- раскатная свая Св1 Ø500, L=11000, армируемая (%d шт.)' % Q.NSV1, lx + 1100, ly, 250, att=4)
    L.circle((lx + 400, ly - 1100), 250)
    L.mtext('- раскатная свая Св2 Ø500, L=9000, неармируемая (%d шт.)' % Q.NSV2, lx + 1100, ly - 1100, 250, att=4)
    sh.notes(['Раскатные сваи Ø500 (бетон C16/20 W10 на с.ф.ц.): Св1 L=11000 - армируемые, под стеной См-1, центральной опорой Км-1 и стенами камеры с шагом не более 1000 (%d шт.); Св2 L=9000 - неармируемые, под днищем Фм-1 с шагом 2000х2000 (%d шт.).' % (Q.NSV1, Q.NSV2),
              'Дно котлована и верх свай - отм. -3,950, в зоне приямка - отм. -5,650. Уровень земли - отм. -2,200.',
              'Армирование свай см. лист 1.5. Под фундаментами - подушка из уплотненного суглинка толщ. не менее 1000 мм (К=0,95), см. лист 1.4.'])
    return sh


def b21():
    sh = L.Sheet('2.1', 'Схема расположения элементов на отм. -1.700')
    C = sh.P(18500, 19500)
    L.title('Схема расположения элементов на отм. -1.700', C[0] + 3500, sh.Y0 + 40500)
    L.circle(C, R_OUT)
    L.circle(C, R_WO); L.circle(C, R_WI); L.hatch([L.ring_pts(C, R_WO, 180), L.ring_pts(C, R_WI, 180)])
    L.circle(C, R_HT, layer=L.L_THIN); L.circle(C, R_PT); L.circle(C, R_PB, layer=L.L_THIN)
    L.circle(C, R_COL_O); L.circle(C, R_COL_I); L.hatch([L.ring_pts(C, R_COL_O), L.ring_pts(C, R_COL_I)])
    D.axes(C)
    D.camera_plan(C)
    L.line(C, D.uv(C, 16500, 0), **D.AX)
    L.ddim(C, R_OUT, 150); L.ddim(C, R_WO, 162); L.ddim(C, R_WI, 174, tx_out=1600)
    L.adim(C, D.uv(C, D.U0, 0), D.uv(C, D.U0 / 2, 900))
    L.section(1, (C[0] - 11700, C[1]), (C[0] + 11700, C[1]))
    L.section(2, D.uv(C, 8300, -600), D.uv(C, 15900, -600))
    L.section(3, D.uv(C, D.U0 + 1800, -4500), D.uv(C, D.U0 + 1800, 4500))
    L.note('Фм-1', '', (C[0] - 5200, C[1] - 6000), (C[0] - 6500, C[1] - 7400))
    L.note('См-1', '', (C[0] + 5200, C[1] - 11900), (C[0] + 10175 * math.cos(math.radians(-70)), C[1] + 10175 * math.sin(math.radians(-70))))
    L.note('Км-1', '', (C[0] + 1700, C[1] - 2900), (C[0] + 550 * math.cos(math.radians(-50)), C[1] + 550 * math.sin(math.radians(-50))))
    L.note('Фм-2', '', D.uv(C, 17000, 2600), D.uv(C, D.U0 + 3850, 3000))
    L.note('См-2', '', D.uv(C, 16800, -1500), D.uv(C, D.U0 + 3450, -1500))
    L.mtext('i=1:12', C[0] - 5600, C[1] + 250, 250, att=8, layer=L.L_DIM); L.mtext('i=1:12', C[0] + 5600, C[1] + 250, 250, att=8, layer=L.L_DIM)
    el_table(sh.X0 + 40400, sh.Y0 + 18000, 'Спецификация элементов на отм. -1.700 и +2.300', [
        ('', 'Фундаменты:'), ('Фм-1', 'листы 3.1 - 3.5', 'Фундамент Фм-1', 1), ('Фм-2', 'лист 3.6', 'Фундамент Фм-2', 1),
        ('', 'Опора:'), ('Км-1', 'лист 4.1', 'Центральная опора Км-1', 1),
        ('', 'Стены:'), ('См-1', 'листы 5.1 - 5.4', 'Стена См-1', 1), ('См-2', 'листы 5.5 - 5.7', 'Стены камеры См-2', 1),
        ('', 'Плита:'), ('Пм-1', 'лист 7.1', 'Плита покрытия камеры Пм-1', 1)])
    sh.notes([N0, 'Отверстия, гильзы и закладные детали уточнить по разделу ТХ.'])
    return sh


def b22():
    sh = L.Sheet('2.2', 'Схема расположения элементов на отм. +2.300')
    C = sh.P(18500, 19500)
    L.title('Схема расположения элементов на отм. +2.300', C[0] + 3500, sh.Y0 + 40500)
    L.circle(C, 11000)
    L.circle(C, R_WO, layer=L.L_THIN); L.circle(C, R_WI)
    L.circle(C, 9500); L.circle(C, 9300)
    L.hatch([L.ring_pts(C, 9500, 180), L.ring_pts(C, 9300, 180)])
    L.circle(C, R_COL_O); L.op(t='hatch', pat='ANSI36', sc=20, layer=L.L_DIM, lw=5, loops=[[list(q) for q in L.ring_pts(C, R_COL_O)]])
    D.axes(C)
    D.camera_plan(C, slab=False, cover=True)
    L.line(C, D.uv(C, 16500, 0), **D.AX)
    L.ddim(C, 11000, 150); L.ddim(C, R_WI, 165, tx_out=1900); L.ddim(C, 9300, 120, tx_out=-2500)
    L.section(1, (C[0] - 11900, C[1]), (C[0] + 11900, C[1]))
    L.section(2, D.uv(C, 8300, -600), D.uv(C, 15900, -600))
    L.note('См-1', '', (C[0] + 4200, C[1] - 12300), (C[0] + 10175 * math.cos(math.radians(-70)), C[1] + 10175 * math.sin(math.radians(-70))))
    L.note('Консоль', '650х120', (C[0] - 9000, C[1] - 12200), (C[0] + 10700 * math.cos(math.radians(-120)), C[1] + 10700 * math.sin(math.radians(-120))))
    L.note('Лоток', '', (C[0] - 5000, C[1] - 6500), (C[0] + 9400 * math.cos(math.radians(-130)), C[1] + 9400 * math.sin(math.radians(-130))))
    L.note('Км-1', '', (C[0] + 1700, C[1] - 2900), (C[0] + 550 * math.cos(math.radians(-50)), C[1] + 550 * math.sin(math.radians(-50))))
    L.note('Пм-1', '', D.uv(C, 17000, 2000), D.uv(C, D.U0 + 2600, 1800))
    L.mtext('+2,300', C[0] - 10700, C[1] + 2600, 250, att=5, layer=L.L_DIM, rot=math.pi / 2)
    L.mtext('+2,800', *D.uv(C, D.U0 + 1800, -1600), 250, att=5, layer=L.L_DIM)
    sh.notes([N0, 'Стальная лестница и перила из нержавеющей стали - по разделу ТХ, в комплект КЖ не входят.'])
    return sh


def b23():
    sh = L.Sheet('2.3', 'Разрезы 1-1, 2-2, 3-3')
    cx, y0 = sh.X0 + 29700, sh.Y0 + 34500
    L.title('Разрез 1-1', cx, sh.Y0 + 40700)
    S = D.tank_section(cx, y0)
    yd = y0 + Z_B3 - 1700
    L.chain_h([cx + v for v in (-R_OUT, -R_WO, -R_HT, -R_PT, -R_PB, 0, R_PB, R_PT, R_HT, R_WO, R_OUT)], y0 + Z_B3 - 250, yd)
    L.dim((cx - R_OUT, y0 + Z_B3 - 250), (cx + R_OUT, y0 + Z_B3 - 250), (cx, yd - 700))
    yt = y0 + Z_TOPW + 1000
    L.chain_h([cx + v for v in (-11000, -R_WO, 0, R_WO, 11000)], y0 + Z_TOPW + 200, yt)
    L.dim((cx - R_WO, y0 + Z_TOPW + 200), (cx - R_WI, y0 + Z_TOPW + 200), (cx, yt - 500)); L.dim((cx + R_WI, y0 + Z_TOPW + 200), (cx + R_WO, y0 + Z_TOPW + 200), (cx, yt - 500))
    L.lev(Z_TOPW, S(-11000, Z_TOPW), 'L', ext=1500); L.lev(Z_FL, S(-R_OUT, Z_FL), 'L', ext=1650); L.lev(Z_B3, S(-R_B3, Z_B3), 'L', ext=R_OUT - R_B3 + 1650)
    L.lev(1250, S(-9500, 1250), 'R', ext=900); L.lev(1750, S(9300, 1750), 'L', ext=900)
    L.lev(Z_PB, S(-R_PB + 60, Z_PB), 'R', ext=250)
    xr = cx + 11000 + 900
    L.chain_v([y0 + v for v in (Z_BOT, Z_FL, 1250, Z_TOPW)], cx + 11000 + 150, xr)
    L.dim((cx + 11000 + 150, y0 + Z_FL), (cx + 11000 + 150, y0 + Z_TOPW), (xr + 700, y0), math.pi / 2)
    L.lev(Z_BOT, S(R_OUT, Z_BOT), 'R', ext=3300)
    for sg in (1, -1):
        rm = 5600; a = math.atan2((Z_HT - Z_PT), (R_HT - R_PT)) * sg
        L.mtext('i=1:12', cx + sg * rm, y0 + z_top(rm) + 330, 250, att=8, layer=L.L_DIM, rot=a)
    L.note('Бетон заполнения', 'С12/15', S(3300, -3000), S(1100, -3500))
    L.note('Км-1', '', S(2200, 500), S(700, 0)); L.note('Лоток', '', S(-7600, 400), S(-9400, 1100)); L.note('Консоль 650х120', '', S(-13600, 1200), S(-10700, 2200))
    L.note('Подготовка из бетона С8/10', 'толщиной 100 мм', S(-6500, -4300), S(-6000, z_bot(6000) - 60))
    # ---------- Разрез 2-2 (камера көлденең, резервуар жиегімен) ----------
    k = 1.0; x2, y2 = sh.X0 + 14500, sh.Y0 + 14500      # u=U0 → x2; z=0 → y2
    L.title('Разрез 2-2', x2 + 500, sh.Y0 + 21000)
    def T(u, z): return (x2 + (u - D.U0), y2 + z)
    # резервуар жиегі
    ed = [T(9300, z_top(9300)), T(R_HT, Z_HT), T(R_WI, Z_JOINT), T(R_WI, Z_TOPW), T(11000, Z_TOPW), T(11000, Z_TOPW - 120), T(R_WO, Z_TOPW - 120), T(R_WO, Z_FL), T(R_OUT, Z_FL), T(R_OUT, Z_BOT), T(R_B1, Z_B1), T(9300, z_bot(9300))]
    L.pl(ed); L.hatch([ed]); L.brk(T(9300, z_top(9300) + 200), T(9300, z_bot(9300) - 300))
    lt = [T(R_WI, 1050), T(9300, 1050), T(9300, 1750), T(9500, 1750), T(9500, 1250), T(R_WI, 1250)]; L.pl(lt); L.hatch([lt])
    cam = [T(D.U0, -2700), T(D.U0 + 4100, -2700), T(D.U0 + 4100, -2200), T(D.U0 + 3600, -2200), T(D.U0 + 3600, 2800), T(D.U0, 2800)]
    inner = [T(D.U0 + 300, -2200), T(D.U0 + 3300, -2200), T(D.U0 + 3300, 2600), T(D.U0 + 300, 2600)]
    L.pl(cam, closed=True); L.pl(inner, closed=True); L.hatch([cam, inner])
    L.pl([T(D.U0, -2700), T(D.U0, -2800), T(D.U0 + 4200, -2800), T(D.U0 + 4200, -2700)], layer=L.L_THIN)
    L.hatch([[T(D.U0, -2700), T(D.U0, -2800), T(D.U0 + 4200, -2800), T(D.U0 + 4200, -2700)]], pat='AR-CONC', sc=2)
    L.pl([T(R_OUT, Z_BOT), T(R_POD, Z_BOT), T(R_POD, Z_BOT - 100), T(9300, z_bot(9300) - 100)], layer=L.L_THIN)
    L.line(T(D.U0 + 4100, -2200), T(D.U0 + 6500, -2200), layer=L.L_THIN)
    L.chain_h([x2 + v for v in (0, 300, 3300, 3600)], y2 - 2950, y2 - 3600)
    L.dim((x2 + 3600, y2 - 2950), (x2 + 4100, y2 - 2950), (x2, y2 - 4250))
    L.dim((x2 - 35, y2 - 2950), (x2, y2 - 2950), (x2, y2 - 4250))
    xr = x2 + 4100 + 1000
    L.chain_v([y2 + v for v in (-2700, -2200, 2600, 2800)], x2 + 4250, xr)
    L.lev(2800, T(D.U0 + 3600, 2800), 'R', ext=3300); L.lev(-2200, T(D.U0 + 4100, -2200), 'R', ext=2800); L.lev(-2700, T(D.U0 + 4100, -2700), 'R', ext=2800)
    L.lev(Z_TOPW, T(R_WI, Z_TOPW), 'L', ext=2300); L.lev(Z_FL, T(9300, Z_FL), 'L', ext=1600)
    L.note('Деформационный шов 35 мм', '', T(11600, 4000), T(11018, 1200))
    L.note('Ур. земли', '', T(D.U0 + 5200, -900), T(D.U0 + 5000, -2200))
    L.note('Пм-1', '', T(D.U0 + 1900, 3700), T(D.U0 + 1500, 2700)); L.note('См-2', '', T(D.U0 + 1700, 500), T(D.U0 + 3450, 0)); L.note('Фм-2', '', T(D.U0 + 1900, -1500), T(D.U0 + 1500, -2450))
    # ---------- Разрез 3-3 (камера бойлық) ----------
    x3, y3 = sh.X0 + 39500, sh.Y0 + 14500
    L.title('Разрез 3-3', x3, sh.Y0 + 21000)
    def W(v, z): return (x3 + v, y3 + z)
    cam = [W(-3800, -2700), W(3800, -2700), W(3800, -2200), W(3300, -2200), W(3300, 2800), W(-3300, 2800), W(-3300, -2200), W(-3800, -2200)]
    c1 = [W(-3000, -2200), W(-150, -2200), W(-150, 2600), W(-3000, 2600)]; c2 = [W(150, -2200), W(3000, -2200), W(3000, 2600), W(150, 2600)]
    L.pl(cam, closed=True); L.pl(c1, closed=True); L.pl(c2, closed=True); L.hatch([cam, c1, c2])
    pd = [W(-3900, -2700), W(-3900, -2800), W(3900, -2800), W(3900, -2700)]; L.pl(pd, layer=L.L_THIN); L.hatch([pd], pat='AR-CONC', sc=2)
    L.chain_h([x3 + v for v in (-3300, -3000, -150, 150, 3000, 3300)], y3 - 2950, y3 - 3600)
    L.chain_h([x3 + v for v in (-3800, -3300, 3300, 3800)], y3 - 2950, y3 - 4250)
    L.dim((x3 - 3800, y3 - 2950), (x3 + 3800, y3 - 2950), (x3, y3 - 4900))
    L.chain_v([y3 + v for v in (-2700, -2200, 2600, 2800)], x3 + 3950, x3 + 4700)
    L.lev(2800, W(3300, 2800), 'R', ext=3600); L.lev(-2200, W(3800, -2200), 'R', ext=3100); L.lev(-2700, W(-3800, -2700), 'L', ext=1500); L.lev(2600, W(-3300, 2600), 'L', ext=2000)
    sh.notes([N0, 'Данный лист читать совместно с л. 2.1, 2.2.', 'Отверстия, гильзы и закладные детали уточнить по разделу ТХ.'])
    return sh


B = {'1.3': b13, '2.1': b21, '2.2': b22, '2.3': b23}
if __name__ == '__main__':
    import s1_run
    for n in sys.argv[1].split(','): s1_run.go(B[n], 'p' + n.replace('.', ''), dpi=100)
