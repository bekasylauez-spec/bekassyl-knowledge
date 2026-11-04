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
         'Данный лист читать совместно с л. 2.1 и 3.1 ... 3.8.',
         'Стыки рабочей арматуры внахлестку без сварки, на скрутках из вязальной проволоки не менее 3 шт. на стык. '
         'Длина нахлеста 71d. Стыки располагать вразбежку, чтобы площадь рабочей арматуры, стыкуемой в одном сечении, не превышала 50%.',
         'Расход арматуры в погонных метрах приведен с учетом нахлеста.',
         'Дополнительные стержни укладываются в одном уровне с основной сеткой, между ее стержнями.',
         'Армирование принято по расчетной модели ЛИРА "Тип А6 С2" от 03.11.2026; в полосе между осями А и Б (y = 8,0...13,9 м) '
         'модель короче схемы на 5 м - армирование в этой полосе принято условно.']


def notes_mtext(fx, lines, sc=1.0, tag='N'):
    txt = '\\P'.join('%d. %s' % (i + 1, l) for i, l in enumerate(lines))
    add(t='mtext', at=[fx + 40400 * sc, 455939 + (5500 + 750) * sc], h=250 * sc, w=18400 * sc, att=7, s=txt, layer='О_Формат', style='Isocpeur', tag=tag)


K = 0.25; fx7 = 528579.0
add(t='eraseregion', win=[fx7+300, 455938.9+3500, fx7+12500, 455938.9+8600])
SC = 25
DOT0 = (-1966500 + 9803 + 16, -1318500 + 5801 + 16)
SHPOS = json.load(open('arm/fm_shear_pos.json')) if __import__('os').path.exists('arm/fm_shear_pos.json') else {}
SHPOS = {int(k): v for k, v in SHPOS.items()}
def dimK(p1, p2, dl, vert, txt=None, tx=None):
    o = {'t': 'dim', 'h': 'CC00A', 'p1': p1, 'p2': p2, 'dl': dl, 'rot': math.pi / 2 if vert else 0.0, 'dscale': SC}
    if txt: o['txt'] = txt
    if tx: o['tx'] = tx
    ops.append(o)
# section origin: x = axis 1, z = 0 at ±0.000; two drawings: опалубка (left) and армирование (right)
XL = 0.0
for k, (ox, oy) in enumerate([(fx7 + 2600, 455938.9 + 6400), (fx7 + 8300, 455938.9 + 6400)]):
    P = lambda x, z: [ox + x, oy + (z + 4650)]           # z: absolute level mm; oy at −4.650
    xr = 3300                                             # break at x = 3.3 m from axis 1
    slab = [P(-825, -4650), P(xr, -4650), P(xr, -5350), P(-825, -5350)]
    add(t='pl', p=[slab[1], slab[0], slab[3], slab[2]], closed=False, layer='0', color=124, lw=30 if k == 0 else 5)
    add(t='hatch', pat='ANSI36', sc=5, ang=0, layer='.', loops=[slab]) if k == 0 else None
    prep = [P(-925, -5350), P(xr, -5350), P(xr, -5450), P(-925, -5450)]
    add(t='pl', p=[prep[1], prep[0], prep[3], prep[2]], closed=False, layer='0', color=124, lw=18)
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
    dimK(P(-125, -3950), P(125, -3950), [P(125, 0)[0], P(0, -3800)[1]], False, tx=[P(255, 0)[0], P(0, -3800)[1] + 56])
    if k == 0:
        dimK(P(-825, -4650), P(-825, -5350), [P(-1200, 0)[0], P(0, -5350)[1]], True)
        dimK(P(-925, -5350), P(-925, -5450), [P(-1200, 0)[0], P(0, -5450)[1]], True)
        note('O37a', 'Фм-1', P(1700, -4300), [P(1500, -4650)], scale=SC)
        note('O37b', 'Стена', P(800, -4100), [P(125, -4400)], scale=SC)
        note('O37c', 'Бетонная подготовка', P(1300, -5800), [P(1100, -5450)], l2='С8/10 t=100', scale=SC)
    else:
        # analog «Разрез а-а» graphics (Bekassyl 04.11: «Разрезді соңғы аналогтан алып жаса»): bars along the cut =
        # thin rectangles (two lines + end caps, analog 2C2F35/4F/50), bars across = analog dot hatch 2C2F55 (scaled 1:2),
        # shear bars = analog block A$Ceb61dfd2 outline, Ск1 green, notes СПДС: Oblique on lines, None on dots.
        zL, zD = -5292, -5276                 # bottom: line (X bars) / dots (Y bars) centres, cover 50
        tD, tL = -4688, -4704                 # top: dots / line, cover 30
        e0 = -825 + 50
        def barline(x0, x1, zc, lay='диам16', d=16):
            add(t='pl', p=[P(x0, zc - d / 2), P(x1, zc - d / 2), P(x1, zc + d / 2), P(x0, zc + d / 2)], closed=True, layer=lay)
        barline(e0 + 30, xr - 15, zL); barline(e0 + 30, xr - 15, tL)
        xs = [e0 + 25 + 200 * i for i in range(int((xr - e0 - 100) / 200) + 1)]
        for x in xs:
            for z in (zD, tD):
                add(t='clone', h='D37:2C2F55', base=[DOT0[0], DOT0[1]], to=P(x, z), s=0.5)
        add(t='pl', p=[P(e0 + 980, tL), P(e0, tL), P(e0, zL), P(e0 + 980, zL)], closed=False, layer='диам16', color=3)
        # Ф1 frogs (Ø12) between the meshes
        for x0 in (250, 1350, 2350):
            add(t='pl', p=[P(x0, zD + 14), P(x0 + 300, zD + 14), P(x0 + 300, tD - 14), P(x0 + 600, tD - 14), P(x0 + 600, zD + 14), P(x0 + 900, zD + 14)], closed=False, layer='диам12')
        # shear bars of the zones crossing the cut (y = 2000)
        SH = json.load(open('arm/fm_shear.json'))
        shx = []
        for zz in SH:
            if zz['y0'] - 1 <= 2100 <= zz['y1'] + 1:
                k_ = 0
                while zz['x0'] + 200 * k_ <= zz['x1'] + 1:
                    shx.append((zz['x0'] + 200 * k_, zz['d'])); k_ += 1
        for x, d in shx:
            if not (-825 < x < xr - 50): continue
            h2 = (tD - zD) / 2 + 8; zc = (tD + zD) / 2; w = d; hk = 60
            q = [(-w, h2), (-w, -h2), (-w - hk, -h2), (-w - hk, -h2 - 8), (-12, -h2 - 8), (0, -h2 + 4), (0, h2 - 4), (-12, h2 + 8), (-w - hk, h2 + 8), (-w - hk, h2)]
            add(t='pl', p=[P(x + w / 2 + qx, zc + qz) for qx, qz in q], closed=False, layer='диам%d' % d)
        dimK(P(-825, -4650), P(-825, tD + 8), [P(-1200, 0)[0], P(0, tD + 8)[1]], True)
        dimK(P(-825, tD + 8), P(-825, zL - 8), [P(-1200, 0)[0], P(0, zL - 8)[1]], True)
        dimK(P(-825, zL - 8), P(-825, -5350), [P(-1200, 0)[0], P(0, -5350)[1]], True)
        n = len(xs) - 1
        dimK(P(-825, zD), P(xs[0], zD), [P(xs[0], 0)[0], P(0, -6100)[1]], False)
        dimK(P(xs[0], zD), P(xs[-1], zD), [P(xs[-1], 0)[0], P(0, -6100)[1]], False, txt='200x%d' % n)
        def note2(tag, l1, org, tg, l2='', arrow='Oblique'):
            note(tag, l1, org, tg, l2=l2, scale=SC)
            add(t='mcset', h=tag, set={'Arrow': arrow})
        note2('R37a', 'Ск1', P(-450, -4250), [P(e0, tL - 150)])
        note2('R37b', '1', P(2850, -4250), [P(2700, tL)], l2='ш.200')
        note2('R37c', '1', P(2300, -5800), [P(xs[11], zD)], l2='ш.200', arrow='None')
        note2('R37d', 'Ф1', P(1200, -4250), [P(1650, tD - 250)], l2='ш.400х400')
        if shx:
            xsh = [x for x, d in shx if -825 < x < xr - 50]
            if xsh:
                note2('R37e', str(SHPOS.get(shx[0][1], '')), P(xsh[-1] + 700, -5800), [P(xsh[-1], -5000)], l2='ш.200х200')
    # titles
    add(t='mtext', at=P(1200, -3300), h=87.5, w=4000, att=5, s='{\\LРазрез 1-1 (%s)}' % ('опалубка' if k == 0 else 'армирование'),
        layer='О_Формат', style='Isocpeur', tag='T37_%d' % k)
json.dump(ops, open('ops/fm37.json','w',encoding='utf-8'), ensure_ascii=False)
print(len(ops))
