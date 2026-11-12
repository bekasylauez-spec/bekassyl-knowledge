# -*- coding: utf-8 -*-
"""Лист 3.4: Схема расположения выпусков из фундамента. A2, М 1:50 (аналог an09).
План: Вп1 (П-шпилька, ноги r 5049 / r 5251, 324 шт.), выпуски колонны Км-1 (r 500 - 32, r 300 - 19);
Фрагмент 1 (без увеличения), А-А (стена + край днища, Вп1 на всю высоту), выпуск колонны,
Ведомость деталей, Спецификация Вп1, Ведомость расхода стали. Сандар s4_qty.json-нан."""
import math, json
import s4_lib as L
from s4_lib import op, pl, dim, hatch, section, Sheet
from s4_geo import *
import s4_draw as D
SC = 50
X0, Y0 = 309300.0, -300000.0
W, H = 29700.0, 21000.0
Q = json.load(open(r'D:\_claude_work\otst\s4\s4_qty.json', encoding='utf-8'))
VP = Q['elements']['Вп1']['rows'][0]
NV = int(VP['qty'])                                         # 324
KM2 = [r for r in Q['elements']['Км-1']['rows'] if r['pos'] == '2'][0]
NKO, NKI = 32, 19                                           # ШЕШІМДЕР: r 500 - 32, r 300 - 19 (= Км-1 поз.2, 51 шт.)
assert NKO + NKI == int(KM2['qty'])
op(t='ltload', names=['CENTER2', 'HIDDEN2'])
op(t='eraseregion', win=[X0 - 10, Y0 - 10, X0 + W + 10, Y0 + H + 10])
sh = Sheet('3.4', 'Схема расположения выпусков из фундамента', None, X0, Y0, 'A2', SC)
T = L.L_THIN; C = L.L_CONT; V = math.pi / 2
B18 = 'диам18'
AX = dict(layer=T, ltype='CENTER2', ltscale=20)
RVI, RVO = R_IN + 49.0, R_OUT - 49.0                        # 5049 / 5251
ZBB = Z_FBOT + 50 + 36                                      # низ П-шпильки: на верху нижней сетки днища (-2914)
LV, BV = 4450.0, 220.0


def dot(x, y, r=30.0, layer=B18):
    D.circ(x, y, r, layer); hatch([D.circle_pts(x, y, r, 16)], pat='SOLID', layer=layer)


def note(l1, l2, o, t, arrow='none'):
    return D.note(l1, l2, o, t, sc=SC, arrow=arrow)


# ======================= план =======================
cx, cy = X0 + 7700.0, Y0 + 10400.0
sh.text(L.title_u('Схема расположения выпусков из фундамента'), cx, cy + R_FM + 1250, 175, att=8, layer='0')
for r in (R_FM, R_OUT, R_IN, R_COL, R_HOLE, R_SUMP_T, R_SUMP_B): D.circ(cx, cy, r, T)
pl([(cx - R_FM - 500, cy), (cx + R_FM + 500, cy)], **AX)
pl([(cx, cy - R_FM - 500), (cx, cy + R_FM + 500)], **AX)
for i in range(NV):
    a = 2 * math.pi * i / NV
    for r in (RVI, RVO): dot(cx + r * math.cos(a), cy + r * math.sin(a))
for r, n in ((500.0, NKO), (300.0, NKI)):
    for i in range(n):
        a = 2 * math.pi * i / n
        dot(cx + r * math.cos(a), cy + r * math.sin(a), 20.0)
a = math.radians(20); note('Вп1', 'ш.100', (cx + 6600, cy + 2900), (cx + RVO * math.cos(a), cy + RVO * math.sin(a)))
a = math.radians(-35); note('2 (Км-1)', 'ш.100', (cx + 2200, cy - 1700), (cx + 520 * math.cos(a), cy + 520 * math.sin(a)))
for r, ang, o in ((R_FM, 128, (-4300, 6300)), (R_OUT, 142, (-5100, 5700)), (R_IN, 156, (-5800, 5100))):
    b = math.radians(ang); t = (cx + r * math.cos(b), cy + r * math.sin(b))
    note('%%c' + str(int(round(2 * r))), '', (cx + o[0], cy + o[1]), t, arrow='arrow')
# Фрагмент 1 (окружность) и разрез А-А (через стену на 90°)
fa = math.radians(45); fr = (cx + 5150 * math.cos(fa), cy + 5150 * math.sin(fa))
D.circ(fr[0], fr[1], 900.0, T)
note('Фрагмент 1', '', (fr[0] + 1500, fr[1] + 1100), (fr[0] + 900 * math.cos(math.radians(40)), fr[1] + 900 * math.sin(math.radians(40))))
section('А', (cx - 400, cy + R_IN - 700), (cx - 400, cy + R_FM + 700), sc=SC)

# ======================= Фрагмент 1 =======================
gx, gy = X0 + 16700.0, Y0 + 15000.0                   # точка (0, 5150) плана -> (gx, gy)
F = lambda x, y: (gx + x, gy + (y - 5150.0))
sh.text(L.title_u('Фрагмент 1'), gx, gy + 1900, 175, att=8, layer='0')
A0, A1 = 90.0 - 11.0, 90.0 + 11.0
for r in (R_IN, R_OUT):
    pl([F(*p) for p in D.circle_pts(0, 0, r, 40, A0, A1)], layer=T)
for a in (A0, A1):
    b = math.radians(a)
    p0 = F((R_IN - 150) * math.cos(b), (R_IN - 150) * math.sin(b)); p1 = F((R_OUT + 150) * math.cos(b), (R_OUT + 150) * math.sin(b))
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2; ux, uy = math.cos(b), math.sin(b); vx, vy = -uy, ux
    pl([p0, (mx - 40 * ux, my - 40 * uy), (mx - 15 * ux + 60 * vx, my - 15 * uy + 60 * vy), (mx + 15 * ux - 60 * vx, my + 15 * uy - 60 * vy), (mx + 40 * ux, my + 40 * uy), p1], layer=T)
ka = [i for i in range(NV) if A0 + 0.3 < 360.0 * i / NV < A1 - 0.3]
for i in ka:
    b = 2 * math.pi * i / NV
    for r in (RVI, RVO): dot(*F(r * math.cos(b), r * math.sin(b)))
# размеры: шаг 100 (по оси стены), 40 / 220 / 40
i0 = ka[len(ka) // 2]; b0, b1 = 2 * math.pi * i0 / NV, 2 * math.pi * (i0 + 1) / NV
q0 = F(RVO * math.cos(b0), RVO * math.sin(b0)); q1 = F(RVO * math.cos(b1), RVO * math.sin(b1))
dim(q0, q1, (q0[0], q0[1] + 600), math.atan2(q1[1] - q0[1], q1[0] - q0[0]), SC, txt='100', tx=((q0[0] + q1[0]) / 2 - 260, q0[1] + 600 + 110))
i2 = ka[2]; b2 = 2 * math.pi * i2 / NV
rad = [R_IN, R_IN + 40, R_OUT - 40, R_OUT]
bm = math.radians(A1 - 0.5)                         # у края фрагмента (за разрывом)
ux, uy = math.cos(bm), math.sin(bm)
pts = [F(r * ux, r * uy) for r in rad]
rot = math.atan2(uy, ux); vx_, vy_ = -uy, ux; OFF = 600.0
dl = F(R_IN * ux + OFF * vx_, R_IN * uy + OFF * vy_)
for j in range(3):
    tx = None
    if j != 1:
        rr = (R_IN - 300) if j == 0 else (R_OUT + 300)
        tx = F(rr * ux + (OFF + 110) * vx_, rr * uy + (OFF + 110) * vy_)
    dim(pts[j], pts[j + 1], dl, rot, SC, tx=tx)
note('Вп1', 'ш.100', F(1500, 5150 + 900), F(RVO * math.cos(math.radians(85)), RVO * math.sin(math.radians(85))))

# ======================= А-А =======================
OX, zy = X0 + 21300.0, Y0 + 13900.0
P = lambda r, z: (OX + (r - 5150.0), zy + z)
sh.text(L.title_u('А-А'), OX, zy + Z_TOP + 1150, 175, att=8, layer='0')
RL = 4200.0
CUT = (RL, -3300.0, 6400.0, 2000.0)
g = D.clip_geom(D.section_geom(dict(), dict()), *CUT)
D.draw_section(P, g, hatch_conc=False, cont=T, cut=CUT)
zt_ = lambda r: Z_F15 + (r - R_SUMP_T) / 12.0
kb = (Z_FBOT - Z_B2) / (R_BOT1 - R_BOT2)
D.break_line(P, RL, Z_B2 + (RL - R_BOT2) * kb, zt_(RL))
pod = [(RL, Z_FBOT - 100 - (R_BOT1 - RL) * 0), (R_POD, Z_FBOT - 100), (R_POD, Z_FBOT), (R_BOT1, Z_FBOT), (RL, Z_B2 + (RL - R_BOT2) * kb)]
from shapely.geometry import Polygon, box
pq = Polygon(D.podg_loop(1)).intersection(box(RL, -4000, 6100, -2900))
pq = [P(x, z) for x, z in list(pq.exterior.coords)[:-1]]
pl(pq, layer=T, closed=True); hatch([pq], pat='AR-CONC', sc=0.4, layer=D.HL)
# Вп1: П-шпилька 4450 + 220 + 4450
pl([P(RVI, ZBB + LV), P(RVI, ZBB + 9), P(RVI + 9, ZBB), P(RVO - 9, ZBB), P(RVO, ZBB + 9), P(RVO, ZBB + LV)], layer=B18)
note('Вп1', 'ш.100', P(3900, -800), P(RVI, -1300))
# размеры А-А
xd = 6400.0 + 500
dim(P(RVO, ZBB), P(RVO, ZBB + LV), P(xd, ZBB), V, SC)
dim(P(RVI - 9, ZBB), P(RVO + 9, ZBB), P(RVI, Z_FBOT - 500), 0.0, SC, tx=P(5150, Z_FBOT - 500 + 110))
dim(P(R_IN, Z_TOP), P(R_IN + 40, Z_TOP), P(R_IN, Z_TOP + 450), 0.0, SC, tx=P(R_IN - 260, Z_TOP + 450 + 110))
dim(P(R_IN + 40, Z_TOP), P(R_OUT - 40, Z_TOP), P(R_IN, Z_TOP + 450), 0.0, SC, tx=P(5150, Z_TOP + 450 + 110))
dim(P(R_OUT - 40, Z_TOP), P(R_OUT, Z_TOP), P(R_IN, Z_TOP + 450), 0.0, SC, tx=P(R_OUT + 260, Z_TOP + 450 + 110))
for z, x_, side, ext in ((Z_TOP, D.R_CON, 'R', 300), (Z_WBOT, R_FM, 'R', 950), (Z_FBOT, R_FM, 'R', 950)):
    D.lev2(z, P(x_, z), SC, side=side, ext=ext)

# ======================= выпуски колонны Км-1 =======================
kx, ky = X0 + 26700.0, Y0 + 13000.0
K = lambda r, z: (kx + r, ky + (z - Z_SUMP))
sh.text(L.title_u('Выпуски в колонну Км-1'), kx, K(0, -1900)[1] + 600, 175, att=8, layer='0')
# контур плиты приямка (тонко) r -1100…1100, -4.293…-3.512, гнездо r 250 до -3.793; колонна над -3.512
RK = 1100.0
pl([K(-RK, Z_SUMP), K(-R_HOLE, Z_SUMP), K(-R_HOLE, Z_HOLE), K(R_HOLE, Z_HOLE), K(R_HOLE, Z_SUMP), K(RK, Z_SUMP)], layer=T)
pl([K(-RK, Z_SBOT), K(RK, Z_SBOT)], layer=T)
for s in (1, -1):
    D.break_line(K, s * RK, Z_SBOT, Z_SUMP)
    pl([K(s * R_COLB, Z_SUMP), K(s * R_COL, Z_COLB), K(s * R_COL, -1900)], layer=T)
    pl([K(s * R_HOLE, Z_SUMP), K(s * R_HOLE, -1900)], layer=T)
    for x0_, x1_ in ((R_HOLE, R_COL),):
        xm = s * (x0_ + x1_) / 2
        pl([K(s * x0_ - s * 60, -1900), K(xm - 30, -1900), K(xm - 10, -1850), K(xm + 10, -1950), K(xm + 30, -1900), K(s * x1_ + s * 60, -1900)], layer=T)
ZF = Z_SUMP - 600.0; ZTOPB = Z_SUMP + 1280.0
for s in (1, -1):
    for r in (500.0, 300.0):
        pl([K(s * r, ZTOPB), K(s * r, ZF + 9), K(s * (r + 9), ZF), K(s * (r + 300), ZF)], layer=B18)
pl([K(0, Z_SBOT - 300), K(0, -1700)], **AX)
note('2 (Км-1)', 'ш.100', K(-1500, -2700), K(-500, -2900))
dim(K(500, ZF), K(500, Z_SUMP), K(RK + 400, ZF), V, SC)
dim(K(500, Z_SUMP), K(500, ZTOPB), K(RK + 400, ZF), V, SC)
dim(K(500, ZF), K(800, ZF), K(500, Z_SBOT - 400), 0.0, SC)

# ======================= Ведомость деталей =======================
vx, vy = X0 + 1500.0, Y0 + 4300.0
cw = [1500.0, 5000.0]
sh.text('Ведомость деталей', vx + sum(cw) / 2, vy + 250, 175, att=8, layer='0')
yb = D.table(vx, vy, cw, [['Вп1', ''], ['2 (Км-1)', '']], hdr_h=600, row_h=1100, hdr=['Поз.', 'Эскиз'])
# Вп1: П (не в масштабе)
ex, ey = vx + cw[0] + 1000, vy - 600 - 550
pl([(ex + 3000, ey + 220), (ex, ey + 220), (ex, ey - 220), (ex + 3000, ey - 220)], layer=B18)
sh.text(D.fnum(LV), ex + 1500, ey + 220 + 60, 125, att=8, layer=L.L_TXT)
sh.text(D.fnum(LV), ex + 1500, ey - 220 + 60, 125, att=8, layer=L.L_TXT)
sh.text(D.fnum(BV), ex - 80, ey, 125, att=6, layer=L.L_TXT, rot=0)
# поз.2 Км-1: Г 1880 + 300
ex2, ey2 = vx + cw[0] + 1200, vy - 600 - 1100 - 550
pl([(ex2 + 3000, ey2 + 150), (ex2, ey2 + 150), (ex2, ey2 - 250)], layer=B18)
sh.text(D.fnum(600 + 1280), ex2 + 1500, ey2 + 150 + 60, 125, att=8, layer=L.L_TXT)
sh.text('300', ex2 - 80, ey2 - 50, 125, att=6, layer=L.L_TXT)

# ======================= Спецификация элементов =======================
colw = [w * SC for w in (15, 60, 65, 10, 15, 20)]
tx0, ty0 = X0 + W - 250 - 250 - sum(colw), Y0 + 10000.0
sh.text('Спецификация элементов', tx0 + sum(colw) / 2, ty0 + 250, 175, att=8, layer='0')
D.table(tx0, ty0, colw, [['', '', 'Выпуск Вп1', '1', '', ''], D.spec_row(VP)], hdr_h=750, row_h=450,
        hdr=['Поз.', 'Обозначение', 'Наименование', 'Кол.', 'Масса ед., кг', 'Примечание'])
# ======================= Ведомость расхода стали =======================
SV = Q['steel']['Вп1']
mw = 2500.0; tw = mw + 2 * 800 + 1000
gx2, gy2 = X0 + W - 250 - 250 - tw, Y0 + 7700.0
sh.text('Ведомость расхода стали на элемент, кг', gx2 + tw / 2, gy2 + 250, 175, att=8, layer='0')
D.steel_table(gx2, gy2, mw, [('А500С', [18])], [('Выпуск Вп1', {18: SV['Ø18 А500С']}, {'А500С': SV['Ø18 А500С']}, SV['Итого'])],
              gost='ГОСТ 34028-2016 (214-210-0502)')
# ======================= примечания =======================
sh.notes(['Общие указания см. л. 1.1.',
          'Стыки рабочей арматуры внахлестку без сварки, на скрутках из вязальной проволоки не менее 3 шт. на стык. Длина нахлеста 71d. Стыки располагать вразбежку, чтобы площадь рабочей арматуры, стыкуемой в одном сечении, не превышала 50%.',
          'Расход арматуры в погонных метрах приведен с учетом нахлеста.',
          'Стержни, указанные в "Ведомости деталей", должны гнуться механическим способом в холодном состоянии с радиусом гиба 3d - 5d, где d - диаметр стержня.'], w=9250)
L.dump(r'D:\_claude_work\otst\s4\ops\s34.json')
if __name__ == '__main__':
    import s4_ab
    print(s4_ab.run(L.OPS, 's34')); lg = s4_ab.log()
    print("\n".join(l[:200] for l in lg.splitlines() if l.startswith(('ERR', 'done', 'no ', 'GUARD'))))
