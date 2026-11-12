# -*- coding: utf-8 -*-
"""Лист 2.3: Разрез 1-1; 2-2. М 1:50, A2 (аналог an05).
1-1 — по горизонтальной оси (слева 180°: труба Ø350 и углублённый лоток, колонна — через тиреу 0°/180°);
2-2 — по вертикальной оси (стрелки влево: справа 90°; колонна — через окна 90°/270°)."""
import math
import s4_lib as L
from s4_lib import op, pl, dim, hatch, lev, note, Sheet
from s4_geo import *
import s4_draw as D
SC = 50
X0, Y0 = 190500.0, -300000.0
W, H = 29700.0, 21000.0
op(t='ltload', names=['CENTER2'])
op(t='eraseregion', win=[X0 - 10, Y0 - 10, X0 + W + 10, Y0 + H + 10])
sh = Sheet('2.3', 'Разрез 1-1; 2-2', None, X0, Y0, 'A2', SC)
T = L.L_THIN; C = L.L_CONT; V = math.pi / 2
SX = X0 + 12300.0


def lev_up(zy, P, x, z, dz, right=True):
    """отметка с выноской вверх (полка над элементом)"""
    t = lev(zy, P(x, z), SC, side='L', ext=0)
    a = P(x, z + dz); b = (a[0] + (627 if right else -627), a[1] + 300)
    op(t='sp_set', h=t, pts=[[2, a[0], a[1]], [1, a[0] - 627, a[1] + 300]])


def section_sheet(name, zy, left, right, piles_axis, pile_sign, full_levels):
    sx = SX
    P = lambda x, z: (sx + x, zy + z)
    sh.text(L.title_u(name), sx, zy + 2950, 175, att=8, layer='0')
    g = D.section_geom(left, right)
    # подушка (грунт) и подготовка
    for s in (1, -1):
        cl = [P(x, z) for x, z in D.cushion_loop(s)]
        pl(cl, layer=T, closed=True)
        hatch([cl], pat='EARTH', sc=20, layer=D.HL)
        pp = [P(x, z) for x, z in D.podg_loop(s)]
        pl(pp, layer=T, closed=True)
        hatch([pp], pat='AR-CONC', sc=0.4, layer=D.HL)
    D.draw_section(P, g)
    # сваи
    piles = D.piles_in_section(piles_axis)
    for s_, r in piles:
        D.pile(P, pile_sign * s_, D.pile_top(r), length=500)
    # ось
    pl([P(0, D.Z_CUSH_PIT - 800), P(0, Z_TOP + 350)], layer=T, ltype='CENTER2', ltscale=20)
    # уровень воды
    for s in (1, -1):
        pl([P(s * D.R_PLATE, D.Z_WATER), P(s * D.R_LT_I, D.Z_WATER)], layer=T)
    # уклон днища
    for s in (1, -1):
        r0, r1 = 3900.0, 2500.0; zf = lambda r: Z_F15 + (r - R_SUMP_T) / 12.0
        pl([P(s * r0, zf(r0) + 230), P(s * r1, zf(r1) + 230)], layer=T)
        pl([P(s * (r1 + 160), zf(r1 + 160) + 262), P(s * r1, zf(r1) + 230), P(s * (r1 + 165), zf(r1 + 165) + 212)], layer=T)
        sh.text('i=1:12', sx + s * 3200, zy + zf(3200) + 300, 125, att=8, layer=L.L_DIM, rot=math.atan(1 / 12.0) * s)
    # труба (снаружи стены) — 1-1 слева
    if left.get('pipe'):
        for dz in (-D.D_PIPE / 2, D.D_PIPE / 2):
            pl([P(-R_OUT, D.Z_PIPE + dz), P(-R_OUT - D.PIPE_OUT, D.Z_PIPE + dz)], layer=T)
        pl([P(-R_OUT - D.PIPE_OUT, D.Z_PIPE - D.D_PIPE / 2), P(-R_OUT - D.PIPE_OUT, D.Z_PIPE + D.D_PIPE / 2)], layer=T)
        pl([P(-R_IN + 150, D.Z_PIPE), P(-R_OUT - D.PIPE_OUT - 250, D.Z_PIPE)], layer=T, ltype='CENTER2', ltscale=10)
    # ---- размеры: верх ----
    zt = Z_TOP
    xa = [-D.R_CON, -R_OUT, -R_IN, -D.R_PLATE, 0, D.R_PLATE, R_IN, R_OUT, D.R_CON]
    for i in range(len(xa) - 1):
        dim(P(xa[i], zt), P(xa[i + 1], zt), (sx, zy + zt + 500), 0.0, SC)
    xb = [-D.R_CON, -R_OUT, -R_IN, R_IN, R_OUT, D.R_CON]
    for i in range(len(xb) - 1):
        dim(P(xb[i], zt), P(xb[i + 1], zt), (sx, zy + zt + 900), 0.0, SC)
    # ---- размеры: низ (только 1-1) ----
    if full_levels:
        xs = [-R_FM, -R_OUT, -R_IN, -R_BOT2, -R_BOT3, 0, R_BOT3, R_BOT2, R_IN, R_OUT, R_FM]
        tx = [None, None, '3156', None, None, None, None, '3156', None, None]
        zs = [Z_FBOT, Z_FBOT, Z_FBOT, Z_B2, Z_SBOT, Z_SBOT, Z_SBOT, Z_B2, Z_FBOT, Z_FBOT, Z_FBOT]
        for i in range(len(xs) - 1):
            dim(P(xs[i], zs[i]), P(xs[i + 1], zs[i + 1]), (sx, zy - 6250), 0.0, SC, txt=tx[i])
    # ---- размеры: вертикальные снаружи справа ----
    xr1, xr2 = D.R_CUSH + 400, D.R_CUSH + 850
    ch1 = [(D.R_CUSH, D.Z_CUSH), (R_POD, Z_FBOT - 100), (R_FM, Z_FBOT), (R_FM, Z_WBOT), (R_OUT, D.Z_CON_ROOT), (D.R_CON, Z_TOP)]
    for (r0, z0), (r1, z1) in zip(ch1[:-1], ch1[1:]):
        tx = P(xr1 + 220, (z0 + z1) / 2) if abs(z1 - z0) < 200 else None    # короткий размер — между цепочками
        dim(P(r0, z0), P(r1, z1), P(xr1, z0), V, SC, tx=tx)
    for (r0, z0), (r1, z1) in (((R_FM, Z_FBOT), (R_FM, Z_WBOT)), ((R_FM, Z_WBOT), (D.R_CON, Z_TOP))):
        dim(P(r0, z0), P(r1, z1), P(xr2, z0), V, SC)
    # лоток (в канале, справа — обычный)
    xl = (R_IN + D.R_LT_O) / 2
    chl = [(D.R_LT_I, D.Z_LT_N[0]), (D.R_LT_O, D.Z_LT_N[1]), (D.R_LT_O, D.Z_LT_TOP), (R_IN, Z_TOP)]
    for (r0, z0), (r1, z1) in zip(chl[:-1], chl[1:]):
        dim(P(r0, z0), P(r1, z1), P(xl, z0), V, SC, tx=P(xl + 2, z0 - 250) if z1 - z0 < 200 else None)
    if left.get('deep'):
        chd = [(-D.R_LT_I, D.Z_LT_D[0]), (-D.R_LT_O, D.Z_LT_D[1]), (-D.R_LT_O, D.Z_LT_TOP), (-R_IN, Z_TOP)]
        for (r0, z0), (r1, z1) in zip(chd[:-1], chd[1:]):
            dim(P(r0, z0), P(r1, z1), P(-xl, z0), V, SC, tx=P(-xl + 2, z0 - 250) if z1 - z0 < 200 else None)
    # приямок 720 / 781 (слева, между конусом колонны и стенкой приямка)
    for z0, z1 in ((Z_SBOT, Z_SUMP), (Z_SUMP, Z_F15)):
        dim(P(-950, z0), P(-950, z1), P(-950, z0), V, SC)
    # ---- отметки ----
    xm = D.R_CUSH + 600                  # слева снаружи: точка знака
    lev(zy, P(-D.R_CON, Z_TOP), SC, side='L', ext=xm - D.R_CON)
    lev(zy, P(-R_FM, Z_WBOT), SC, side='L', ext=xm - R_FM)
    lev(zy, P(-R_FM, Z_FBOT), SC, side='L', ext=xm - R_FM)
    lev(zy, P(-D.R_CUSH, D.Z_CUSH), SC, side='L', ext=xm - D.R_CUSH)
    if left.get('pipe'):
        lev(zy, P(-R_OUT - D.PIPE_OUT, D.Z_PIPE), SC, side='L', ext=xm - R_OUT - D.PIPE_OUT)
    if full_levels:
        lev(zy, P(-R_BOT3, Z_SBOT), SC, side='L', ext=xm + 900 - R_BOT3)
        lev(zy, P(-D.R_PIT_B, D.Z_CUSH_PIT), SC, side='L', ext=xm - D.R_PIT_B)
    # внутри
    lev(zy, P(2000, D.Z_WATER), SC, side='R', ext=0)
    lev(zy, P(D.R_LT_I, D.Z_LT_TOP), SC, side='L', ext=550)
    lev(zy, P(D.R_LT_O, D.Z_LT_N[1]), SC, side='L', ext=700)
    if left.get('deep'):
        lev(zy, P(-D.R_LT_O, D.Z_LT_D[1]), SC, side='R', ext=500)
    lev_up(zy, P, 950, Z_SUMP, 1050)
    return P


# ---- Разрез 1-1 (вверху) ----
P1 = section_sheet('Разрез 1-1', Y0 + 17075.0, dict(deep=1, pipe=1), dict(), 0.0, 1, True)
D.note('Отв. %%c350', '', P1(-6600, 950), P1(-5600, D.Z_PIPE + D.D_PIPE / 2), sc=SC, arrow='arrow')
# ---- Разрез 2-2 (внизу): справа 90°, окна колонны ----
P2 = section_sheet('Разрез 2-2', Y0 + 7100.0, dict(win=1), dict(win=1), 90.0, 1, False)
# выноски (2-2, внизу, в свободной зоне грунта)
D.note('Подушка из уплотненного суглинка', 't=1000 (Купл=0,95)', P2(-3300, -5000), P2(-2700, -3700), sc=SC, arrow='arrow')
D.note('Подготовка, бетон С8/10, t=100', '', P2(-2700, -5500), P2(-2200, -3290), sc=SC, arrow='arrow')
D.note('Раскатные сваи %%c500,', 'см. л. 1.3...1.5', P2(4300, -5300), P2(4894, -4450), sc=SC, arrow='arrow')
L.dump(r'D:\_claude_work\otst\s4\ops\s23.json')
if __name__ == '__main__':
    import s4_ab
    print(s4_ab.run(L.OPS, 's23')); lg = s4_ab.log()
    print("\n".join(l[:200] for l in lg.splitlines() if l.startswith(('ERR', 'done', 'no ', 'GUARD'))))
