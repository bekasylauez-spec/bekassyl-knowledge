"""Лист 1.4 «Спецификация котлована и раскатных свай» — Помещение обезвоживания.
Разрез 1-1 по оси Б (оси 1, 2 | разрыв | 7, 8), разрез по свае (относительные отметки), указания, таблицы."""
import sys, os, re, math
import ab, geo_ob
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

A1, Y0 = -1599244.0, -1714044.0                 # axis 1 / level 0.000 of section 1-1 on the sheet
a = {1: 0.0, 2: 3250.0, 7: 7250.0, 8: 13250.0}  # drawn axis positions (break between 2 and 7)
BR = 5250.0                                     # break x
XI0, XI1 = -2100.0, a[8] + 2100                  # pit bottom edges
XO0, XO1 = XI0 - 650, XI1 + 650                  # slope tops
ZG, ZT, ZB, ZS, ZC, ZP = -300, -500, -1500, -1600, -2600, -2952   # ground, pad top, pad bottom, sole, cushion bottom, pile head bottom


def P(x, z):
    return [round(A1 + x, 1), round(Y0 + z, 1)]


def rect(x0, x1, z0, z1):
    return [P(x0, z0), P(x1, z0), P(x1, z1), P(x0, z1)]


O = []
TAGN = [0]


def clone_rect(src, pts, hatch=None, hp=None):
    TAGN[0] += 1; t = 'c14_%d' % TAGN[0]
    O.append({'t': 'clone', 'h': src, 'tag': t})
    O.append({'t': 'plset', 'h': t, 'p': pts, 'closed': True})
    if hatch:
        th = t + 'h'
        O.append({'t': 'clone', 'h': hatch, 'tag': th})
        O.append({'t': 'hatchset', 'h': th, 'loops': [hp or pts]})


# ---------- section 1-1 geometry
O.append({'t': 'plset', 'h': '37EA48', 'p': [P(XO0 - 1300, ZG), P(XO0, ZG), P(XI0, ZS), P(XI1, ZS), P(XO1, ZG), P(XO1 + 1300, ZG)], 'closed': False})
SLAB = (-350, a[8] + 350, -120, 0)
O.append({'t': 'plset', 'h': '37EA3D', 'p': rect(*SLAB), 'closed': True})
O.append({'t': 'hatchset', 'h': '37EA3C', 'loops': [rect(*SLAB)]})
struct = []
for k, x in a.items():
    clone_rect('37EA3B', rect(x - 1000, x + 1000, ZB, ZT), '37EA3A')            # pad 2000 x 1000
    clone_rect('37EA39', rect(x - 1100, x + 1100, ZS, ZB), '37EA38')            # подготовка 100
    clone_rect('37EA3B', rect(x - 300, x + 300, ZT, -120), '37EA3A')            # column stub
    struct += [box(x - 1000, ZB, x + 1000, ZT), box(x - 1100, ZS, x + 1100, ZB), box(x - 300, ZT, x + 300, -120)]
for x0, x1 in ((1000, 2250), (4250, BR - 100), (BR + 100, 6250), (8250, 12250)):   # foundation beams 350x600 (cut along)
    clone_rect('37EA3B', rect(x0, x1, -1100, ZT), '37EA3A')
    struct.append(box(x0, -1100, x1, ZT))
# backfill = pit below ground + under-slab layer, minus structures
pit = Polygon([(XO0, ZG), (XI0, ZS), (XI1, ZS), (XO1, ZG)])
fill = unary_union([pit, box(SLAB[0], ZG, SLAB[1], -120)]).difference(unary_union(struct))
loops = []
for g in (fill.geoms if hasattr(fill, 'geoms') else [fill]):
    loops.append([P(x, z) for x, z in list(g.exterior.coords)[:-1]])
    for r in g.interiors:
        loops.append([P(x, z) for x, z in list(r.coords)[:-1]])
O.append({'t': 'hatchset', 'h': '37EA3E', 'loops': loops})
# cushion 1000 under foundations (whole sole width), pile heads, soil band, break
CU = (-1100, a[8] + 1100)
O.append({'t': 'hatchset', 'h': '3D1545', 'loops': [rect(CU[0], CU[1], ZC, ZS)]})
O.append({'t': 'plset', 'h': '3D1546', 'p': [P(CU[0], ZC), P(CU[1], ZC)], 'closed': False})
PX = [-1000, 0, 1000, 1625, 2250, 3250, 4250, 6250, 7250, 8250, 9250, 10250, 11250, 12250, 13250, 14250]
old_heads = ['3D15F8', '3D15F9', '3D15FA', '3D15FB', '3D15FC', '3D15FD', '3D15FE', '3D15FF', '3D1600', '3D1601', '3D1602', '3D1603', '3D1604', '3D1605']
for i, x in enumerate(PX):
    pts = rect(x - 250, x + 250, ZP, ZC)
    if i < len(old_heads):
        O.append({'t': 'plset', 'h': old_heads[i], 'p': pts, 'closed': True})
    else:
        clone_rect('3D15F8', pts)
band = [rect(CU[0], CU[1], ZP, ZC)] + [rect(x - 250, x + 250, ZP, ZC) for x in PX]
O.append({'t': 'hatchset', 'h': '37EA50', 'loops': band})
O.append({'t': 'spmove', 'h': '37EA54', 'items': [[0] + P(CU[1], ZP), [1] + P(BR, ZP), [2] + P(CU[0], ZP)]})
O.append({'t': 'spmove', 'h': '37EA46', 'items': [[0] + P(XI0, ZS), [1] + P(XI1, ZS)]})
# axes
for h, k in (('37EA24', 1), ('37EA25', 2), ('37EA29', 7), ('37EA2D', 8)):
    O.append({'t': 'axis', 'h': h, 's': P(a[k], 0), 'e': P(a[k], -5632), 'val': str(k)})


# ---------- dims
def hd(h, x1, z1, x2, z2, zl, txt=None, tx=None):
    o = {'t': 'dimset2', 'h': h, 'p1': P(x1, z1), 'p2': P(x2, z2), 'dl': P(x1, zl), 'tx': tx or P((x1 + x2) / 2, zl + 187)}
    O.append(o)
    if txt: O.append({'t': 'dimtext', 'h': h, 's': txt})


def vd(h, x1, z1, x2, z2, xl, tx=None):
    O.append({'t': 'dimset2', 'h': h, 'p1': P(x1, z1), 'p2': P(x2, z2), 'dl': P(xl, z1), 'tx': tx or P(xl - 188, (z1 + z2) / 2)})


ZL = -4932
hd('37EA4F', XO0, ZG, XI0, ZS, ZL)
hd('37EA4E', a[1], ZS, XI0, ZS, ZL)
hd('37EA2A', a[1], -6132, a[2], -6132, ZL)
hd('37EA2E', a[2], -6132, a[7], -6132, ZL, '4500х3+3250=16750', P((a[2] + a[7]) / 2 + 2600, ZL + 531))
hd('37EA31', a[7], -6132, a[8], -6132, ZL)
hd('37EA26', a[1], -6132, a[8], -6132, -5632, '32000')
hd('37EA56', XI1, ZS, a[8], ZS, ZL)
hd('37EA62', XI1, ZS, XO1, ZG, ZL)
vd('37EA44', XI0, ZS, XO0, 0, -4574)
vd('37EA49', XI0, ZS, XI0, ZG, -3720)
vd('37EA4B', XI0, ZG, XI0, 0, -3720, P(-3720 - 188, 450))
vd('37EA57', XI1, ZS, XI1, ZG, a[8] + 4400)
vd('37EA64', XO1, 0, XO1, ZS, a[8] + 5258)
vd('37EA5E', XI1, ZG, XO1, 0, a[8] + 4400, P(a[8] + 4400 - 188, 450))

# ---------- level marks (tip, shelf end); texts fixed after the move
LM = [('37EA45', 0, 'L', '0.000'), ('37EA4A', ZG, 'L', '-0,300'), ('37EA47', ZS, 'L', '-1,600'),
      ('37EA58', 0, 'R', '0.000'), ('37EA5A', ZG, 'R', '-0,300'), ('37EA59', ZS, 'R', '-1,600')]
for h, z, side, v in LM:
    if side == 'L':
        tip, sh = P(XO0 - 1300 + 100, z), P(-6329, z + 500)
    else:
        tip, sh = P(XO1 + 1300 - 100, z), P(a[8] + 7092, z + 500)
    O.append({'t': 'spmove', 'h': h, 'items': [[0] + tip, [1] + sh]})

# ---------- notes «Грунт обратной засыпки»: move with their leaders into the fill
for h, tgt0, tgt in (('37EA55', (-1599790, -1715027), (-1700, -1000)), ('37EA5F', (-1590403, -1715092), (10250, -1350)),
                     ('37EA5D', (-1584257, -1715235), (14750, -1000))):
    O.append({'t': 'moveto', 'h': h, 'idx': 1, 'to': P(*tgt)})
O.append({'t': 'moveto', 'h': '37EA63', 'idx': 0, 'to': P((XO0 + XO1) / 2 - 1564, 3006)})

# ---------- erase analog-only parts of section 1-1
O.append({'t': 'erase', 'h': ['37EA21', '37EA35', '37EA20', '37EA34', '37EA22', '37EA23', '37EA36', '37EA37', '37EA38', '37EA39', '37EA3A', '37EA3B',
                              '37EA3F', '37EA40', '37EA41', '37EA42', '37EA43', '37EA4C', '37EA4D', '37EA5B', '37EA5C']})

# ---------- pile section: ground 200 lower (sole 1300 below ground), relative levels
O.append({'t': 'stretchwin', 'win': [-1601000, -1728100, -1586000, -1727000], 'sel': [-1601000, -1728100, -1586000, -1727000], 'd': [0, -200]})
O.append({'t': 'hatchset', 'h': '37E9F1', 'loops': [[[-1593897, -1728219], [-1591188, -1728219], [-1591188, -1731219], [-1593897, -1731219]]]})
O.append({'t': 'plset', 'h': '37E9F2', 'p': [[-1593897, -1728219], [-1591188, -1728219], [-1591188, -1731219], [-1593897, -1731219]], 'closed': True})

# ---------- quantities
F, S = geo_ob.piles()
nF, nS = len(F), len(S)
Ab = 36.2 * 17.2; At = 37.5 * 18.5; Am = 36.85 * 17.85
Vpit = 1.3 / 6 * (Ab + 4 * Am + At)               # -0.300 ... -1.600
Vcush = Ab * 1.0                                  # -1.600 ... -2.600, whole pit bottom
Vexc = Vpit + Vcush
pads = 24 * (2.0 * 3.0 * 1.0 + 2.2 * 3.2 * 0.1)
blen = 3 * (32 - 8 * 2.0) + 8 * (12 - 3 * 3.0)
beams = blen * 0.35 * 0.6
cols = 24 * 0.38 * 0.7 * 0.2                      # stubs below -0.300 (≈0.7x0.7 avg x 0.2)... conservative
Vfill = Vpit - pads - beams - cols + 32.7 * 12.7 * 0.18   # plus layer -0.300...-0.120 inside the building
fmt = lambda v: ('%.2f' % v).replace('.', ',')
print('piles', nF, nS, 'Vexc %.2f Vpit %.2f Vcush %.2f Vfill %.2f pads %.2f beams %.2f (L=%.1f)' % (Vexc, Vpit, Vcush, Vfill, pads, beams, blen))
O.append({'t': 'tset', 'h': '37EA1C', 'cells': [[2, 3, 'Свая раскатная Св1 %%C500, L=11000 (под Фм-1)'], [2, 4, str(nF)], [2, 5, '-2,600'],
                                               [3, 3, 'Свая раскатная Св1 %%C500, L=11000 (под Пм-1)'], [3, 4, str(nS)], [3, 5, '-2,600']]})
O.append({'t': 'tset', 'h': '37EA74', 'cells': [[2, 5, fmt(Vexc)], [3, 5, fmt(Vfill)], [4, 5, fmt(Vcush)]]})

NOTE = ('{\\C7;\\P\\P                       Общие указания по устройству подушки и раскатных свай'
        '\\P1. Раскатные сваи Св1 %%C500 мм, L=11000 мм, заполнение - бетон класса C16/20 (B20) W4. Отметка верха свай -2.600, низа -13.600.'
        '\\P2. Шаг свай: под фундаментами Фм-1 - 1000х1000 мм (' + str(nF) + ' шт.), под плитой по грунту Пм-1 - 2000х2000 мм (' + str(nS) + ' шт.), см. лист 1.3.'
        '\\P3. Скважины образуются раскатчиком без выемки грунта с последующим заполнением бетоном. Сваи выполнять с отметки -2.600 (низ подушки).'
        '\\P4. После устройства свай выполнить подушку из уплотненного суглинка толщиной 1000 мм (отм. -2.600...-1.600), уплотнение слоями 200-250 мм до Купл=0,95 с контролем плотности.'
        '\\P5. Работы выполнять в соответствии с СП РК 5.01-103-2013 "Свайные фундаменты" и ППР.'
        '\\P6. До начала массовых работ выполнить опытные сваи и испытания по ГОСТ 5686-2012 для подтверждения несущей способности основания, принятой в расчете.'
        '\\P7. Проектом производства работ (ППР) предусмотреть водопонижение площадки на период строительства.}')
O.append({'t': 'settext', 'h': '37EA76', 's': NOTE})
NOTE2 = ('{\\C256;8. Все железобетонные поверхности, соприкасающиеся с грунтом засыпки, покрыть мастикой гидроизоляционной ТЕХНОНИКОЛЬ №24 (МГТН) по ТУ 5775-034-17925162-2005 за 2 раза, по предварительно приготовленной поверхности из праймер битумный ТЕХНОНИКОЛЬ № 01 по ТУ 5775-011-17925162-2003.'
         '\\P9. При обратной засыпке грунта гидроизоляционный слой защитить от механических повреждений геотекстилем или защитным слоем.'
         '\\P10. Отметки даны относительные (0.000 - чистый пол 1-го этажа). Инженерно-геологические слои на разрезе по свае приняты по отчету изысканий площадки завода (апрель 2026) - уточнить по скважинам в пятне здания.}')
O.append({'t': 'settext', 'h': '37EA7B', 's': NOTE2})

if len(sys.argv) > 1:
    out = ab.run(O, 'g14', 1200)
    open('w/g14.log', 'w', encoding='utf-8').write(out)
    print(out[-2500:])
else:
    print(len(O), 'ops')
