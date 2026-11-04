# Фм-1: notes/sections on 3.1–3.2, sheet 3.7 (sections 1:25), sheet 3.8 (specification) — analog «3.1 Фундамент»
import json, math, sys
sys.path.insert(0, '.')
import model as M
from dimtools import chain
import gen_fm as G

ops = []
def add(**k): ops.append(k); return k
NOTE = 'E7E6A'; NOTE_O = [986.812891713809, -2983441.65079645]
SEC = 'F1169'; SEC_O = [1421234.9, -1320597.1]
LEV6 = ('F1167', (1779945.2, -1326169.6), 1784837.9, '-4,350')
FX0, FY0, FX1, FY1 = M.FM


def note(tag, l1, org, tgts, l2='', scale=None):
    add(t='clone', h=NOTE, base=NOTE_O, to=org, tag=tag)
    add(t='spmove', h=tag, items=[[1, tgts[0][0], tgts[0][1]]])
    st = {'FirstLine': l1, 'SecondLine': l2, 'Angle': math.pi if tgts[0][0] > org[0] else 0.0}
    if scale: st['Scale'] = scale
    add(t='mcset', h=tag, set=st)
    for q in tgts[1:]: add(t='addleader', h=tag, target=q)


def section(tag, word, p0, p1):
    add(t='clone', h=SEC, base=SEC_O, to=p0, tag=tag)
    add(t='spmove', h=tag, items=[[1, p1[0], p1[1]]])
    add(t='mcset', h=tag, set={'Word': word})


NOTES = ['Общие указания см. л. 1.1.',
         'Данный лист читать совместно с л. 2.1 и 3.1 ... 3.9.',
         'Стыки рабочей арматуры внахлестку без сварки, на скрутках из вязальной проволоки не менее 3 шт. на стык. '
         'Длина нахлеста 71d. Стыки располагать вразбежку, чтобы площадь рабочей арматуры, стыкуемой в одном сечении, не превышала 50%.',
         'Расход арматуры в погонных метрах приведен с учетом нахлеста.',
         'Дополнительные стержни укладываются в одном уровне с основной сеткой, между ее стержнями.',
         'Армирование принято по расчетной модели ЛИРА "Тип А6 С2" от 03.11.2026; в полосе между осями А и Б (y = 8,0...13,9 м) '
         'модель короче схемы на 5 м - армирование в этой полосе принято условно.']


def notes_mtext(fx, lines, sc=1.0, tag='N'):
    txt = '\\P'.join('%d. %s' % (i + 1, l) for i, l in enumerate(lines))
    add(t='mtext', at=[fx + 40400 * sc, 455939 + (5500 + 750) * sc], h=250 * sc, w=18400 * sc, att=7, s=txt, layer='О_Формат', style='Isocpeur', tag=tag)


# ---------- 3.1 / 3.2 ----------
for sh in ('3.1', '3.2'):
    fx, X, Y = G.origin(sh)
    section('S1_' + sh, '1', [X + 3800, Y + 2000], [X - 3200, Y + 2000])
    notes_mtext(fx, NOTES[:2] + ([NOTES[2], NOTES[3]] if sh == '3.2' else []), tag='N' + sh)
fx, X, Y = G.origin('3.2')
note('P1a', '1', [X + 11000, Y + 3300], [[X + 10025, Y + 3000], [X + 10700, Y + 2400]], l2='ш.200')
note('P1b', 'Ск1', [X + FX0 + 900, Y + 3200], [[X + FX0 + 50, Y + 2400]])
note('P1c', 'Ск1', [X + FX1 - 900, Y + 3200], [[X + FX1 - 50, Y + 2400]])
note('P1d', 'Ск1', [X + 10900, Y + FY1 - 800], [[X + 10025, Y + FY1 - 50]])
note('P1e', 'Ск1', [X + 10900, Y + FY0 + 800], [[X + 10025, Y + FY0 + 50]])
for sh in ('3.3', '3.4', '3.5', '3.6'):
    fx, X, Y = G.origin(sh)
    ex = ['Позиции со "*" - третья сетка: укладывается над основной нижней сеткой с зазором 60 мм, за расчетную зону выходит на анкеровку.'] if sh == '3.5' else []
    notes_mtext(fx, NOTES + ex, tag='N' + sh)

# ---------- 3.7 sections 1:25 (frame F0D08 already scaled) ----------
K = 0.25; fx7 = 528579.0
d7 = fx7 - (-184221.0)
for h in ('DC478', 'DC479', 'DC4E3', 'DC4E5'):
    add(t='clone', h=h, base=[-184221.0, 455938.9], to=[fx7, 455938.9], s=K, tag='FM3.7_' + h)
add(t='settext', h='FM3.7_DC479', s='3.7')
add(t='settext', h='FM3.7_DC4E3', s='{\\LРазрез 1-1}', w=30000 * K)
add(t='settext', h='FM3.7_DC4E5', s='Разрез 1-1 фундамента Фм-1', w=7000 * K)
SC = 25
def dimK(p1, p2, dl, vert, txt=None, tx=None):
    o = {'t': 'dim', 'h': 'CC00A', 'p1': p1, 'p2': p2, 'dl': dl, 'rot': math.pi / 2 if vert else 0.0, 'dscale': SC}
    if txt: o['txt'] = txt
    if tx: o['tx'] = tx
    ops.append(o)
# section origin: x = axis 1, z = 0 at ±0.000; two drawings: опалубка (left) and армирование (right)
XL = 0.0
for k, (ox, oy) in enumerate([(fx7 + 2200, 455938.9 + 6400), (fx7 + 8300, 455938.9 + 6400)]):
    P = lambda x, z: [ox + x, oy + (z + 4650)]           # z: absolute level mm; oy at −4.650
    xr = 3300                                             # break at x = 3.3 m from axis 1
    slab = [P(-825, -4650), P(xr, -4650), P(xr, -5350), P(-825, -5350)]
    add(t='pl', p=slab + [slab[0]], closed=False, layer='0', color=124, lw=30)
    add(t='hatch', pat='ANSI36', sc=5, ang=0, layer='.', loops=[slab]) if k == 0 else None
    prep = [P(-925, -5350), P(xr, -5350), P(xr, -5450), P(-925, -5450)]
    add(t='pl', p=prep + [prep[0]], closed=False, layer='0', color=124, lw=18)
    add(t='hatch', pat='AR-CONC', sc=0.4, ang=0, layer='.', loops=[prep])
    wall = [P(-125, -4650), P(125, -4650), P(125, -3900), P(-125, -3900)]
    add(t='pl', p=[wall[3], wall[0]], closed=False, layer='0', color=124, lw=30); add(t='pl', p=[wall[1], wall[2]], closed=False, layer='0', color=124, lw=30)
    add(t='pl', p=[P(-200, -3900), P(-30, -3900), P(0, -3840), P(30, -3960), P(60, -3900), P(200, -3900)], closed=False, layer='0', lw=13)
    add(t='pl', p=[P(xr, -4600), P(xr + 60, -4900), P(xr - 60, -5100), P(xr, -5400)], closed=False, layer='0', lw=13)
    if k == 0: add(t='hatch', pat='ANSI36', sc=5, ang=0, layer='.', loops=[wall])
    # axis 1
    add(t='clone', h='C8719', base=[0, 0], to=[0, 0], tag='A37_%d' % k)
    add(t='axis', h='A37_%d' % k, s=P(0, -3700), e=P(0, -6600), val='1', scale=SC)
    # level −4.650 (left of the slab)
    h, tip, xend, old = LEV6
    tx_, ty_ = P(-1500, -4650)
    add(t='clone', h=h, base=list(tip), to=[tx_, ty_], tag='L37_%dc' % k)
    add(t='serfix', h='L37_%dc' % k, s=[[old, '-4.650']], d=[[xend + tx_ - tip[0], P(-825, -4650)[0], 0.6]], tag='L37_%d' % k)
    add(t='mcscale', h='L37_%d' % k, v=SC)
    # dims: 825 / 250 wall, thickness chain
    dimK(P(-825, -5450), P(0, -5450), [P(0, -5450)[0], P(0, -5850)[1]], False)
    dimK(P(-125, -3950), P(125, -3950), [P(125, 0)[0], P(0, -3800)[1]], False)
    if k == 0:
        dimK(P(-825, -4650), P(-825, -5350), [P(-1200, 0)[0], P(0, -5350)[1]], True)
        dimK(P(-925, -5350), P(-925, -5450), [P(-1200, 0)[0], P(0, -5450)[1]], True)
        note('O37a', 'Фм-1', P(1700, -4300), [P(1500, -4650)], scale=SC)
        note('O37b', 'Стена', P(800, -4100), [P(125, -4400)], scale=SC)
        note('O37c', 'Бетонная подготовка', P(1300, -5800), [P(1100, -5450)], l2='С8/10 t=100', scale=SC)
    else:
        # bars: Ск1 (green, 980/620/980), top/bottom meshes Ø16 @200, Ф1 frogs
        zt, zb = -4650 - 30, -5350 + 50
        e0 = -825 + 50
        add(t='pl', p=[P(e0 + 980, zt), P(e0, zt), P(e0, zb), P(e0 + 980, zb)], closed=False, layer='диам16', color=3)
        add(t='pl', p=[P(e0 + 20, zt - 24), P(xr - 20, zt - 24)], closed=False, layer='диам16')
        add(t='pl', p=[P(e0 + 20, zb + 24), P(xr - 20, zb + 24)], closed=False, layer='диам16')
        xs = [e0 + 25 + 200 * i for i in range(int((xr - e0 - 100) / 200) + 1)]
        for x in xs:
            for z in (zt - 8, zb + 8):
                add(t='circle', c=P(x, z), r=8, layer='диам16')
        for x0 in (300, 1500, 2700):
            add(t='pl', p=[P(x0, zb + 40), P(x0 + 300, zb + 40), P(x0 + 300, zt - 40), P(x0 + 600, zt - 40), P(x0 + 600, zb + 40), P(x0 + 900, zb + 40)], closed=False, layer='диам12')
        dimK(P(-825, -4650), P(-825, zt), [P(-1200, 0)[0], P(0, zt)[1]], True)
        dimK(P(-825, zt), P(-825, zb), [P(-1200, 0)[0], P(0, zb)[1]], True)
        dimK(P(-825, zb), P(-825, -5350), [P(-1200, 0)[0], P(0, -5350)[1]], True)
        n = len(xs) - 1
        dimK(P(-825, zb), P(e0, zb), [P(e0, 0)[0], P(0, -6100)[1]], False)
        dimK(P(e0, zb), P(xs[-1], zb), [P(xs[-1], 0)[0], P(0, -6100)[1]], False, txt='200x%d' % n)
        note('R37a', 'Ск1', P(-450, -4250), [P(e0, zt - 150)], scale=SC)
        note('R37b', '1', P(2350, -4250), [P(2200, zt - 24)], l2='ш.200', scale=SC)
        note('R37c', '1', P(3500, -5800), [P(3250, zb + 24)], l2='ш.200', scale=SC)
        note('R37d', 'Ф1', P(1200, -4250), [P(1800, zt - 200)], l2='ш.400х400', scale=SC)
    # titles
    add(t='mtext', at=P(1200, -3300), h=87.5, w=4000, att=5, s='{\\LРазрез 1-1 (%s)}' % ('опалубка' if k == 0 else 'армирование'),
        layer='О_Формат', style='Isocpeur', tag='T37_%d' % k)
notes_mtext(fx7, NOTES[:4], sc=K, tag='N3.7')

# ---------- 3.8 specification (A2 frame next to 3.7) ----------
fx8 = fx7 + 14850.0
d8 = fx8 - (-184221.0)
for h in ('DC477', 'DC478', 'DC479', 'DC4E3', 'DC4E5'):
    add(t='clone', h=h, base=[0, 0], to=[d8, 0], tag='FM3.8_' + h)
add(t='settext', h='FM3.8_DC479', s='3.8')
add(t='settext', h='FM3.8_DC4E3', s='{\\LСпецификация фундамента Фм-1 на отм. -4.650}', w=30000)
add(t='settext', h='FM3.8_DC4E5', s='Спецификация фундамента Фм-1 на отм. -4.650', w=7000)

json.dump(ops, open('ops/fm2.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(len(ops))
