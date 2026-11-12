# -*- coding: utf-8 -*-
"""Лист 3.2: Схема расположения основных арматур фундамента Фм-1. A2, М 1:50 (аналог an07).
Армирование парағы: бетон штрихталмайды, контур жіңішке, арматура қалың (диам18/диам12/диам16/диам8).
План: поз.1 шартты (әр бағытта 3 стержень + таралу аймағы), Ск1; «Армирование приямка» планы (поз.2-5);
«Разрез Б-Б» приямок қимасы; «Узел стыковки…»; «Разрез 1-1 (Армирование)» днище шеті."""
import math, json
import s4_lib as L
from s4_lib import op, pl, dim, hatch, section, Sheet
from s4_geo import *
import s4_draw as D
from shapely.geometry import Polygon, box
SC = 50
X0, Y0 = 249900.0, -300000.0
W, H = 29700.0, 21000.0
Q = json.load(open(r'D:\_claude_work\otst\s4\s4_qty.json', encoding='utf-8'))
ROWS = {r['pos']: r for r in Q['elements']['Фм-1']['rows']}
op(t='ltload', names=['CENTER2', 'HIDDEN2'])
op(t='eraseregion', win=[X0 - 10, Y0 - 10, X0 + W + 10, Y0 + H + 10])
sh = Sheet('3.2', 'Схема расположения основных арматур фундамента Фм-1', None, X0, Y0, 'A2', SC)
T = L.L_THIN; C = L.L_CONT; V = math.pi / 2
B18, B12, B16, B8 = 'диам18', 'диам12', 'диам16', 'диам8'
AX = dict(layer=T, ltype='CENTER2', ltscale=20)
RA = 5750.0                                   # граница армирования (защитный слой 50)
LAP = 1280.0


def bar(pts, layer=B18):
    pl(pts, layer=layer)


def dot(x, y, r=9.0, layer=B18):
    D.circ(x, y, r, layer); hatch([D.circle_pts(x, y, r, 16)], pat='SOLID', layer=layer)


def chord(c, r, k):
    return math.sqrt(max(0.0, r * r - k * k))


def note(l1, l2, o, t, arrow='none'):
    return D.note(l1, l2, o, t, sc=SC, arrow=arrow)


# ======================= план Фм-1 =======================
cx, cy = X0 + 7700.0, Y0 + 10400.0
sh.text(L.title_u('Схема расположения основных арматур фундамента Фм-1'), cx, cy + R_FM + 1250, 175, att=8, layer='0')
D.circ(cx, cy, R_FM, T)
for r in (R_OUT, R_IN, R_VUT): D.circ(cx, cy, r, T)
for r in (R_SUMP_T, R_SUMP_B): D.circ(cx, cy, r, T)
D.circ(cx, cy, R_BOT2, T, ltype='HIDDEN2', ltscale=10)
D.circ(cx, cy, R_HOLE, T)
pl([(cx - R_FM - 500, cy), (cx + R_FM + 500, cy)], **AX)
pl([(cx, cy - R_FM - 500), (cx, cy + R_FM + 500)], **AX)
# поз.1 — X направление (горизонтальные стержни): 3 стержня у низа плана
for k in (-3850.0, -3950.0, -4050.0):
    h = chord(0, RA, k); bar([(cx - h, cy + k), (cx + h, cy + k)])
# поз.1 — Y направление: 3 стержня справа
for k in (3850.0, 3950.0, 4050.0):
    h = chord(0, RA, k); bar([(cx + k, cy - h), (cx + k, cy + h)])
# зоны распределения (размерная линия) 100х115=11500
dim((cx, cy - RA), (cx, cy + RA), (cx - 2600, cy), V, SC, txt='100х115=11500', tx=(cx - 2600 - 110, cy - 1700))
dim((cx - RA, cy), (cx + RA, cy), (cx, cy + 2600), 0.0, SC, txt='100х115=11500', tx=(cx + 1800, cy + 2600 + 110))
note('1', 'ш.100', (cx - 1700, cy - 4950), (cx - 1300, cy - 4050))
note('1', 'ш.100', (cx + 4700, cy + 1300), (cx + 4050, cy + 800))
# Ск1 — радиальные П-скобы (в плане - отрезок 1280 от края)
for a in (135.0, 225.0):
    b = math.radians(a)
    bar([(cx + RA * math.cos(b), cy + RA * math.sin(b)), (cx + (RA - LAP) * math.cos(b), cy + (RA - LAP) * math.sin(b))])
b = math.radians(135.0); tp = (cx + (RA - 400) * math.cos(b), cy + (RA - 400) * math.sin(b))
note('Ск1', 'ш.100', (tp[0] - 900, tp[1] + 900), tp)
b = math.radians(225.0); tp = (cx + (RA - 400) * math.cos(b), cy + (RA - 400) * math.sin(b))
note('Ск1', 'ш.100', (tp[0] - 900, tp[1] - 700), tp)
a = math.radians(60); tp = (cx + R_FM * math.cos(a), cy + R_FM * math.sin(a))
note('%%c11600', '', (tp[0] + 800, tp[1] + 700), tp, arrow='arrow')
note('Армирование приямка', 'см. фрагмент', (cx - 2900, cy + 1300), (cx + R_SUMP_T * math.cos(math.radians(150)), cy + R_SUMP_T * math.sin(math.radians(150))), arrow='arrow')
section('1', (cx + R_FM + 600, cy - 1500), (cx + 4500, cy - 1500), sc=SC)

# ======================= Армирование приямка (план) =======================
px, py = X0 + 17800.0, Y0 + 16300.0
sh.text(L.title_u('Армирование приямка'), px, py + 2500, 175, att=8, layer='0')
for r in (R_SUMP_T, R_SUMP_B, R_HOLE): D.circ(px, py, r, T)
for r in (R_BOT2, R_BOT3): D.circ(px, py, r, T, ltype='HIDDEN2', ltscale=10)
pl([(px - 3300, py), (px + 3300, py)], **AX); pl([(px, py - 3300), (px, py + 3300)], **AX)
# поз.2 — сетка ш.100 (верх r<=1160 и низ r<=1370 в плане совпадают по осям стержней)
R2 = 1370.0
for i in range(-13, 14):
    k = i * 100.0
    h = chord(0, R2, k)
    if h < 50: continue
    bar([(px - h, py + k), (px + h, py + k)]); bar([(px + k, py - h), (px + k, py + h)])
# поз.3 (r 1500, 95 шт.) и поз.4 (r 1845, 116 шт.) — точками; 2 радиальных стержня каждого
for r, n in ((R_SUMP_T - 49, ROWS['3']['qty']), (R_BOT2 - 59, ROWS['4']['qty'])):
    for i in range(int(n)):
        a = 2 * math.pi * i / n
        dot(px + r * math.cos(a), py + r * math.sin(a), 30.0)
for a, r0, r1 in ((200.0, R_SUMP_B - 700, R_SUMP_T + LAP), (160.0, R_BOT3 - 700, R_BOT2 + LAP)):
    b = math.radians(a)
    bar([(px + r0 * math.cos(b), py + r0 * math.sin(b)), (px + r1 * math.cos(b), py + r1 * math.sin(b))])
# поз.5 — кольца (крайние кольца каждой группы)
for r in (R_SUMP_B + 67, R_SUMP_T - 67 - 18, R_BOT3 + 77, R_BOT2 - 77 - 18):
    D.circ(px, py, r, B18)
# выноски
note('2', 'ш.100', (px + 2300, py + 2200), (px + 650, py + 1050))
b = math.radians(200.0); note('3', 'ш.100', (px - 3000, py - 1700), (px + 2200 * math.cos(b), py + 2200 * math.sin(b)))
b = math.radians(160.0); note('4', 'ш.100', (px - 3000, py + 1900), (px + 2600 * math.cos(b), py + 2600 * math.sin(b)))
b = math.radians(-45.0); note('5', '', (px + 2600, py - 2400), (px + (R_BOT2 - 77) * math.cos(b), py + (R_BOT2 - 77) * math.sin(b)))
section('Б', (px + 3300, py), (px - 3300, py), sc=SC)
note('%%c3000', '', (px + 2500, py - 1100), (px + R_SUMP_T * math.cos(math.radians(-20)), py + R_SUMP_T * math.sin(math.radians(-20))), arrow='arrow')
note('%%c3689', '', (px + 2700, py - 1700), (px + R_BOT2 * math.cos(math.radians(-30)), py + R_BOT2 * math.sin(math.radians(-30))), arrow='arrow')

# ======================= Разрез Б-Б (приямок) =======================
sx, zy = X0 + 25300.0, Y0 + 18200.0 + 2550.0          # P(x,z): z — отметка*1000
P = lambda x, z: (sx + x, zy + z)
XC = 2300.0
sh.text(L.title_u('Б-Б'), sx, py + 2500, 175, att=8, layer='0')
fm = D._half(dict())[0][0]
from shapely import affinity
g = fm.union(affinity.scale(fm, -1, 1, origin=(0, 0))).intersection(box(-XC, -5000, XC, -2550))
cut = (-XC, -5000, XC, -2550)
D.draw_section(P, dict(polys=[g] if g.geom_type == 'Polygon' else list(g.geoms), joints=[], thin=[]), hatch_conc=False, cont=T, cut=cut)
for s in (1, -1):
    # колонна (контур, тонко) над приямком
    pl([P(s * R_HOLE, Z_SUMP), P(s * R_COLB, Z_SUMP), P(s * R_COL, Z_COLB), P(s * R_COL, -2700)], layer=T)
    pl([P(s * R_HOLE, Z_SUMP), P(s * R_HOLE, -2700)], layer=T)
pl([P(0, Z_SBOT - 300), P(0, -2600)], **AX)
for s in (1, -1):
    xm = s * XC
    zt = Z_F15 + (XC - R_SUMP_T) / 12.0; zb = Z_B2 + (XC - R_BOT2) * (Z_FBOT - Z_B2) / (R_BOT1 - R_BOT2)
    D.break_line(P, xm, zb, zt)
# арматура приямка (правая и левая половины)
nI = (720.0, -300.0); nI = (nI[0] / 780.4, nI[1] / 780.4)        # нормаль внутрь бетона к внутренней грани
dO = (R_BOT2 - R_BOT3, Z_B2 - Z_SBOT); lO = math.hypot(*dO); nO = (-dO[1] / lO, dO[0] / lO)   # нормаль внутрь бетона к наружной грани (вверх-внутрь)
ZT2 = Z_SUMP - 40 - 9; ZT2b = ZT2 - 18             # поз.2 верх: 2 слоя
ZB2 = Z_SBOT + 50 + 9; ZB2b = ZB2 + 18             # поз.2 низ
from shapely.geometry import LineString as _LS
def barc(s, pts, layer=B18):
    g_ = _LS(pts).intersection(box(-XC + 30, -9000, XC - 30, 0))
    for q in (list(g_.geoms) if hasattr(g_, 'geoms') else [g_]):
        if q.length > 1: bar([P(s * x, z) for x, z in q.coords], layer)
for s in (1, -1):
    S = lambda x, z: P(s * x, z)
    # поз.2 верх (разрыв у гнезда r 250) и низ
    bar([S(R_HOLE + 40, ZT2), S(1160, ZT2)])
    bar([S(0, ZB2), S(1370, ZB2)])
    for i in range(3, 12): dot(*S(i * 100.0 + 50, ZT2b))
    for i in range(0, 14): dot(*S(i * 100.0 + 50, ZB2b))
    # поз.3: нахлест 1280 по верху днища -> внутр. грань -> анкер 700 по дну (под верхней сеткой)
    z3 = ZT2b - 27
    a1 = (R_SUMP_B + 30, z3)
    top3 = (R_SUMP_T + LAP, Z_F15 + LAP / 12.0 - 49 - 36)
    barc(s, [top3, (R_SUMP_T + 45, Z_F15 - 49 - 36 + 0), (a1[0], z3), (a1[0] - 700, z3)])
    # поз.4: нахлест 1280 по низу днища -> наружн. грань -> анкер 700 по дну (над нижней сеткой)
    kb = (Z_FBOT - Z_B2) / (R_BOT1 - R_BOT2)
    z4 = ZB2b + 27
    b0 = (R_BOT2 + LAP, Z_B2 + LAP * kb + 59 + 36)
    b1 = (R_BOT2 - 40, Z_B2 + 59 + 36)
    b2 = (R_BOT3 + 40, z4)
    barc(s, [b0, b1, b2, (b2[0] - 700, z4)])
    # поз.1 днища (обрыв) верх/низ — стыкуются с поз.3/4
    bar([S(R_SUMP_T + 300, Z_F15 + 300 / 12.0 - 49), S(XC - 30, Z_F15 + (XC - 30 - R_SUMP_T) / 12.0 - 49)])
    bar([S(R_BOT2 + 300, Z_B2 + 300 * kb + 59), S(XC - 30, Z_B2 + (XC - 30 - R_BOT2) * kb + 59)])
    # поз.5 кольца (точки) по внутр. (8) и наружн. (11) граням — внутри от радиальных
    for i in range(8):
        t = (i + 0.5) / 8.0
        x = R_SUMP_T + (R_SUMP_B - R_SUMP_T) * t + nI[0] * 75; z = Z_F15 + (Z_SUMP - Z_F15) * t + nI[1] * 75 - 30
        dot(*S(x, z))
    for i in range(11):
        t = (i + 0.5) / 11.0
        x = R_BOT2 + (R_BOT3 - R_BOT2) * t + nO[0] * 0 - 85; z = Z_B2 + (Z_SBOT - Z_B2) * t + 85
        dot(*S(x, z))
    # Шп1 (2 шт. в сечении) — между гранями
    for t in (0.35, 0.7):
        xi = R_SUMP_T + (R_SUMP_B - R_SUMP_T) * t + 60; zi = Z_F15 + (Z_SUMP - Z_F15) * t - 40
        xo = R_BOT2 + (R_BOT3 - R_BOT2) * (t * 0.9) - 50; zo = Z_B2 + (Z_SBOT - Z_B2) * (t * 0.9) + 60
        bar([S(xi - 40, zi + 40), S(xi, zi), S(xo, zo), S(xo + 40, zo - 40)], layer=B8)
# выноски Б-Б
note('2', 'ш.100', P(-600, -3000), P(-700, ZT2))
note('2', 'ш.100', P(-600, Z_SBOT - 700), P(-400, ZB2))
note('3', 'ш.100', P(1300, -2350), P(1500 + 600, Z_F15 + 600 / 12.0 - 85))
note('4', 'ш.100', P(2500, Z_SBOT - 600), P(R_BOT2 + 700, Z_B2 + 700 * (Z_FBOT - Z_B2) / (R_BOT1 - R_BOT2) + 95))
note('5', '', P(-2500, -4300), P(-(R_BOT2 + (R_BOT3 - R_BOT2) * 0.5 - 85), Z_B2 + (Z_SBOT - Z_B2) * 0.5 + 85))
note('Шп1', 'ш.400х400', P(-2500, -2450), P(-1520, -3220))
note('1', '', P(2600, -2300), P(XC - 300, Z_F15 + (XC - 300 - R_SUMP_T) / 12.0 - 49))
# размеры Б-Б
dim(P(R_SUMP_B, Z_SUMP), P(R_SUMP_B, Z_SBOT), P(R_SUMP_B - 250, Z_SBOT), V, SC)
dim(P(-R_SUMP_T, Z_F15), P(R_SUMP_T, Z_F15), P(0, -2650), 0.0, SC)
dim(P(-R_BOT3, Z_SBOT), P(R_BOT3, Z_SBOT), P(0, Z_SBOT - 350), 0.0, SC)

# ======================= Разрез 1-1 (Армирование) =======================
ex, ez = X0 + 20500.0, Y0 + 14200.0        # P1(r, z)
P1 = lambda r, z: (ex + (r - 3600.0), ez + z)
RL, ZTOPC = 3600.0, -1500.0
sh.text(L.title_u('Разрез 1-1 (Армирование)'), P1(4800, 0)[0], P1(0, ZTOPC + 900)[1], 175, att=8, layer='0')
g1 = D.clip_geom(D.section_geom(dict(), dict()), RL, -3200.0, 6000.0, ZTOPC)
CUT1 = (RL, -3200.0, 6000.0, ZTOPC)
D.draw_section(P1, g1, hatch_conc=False, cont=T, cut=CUT1)
D.break_line(P1, RL, Z_B2 + (RL - R_BOT2) * (Z_FBOT - Z_B2) / (R_BOT1 - R_BOT2), Z_F15 + (RL - R_SUMP_T) / 12.0)
for x0_, x1_ in ((R_IN, R_OUT),):
    xm = (x0_ + x1_) / 2
    pl([P1(x0_ - 80, ZTOPC), P1(xm - 40, ZTOPC), P1(xm - 15, ZTOPC + 60), P1(xm + 15, ZTOPC - 60), P1(xm + 40, ZTOPC), P1(x1_ + 80, ZTOPC)], layer=T)
pod = Polygon(D.podg_loop(1)).intersection(box(RL, -4000, 6100, -2900))
pq = [P1(x, z) for x, z in list(pod.exterior.coords)[:-1]]
pl(pq, layer=T, closed=True); hatch([pq], pat='AR-CONC', sc=0.4, layer=D.HL)
kb = (Z_FBOT - Z_B2) / (R_BOT1 - R_BOT2)
zt_ = lambda r: Z_F15 + (r - R_SUMP_T) / 12.0            # верх днища (уклон)
zb_ = lambda r: Z_B2 + (r - R_BOT2) * kb if r < R_BOT1 else Z_FBOT
# Ск1: П 1280+400+1280, стенка r 5750; верх -2550, низ -2950 (наружные грани)
SK_T, SK_B = -2550.0 - 9, -2950.0 + 9
bar([P1(RA - LAP, SK_T), P1(RA, SK_T), P1(RA, SK_B), P1(RA - LAP, SK_B)])
# поз.1 верх: по уклону до z = SK_T-18, далее горизонтально до 5730
z1t = SK_T - 18; r_br = R_SUMP_T + 12 * (z1t - Z_F15 + 49 + 18)
bar([P1(RL, zt_(RL) - 49 - 18), P1(r_br, z1t), P1(RA - 20, z1t)])
for r in range(3700, 5701, 100):
    zz = (zt_(r) - 49 - 36) if r < r_br else z1t - 18
    dot(*P1(r, zz))
# поз.1 низ
z1b = SK_B + 18
bar([P1(RL, zb_(RL) + 59 + 18), P1(R_BOT1, z1b), P1(RA - 20, z1b)])
for r in range(3700, 5701, 100):
    zz = (zb_(r) + 59 + 36) if r < R_BOT1 else z1b + 18
    dot(*P1(r, zz))
# поз.6 вут: 850 в днище - 707 по вуту - 850 в стену (r 5067)
d6a = (R_VUT + 35, Z_F45 - 35); d6b = (R_IN + 67, Z_VUT - 35 + 32)
bar([P1(R_VUT + 35 - 850, Z_F45 - 35 - 850 / 12.0), P1(*d6a), P1(*d6b), P1(R_IN + 67, ZTOPC - 10)])
# поз.7 кольца Ø12 r 4600/4750/4900 (над вутовым стержнем)
for r in (4600.0, 4750.0, 4900.0):
    z = d6a[1] + (r - d6a[0]) - 30
    dot(*P1(r, z), r=6.0, layer=B12)
# Кр1 (каркас 600х~ между сетками) ш.1200х1200
for rc in (4100.0,):
    za, zb2 = zb_(rc) + 59 + 36 + 20, zt_(rc) - 49 - 36 - 20
    r0, r1 = rc - 300, rc + 300
    bar([P1(r0, zb_(r0) + 59 + 36 + 20), P1(r1, zb_(r1) + 59 + 36 + 20)], layer=B12)
    bar([P1(r0, zt_(r0) - 85 - 20), P1(r1, zt_(r1) - 85 - 20)], layer=B12)
    for r in (r0 + 40, r1 - 40):
        bar([P1(r, zb_(r) + 59 + 36 + 5), P1(r, zt_(r) - 85 - 5)], layer=B16)
# Вп1 (тонко, см. л. 3.4)
pl([P1(R_IN + 49, ZTOPC - 10), P1(R_IN + 49, z1b + 27), P1(R_OUT - 49, z1b + 27), P1(R_OUT - 49, ZTOPC - 10)], layer=T)
# выноски 1-1
note('1', 'ш.100', P1(3700, -1800), P1(4000, zt_(4000) - 67))
note('1', 'ш.100', P1(4250, -3350), P1(4500, zb_(4500) + 77))
note('Ск1', 'ш.100', P1(6500, -2200), P1(RA, -2700))
note('6', 'ш.100', P1(4900, -1200), P1(4785, -2327))
note('7', '', P1(4400, -1500), P1(4750, d6a[1] + 215 - 30))
note('Кр1', 'ш.1200х1200', P1(3400, -3750), P1(4100, zb_(4100) + 115))
note('Вп1', 'см. л. 3.4', P1(6500, -1650), P1(R_OUT - 49, -1850))
# размеры 1-1
dim(P1(R_FM, Z_FBOT), P1(R_FM, SK_B - 9), P1(R_FM + 400, Z_FBOT), V, SC, tx=P1(R_FM + 400 - 110, Z_FBOT - 230))
dim(P1(R_FM, SK_B - 9), P1(R_FM, SK_T + 9), P1(R_FM + 400, Z_FBOT), V, SC)
dim(P1(R_FM, SK_T + 9), P1(R_FM, Z_WBOT), P1(R_FM + 400, Z_FBOT), V, SC, tx=P1(R_FM + 400 - 110, Z_WBOT + 230))
dim(P1(RA - LAP, SK_B), P1(RA, SK_B), P1(RA, Z_FBOT - 800), 0.0, SC)
dim(P1(RA, Z_FBOT), P1(R_FM, Z_FBOT), P1(RA, Z_FBOT - 800), 0.0, SC, tx=P1(R_FM + 250, Z_FBOT - 800 + 110))
dim(P1(3700, Z_FBOT), P1(4900, Z_FBOT), P1(3700, Z_FBOT - 1200), 0.0, SC, txt='1200')

# ======================= Узел стыковки внахлест =======================
ux, uy = X0 + 17600.0, Y0 + 8100.0
sh.text(L.title_u('Узел стыковки одиночных арматур внахлест (без сварки)'), ux + 2400, uy + 1350, 175, att=8, layer='0')
LP, LZ = 1280.0, 1917.0                        # 71d, 106,5d (d=18)
yA, yB = uy + 250, uy - 250                    # две пары (вразбежку)
x1 = ux + 600; x2 = x1 + LZ
# пара 1 (нижняя): стержень слева до x1+LP, стержень справа от x1
bar([(ux - 400, yB), (x1 + LP, yB)]); bar([(x1, yB - 70), (ux + 5200, yB - 70)])
bar([(ux - 400, yA), (x2 + LP, yA)]); bar([(x2, yA - 70), (ux + 5200, yA - 70)])
for xa_, ya_ in ((x1, yB), (x2, yA)):
    for k in range(4):
        xx = xa_ + 200 + k * 290
        pl([(xx - 50, ya_ - 130), (xx + 50, ya_ + 60)], layer=T)
for y_ in (yA, yB):
    D.break_line(lambda a, b: (a, b), ux - 400, y_ - 120, y_ + 60)
    D.break_line(lambda a, b: (a, b), ux + 5200, y_ - 165, y_ + 15)
dim((x1, yB), (x1 + LP, yB), (x1, yB - 400), 0.0, SC, txt='71d')
dim((x2, yA), (x2 + LP, yA), (x2, yA + 400), 0.0, SC, txt='71d')
dim((x1, yA), (x2, yA), (x1, yA + 800), 0.0, SC, txt='106,5d')
sh.text('(вразбежку)', x2 + LP + 250, yA + 400 + 60, 125, att=7, layer=L.L_TXT)
note('Скрутить вязальной проволокой', 'не менее 3-х скруток', (x1 - 200, uy + 950), (x2 + 300, yA - 20), arrow='arrow')
note('Стыкуемые', 'арм. стержни', (ux - 200, uy - 950), (ux + 100, yB), arrow='arrow')
sh.text('Расстояние до стыка: ~1/2L - для нижней зоны;  500 - для верхней зоны', ux - 400, uy - 1550, 125, att=7, layer=L.L_TXT)
sh.text('"d" - диаметр горизонтальной стыкуемой арматуры плиты', ux - 400, uy - 1900, 125, att=7, layer=L.L_TXT)

# ======================= примечания =======================
sh.notes(['Общие указания см. л. 1.1.', 'Данный лист читать совместно с л. 3.1, 3.3, 3.4.',
          'Стыки рабочей арматуры внахлестку без сварки, на скрутках из вязальной проволоки не менее 3 шт. на стык. Длина нахлеста 71d. Стыки располагать вразбежку, чтобы площадь рабочей арматуры, стыкуемой в одном сечении, не превышала 50%.',
          'Расход арматуры в погонных метрах приведен с учетом нахлеста.',
          'Стержни, указанные в "Ведомости деталей" (л. 3.3), должны гнуться механическим способом в холодном состоянии с радиусом гиба 3d - 5d, где d - диаметр стержня.'], w=9250)
L.dump(r'D:\_claude_work\otst\s4\ops\s32.json')
if __name__ == '__main__':
    import s4_ab
    print(s4_ab.run(L.OPS, 's32')); lg = s4_ab.log()
    print("\n".join(l[:200] for l in lg.splitlines() if l.startswith(('ERR', 'done', 'no ', 'GUARD'))))
