# Резервуар КЖ, Фм-1 по базе Obsidian (02_Фундамент/Фундаментная плита.md) и аналогу Онкоцентр 3.1–3.8:
# 5.1 опалубка, 5.2 основная арматура (+ разрезы), 5.3–5.6 доп. (низ/верх × буквенные/цифровые), 5.7 поперечная, 5.8 спецификация.
import sys, json, math
import common as C
from common import *
from shapely.geometry import box
from shapely.ops import unary_union

D0, T = 14, 400                      # base Ø14 @200 for t=300..400 (vault), slab 400
CB, CT = 50, 40                      # cover bottom / top
LAP = lambda d: int(math.ceil(71 * d / 10.0) * 10)
SK_LEG = {12: 700, 14: 800, 16: 1000}  # П-скоба legs (vault, confirmed 20.10)

class SheetK(Sheet):
    """detail drawn k times enlarged on a 1:100 sheet: geometry ×k, paper annotations at 1:100"""
    def __init__(s, ox, oy, k):
        Sheet.__init__(s, ox, oy, 100.0 / k); s.k = k
    def P(s, x, y): return [round(s.ox + s.k * x, 2), round(s.oy + s.k * y, 2)]
    def dim(s, a, b, off, vert=False, tx=None, txt=None):
        k = Sheet.dim(s, a, b, off, vert, tx); k['dscale'] = 100; k['lfac'] = 1.0 / s.k
        if txt: k['txt'] = txt
        return k
    def note(s, l1, org, tgts, l2='', arrow='arrow'):
        ang = math.pi if sum(q[0] for q in tgts) / len(tgts) > org[0] else 0
        add(t='note', l1=l1, l2=l2, origin=s.P(*org), targets=[s.P(*q) for q in tgts], scale=100, arrow=arrow, layer='Размеры', angle=ang)
    def title(s, text, x, y, cx=None):
        h = 300.0; w = len(text) * 0.75 * h + 2 * h                     # paper 1:100, one line, centred
        c = cx if cx is not None else x + w / 2 / s.k
        add(t='mtext', at=s.P(c, y - h / 2 / s.k), h=h, w=w, att=5, style='Standard', layer='0', s='{\\L' + text + '}')
    def axis(s, tag, val, st, en):
        add(t='clone', h=SRC['axis'], tag=tag); add(t='axis', h=tag, s=s.P(*st), e=s.P(*en), val=val, scale=100)
    def level(s, tag, val, x, y, down=False, right=False, ax=None):
        add(t='clone', h=SRC['lev'], base=list(SRC['levbase']), to=s.P(x, y), tag=tag)
        add(t='levelval', h=tag, old=SRC['lev0'], value=val, tag=tag)
        add(t='moveto', h=tag, idx=0, to=s.P(x, y))
        kx = 1 if right else -1; up = -1 if down else 1; a = ax if ax is not None else x + kx * 36 * s.sc
        add(t='sp_set', h=tag, pts=[[2] + s.P(a, y), [1] + s.P(a + kx * 12.54 * s.sc, y + up * 6 * s.sc)])

def dimtxt(s, a, b, off, txt, vert=False):
    k = s.dim(a, b, off, vert); k['txt'] = txt

def slab_plan(S, hatch_walls=False):
    S.pl(rect((FXO, FYO, FXE, FYE)))
    up = unary_union([box(*r) for rs in walls1.values() for r in rs] + [box(*r) for r in walls2] +
                     [box(*r) for r in list(pil.values()) + list(cols.values()) + [col3]]).simplify(0.5)
    for g in getattr(up, 'geoms', [up]):
        rings = [[(round(x, 1), round(y, 1)) for x, y in r.coords] for r in [g.exterior] + list(g.interiors)]
        for r in rings: S.thin(r)
        if hatch_walls: S.hatch(rings)
    S.pl(rect(pit), layer='Тонкая'); S.hid(rect(pitb), closed=True)

def frameA3(num, fx, name):
    frame(fx, 340000.0, 100, name, num, 'A3')
    S = Sheet(fx + 6600, 340000.0 + 6100, 100); S.cx, S.cy = 7375, 8875
    return S

# ===================== 5.1 Опалубка Фм-1 =====================
FX = {'3.1': 113700.0, '3.2': 155700.0, '3.3': 197700.0, '3.4': 239700.0, '3.5': 281700.0, '3.6': 323700.0}
S = frameA3('3.1', FX['3.1'], 'Опалубочный чертеж\\Pфундамента Фм-1')
S.title('Опалубочный чертеж фундамента Фм-1 на отм. -3.700', 1200, FYE + 2600, cx=7375)
slab_plan(S, hatch_walls=True)
plan_axes(S, 'O1', (FXO, FYO, FXE, FYE))
S.chain([0, 4625, 5625], 14125, 15400); S.chain([13125, 14125, 17750], 4625, 4100, vert=True)
S.plevel('O1p', '-4,200', 5800, 12680)
S.section('o11', '1', (2500, FYO - 2600), (2500, 2300))          # 1-1 through the console at wall А
S.section('o12', '2', (3300, 13625), (7200, 13625))              # 2-2 through the pit
# --- Разрез 1-1 (опалубка), М 1:50: console at axis А
K = SheetK(FX['3.1'] + 30000, 340000.0 + 30000, 2)
K.title('Разрез 1-1 (опалубка) М 1:50', -1300, -2400)
K.solid((-625, -4100, 1800, -3700))                               # Фм-1 piece (with console)
K.solid((-125, -3700, 125, -2900))                                # wall См-1 stub
K.thin([(1800, -4100), (1800, -3700)])
K.pl(rect((-725, -4200, 1800, -4100)), layer='Тонкая'); K.hatch([rect((-725, -4200, 1800, -4100))], pat='AR-CONC', sc=1.5, layer='Бетон штриховка')
K.axis('k1a', 'А', (0, -2700), (0, -5600))
K.chain([-625, -125, 0, 125], -4200, -4700); K.chain([-4200, -4100, -3700], -725, -1100, vert=True)
for i, (v, z, dn) in enumerate([('-3,700', -3700, 0), ('-4,100', -4100, 1)]): K.level('k1l%d' % i, v, -725, z, down=dn)
K.note('Фм-1', (1300, -3300), [(900, -3700)])
K.note('Подбетонка C8/10', (1300, -4600), [(900, -4200)], l2='t=100')
# --- Разрез 2-2 (опалубка), М 1:50: pit
K2 = SheetK(FX['3.1'] + 22000, 340000.0 + 19500, 2)
K2.title('Разрез 2-2 (опалубка) М 1:50', 3800, -2900)
x0, x1 = 3800, 6450   # local x along the cut (= plan x)
prof = [(x0, -4100), (pitb[0], -4100), (pitb[0], -4600), (pitb[2], -4600), (pitb[2], -4100), (x1, -4100), (x1, -3700),
        (pit[2], -3700), (pit[2], -4200), (pit[0], -4200), (pit[0], -3700), (x0, -3700)]
K2.pl(prof); K2.hatch([prof])
K2.thin([(x0, -4100), (x0, -3700)]); K2.thin([(x1, -4100), (x1, -3700)])
K2.chain([pitb[0], pit[0], pit[2], pitb[2]], -4600, -5100)
K2.chain([-4600, -4200, -3700], pitb[2], pitb[2] + 450, vert=True)
for i, (v, z, dn) in enumerate([('-3,700', -3700, 0), ('-4,200', -4200, 1), ('-4,600', -4600, 1)]):
    K2.level('k2l%d' % i, v, x0, z, down=dn)
K2.note('Пр-1', (5600, -3300), [(pit[2], -3900)])

# ===================== 5.2 Основная арматура Фм-1 =====================
S = frameA3('3.2', FX['3.2'], 'Схема расположения основной\\Pарматуры фундамента Фм-1')
S.title('Схема расположения основной арматуры фундамента Фм-1 на отм. -3.700', 1200, FYE + 2600, cx=7375)
slab_plan(S)
plan_axes(S, 'O2', (FXO, FYO, FXE, FYE))
# analog 3.2: bars 50 from the edge, ONE position «1» for all base bars (пог.м.), one «1/ш.200» note with two leaders,
# «Ск1» (no step) on short leaders at the bar ends, chains «50 | 200xN=… | rest» along the top and the right side
e = 50
nX = int((FYE - FYO - 2 * e) / 200); nY = int((FXE - FXO - 2 * e) / 200)
YB, XB = 1700, 7600                                                   # horizontal bar near the bottom, vertical one through the middle
add(t='pl', p=[S.P(FXO + e, YB), S.P(FXE - e, YB)], closed=False, layer='диам14')
add(t='pl', p=[S.P(XB, FYO + e), S.P(XB, FYE - e)], closed=False, layer='диам14')
S.note('1', (XB + 800, YB + 2100), [(XB, YB + 2100), (XB + 400, YB)], l2='ш.200', arrow='oblique')
for org, tgt in [((FXO - 900, YB - 500), (FXO + e, YB)), ((FXE - 900, YB - 500), (FXE - e, YB)),
                 ((XB + 450, FYE - 700), (XB, FYE - e)), ((XB + 450, FYO - 500), (XB, FYO + e))]:
    S.note('Ск1', org, [tgt], arrow='oblique')
for a_, b_ in ((FXO, FXO + e), (FXO + e + 200 * nY, FXE)): S.dim(a_, b_, (FYE, FYE + 600))
dimtxt(S, FXO + e, FXO + e + 200 * nY, (FYE, FYE + 600), '200x%d=%d' % (nY, 200 * nY))
for a_, b_ in ((FYO, FYO + e), (FYO + e + 200 * nX, FYE)): S.dim(a_, b_, (FXE, FXE + 600), vert=True)
dimtxt(S, FYO + e, FYO + e + 200 * nX, (FXE, FXE + 600), '200x%d=%d' % (nX, 200 * nX), vert=True)
S.section('a21', '1', (2500, FYO - 2600), (2500, 2300))
# --- Разрез 1-1 (армирование), М 1:25 at the slab edge (axis А), as analog 3.2 «Разрез 1-1 (Армирование)»
K = SheetK(FX['3.2'] + 30400, 340000.0 + 30000, 4)
K.title('Разрез 1-1 (Армирование) М 1:25', -700, -2550)
XR = 1500                                                              # cut end of the drawn piece
K.pl([(XR, -4100), (-625, -4100), (-625, -3700), (XR, -3700)], closed=False)
K.thin([(XR, -4100), (XR + 60, -3990), (XR - 60, -3810), (XR, -3700)])           # break line
K.thin([(-125, -3700), (-125, -3350)]); K.thin([(125, -3700), (125, -3350)])     # wall stub, not shown
K.thin([(-200, -3350), (-30, -3350), (0, -3290), (30, -3410), (60, -3350), (200, -3350)])
K.hatch([[(-125, -3700), (125, -3700), (125, -3350), (-125, -3350)]])
K.thin([(-725, -4200), (XR, -4200)]); K.thin([(-725, -4200), (-725, -4100)])
yb1, yt1 = -4100 + CB + 7, -3700 - CT - 7                              # bars along the cut (lines)
x_first = -625 + e
add(t='pl', p=[K.P(x_first, yb1), K.P(XR, yb1)], closed=False, layer='диам14')
add(t='pl', p=[K.P(x_first, yt1), K.P(XR, yt1)], closed=False, layer='диам14')
for i in range(int((XR - x_first) / 200) + 1):
    xx = x_first + 200 * i
    for yy in (yb1 + 14, yt1 - 14): add(t='clone', h='24323', base=[534291, 275556], to=K.P(xx, yy), s=14 * 4 / 32.0)
sk = [(x_first + SK_LEG[D0], yb1 - 14), (x_first - 7, yb1 - 14), (x_first - 7, yt1 + 14), (x_first + SK_LEG[D0], yt1 + 14)]
add(t='pl', p=[K.P(*q) for q in sk], closed=False, layer='диам14', color=3)
f1 = [(150, yb1 + 28), (450, yb1 + 28), (450, yt1 - 28), (750, yt1 - 28), (750, yb1 + 28), (1050, yb1 + 28)]
add(t='pl', p=[K.P(*q) for q in f1], closed=False, layer='диам12')
K.chain([-4100, -4100 + CB, -3700 - CT, -3700], -625, -1000, vert=True)
K.dim(-4100, -3700, (-625, -1350), vert=True)
K.chain([-625, -125, 0, 125], -3350, -3150)                           # wall binding 125|125 and console
K.dim(-625, x_first, (-4200, -4450))
nn = int((XR - 100 - x_first) / 200)
dimtxt(K, x_first, x_first + 200 * nn, (-4200, -4450), '200x%d=%d' % (nn, 200 * nn))
K.note('1', (XR + 50, -4450), [(XR + 450, -4450)], l2='ш.200', arrow='arrow')
K.note('1', (900, -3450), [(700, yt1)], l2='ш.200', arrow='oblique')
K.note('1', (1100, -4800), [(1025, yb1 + 14), (825, yb1 + 14)], l2='ш.200', arrow='none')
K.note('Ск1', (-950, -3450), [(x_first - 7, -3900)], arrow='oblique')
K.note('Ф1', (1300, -3450), [(750, -3850)], l2='ш.400х400', arrow='oblique')
K.note('Стена', (450, -3250), [(125, -3500)], l2='условно не показана', arrow='arrow')
K.axis('k21a', 'А', (0, -3200), (0, -4800))
for i, (v, z, dn) in enumerate([('-3,700', -3700, 0), ('-4,100', -4100, 1)]): K.level('k21l%d' % i, v, -625, z, down=dn)

# ===================== 5.3–5.6 доп. арматура (стиль Онкоцентр 3.3–3.6) =====================
Z2 = json.load(open('zones2.json'))
ANCH = lambda d: int(math.ceil(40 * d / 50.0) * 50)
pos = [dict(n='1', d=D0, L='пог.м.', cnt=None, note='основная, низ+верх, оба направления')]
nxt = [2]
DOPS = [('3.3', 'bot_x', 'нижней зоны по буквенным осям'), ('3.4', 'top_x', 'верхней зоны по буквенным осям'),
        ('3.5', 'bot_y', 'нижней зоны по цифровым осям'), ('3.6', 'top_y', 'верхней зоны по цифровым осям')]
gx = lambda v: FXO + 50 + 200 * round((v - FXO - 50) / 200.0)             # base bar lines (50 from the edge)
for num, key, nm in DOPS:
    S = frameA3(num, FX[num], 'Схема расположения доп. арматуры\PФм-1 ' + nm)
    S.title('Схема расположения дополнительной арматуры фундамента Фм-1 ' + nm + ' на отм. -3.700', 1200, FYE + 2600, cx=7375)
    slab_plan(S); plan_axes(S, 'D' + num.replace('.', ''), (FXO, FYO, FXE, FYE))
    dr = key[-1]
    for z in Z2[key]['zones']:
        d = z['d']; a = ANCH(d)
        if dr == 'x':
            p0 = gx(z['y0']) + 100; p1 = gx(z['y1']) - 100                  # dop bars between base bars
            if p1 < p0: p1 = p0
            n = int(round((p1 - p0) / 200.0)) + 1
            xa, xb = max(z['x0'] - a, FXO + 50), min(z['x1'] + a, FXE - 50); L = int(xb - xa)
            for yy in (p0, p1): add(t='pl', p=[S.P(xa, yy), S.P(xb, yy)], closed=False, layer='диам%d' % d)
            ax = [v for v in AX.values() if xa < v < xb]
            S.chain(sorted({xa, xb} | set(ax[:1])), p1, p1 + 300)                  # length bound to an axis, right above the bar
            if n > 1: dimtxt(S, p0, p1, (xb, xb + 350), '200x%d' % (n - 1), vert=True)
            xc = xa + 200 * int(0.3 * (xb - xa) / 200) + 100; tg = [(xc, p0), (xc, p1)] if n > 1 else [(xc, p0)]
            org = (xc, (p0 + p1) / 2) if n > 1 else (xc + 300, p0 - 700)
        else:
            p0 = gx(z['x0']) + 100; p1 = gx(z['x1']) - 100
            if p1 < p0: p1 = p0
            n = int(round((p1 - p0) / 200.0)) + 1
            ya, yb = max(z['y0'] - a, FYO + 50), min(z['y1'] + a, FYE - 50); L = int(yb - ya)
            for xx in (p0, p1): add(t='pl', p=[S.P(xx, ya), S.P(xx, yb)], closed=False, layer='диам%d' % d)
            ay = [v for v in AY.values() if ya < v < yb]
            S.chain(sorted({ya, yb} | set(ay[:1])), p0, p0 - 300, vert=True)
            if n > 1: dimtxt(S, p0, p1, (yb, yb + 350), '200x%d' % (n - 1))
            yc = ya + 200 * int(0.3 * (yb - ya) / 200) + 100; tg = [(p0, yc), (p1, yc)] if n > 1 else [(p0, yc)]
            org = ((p0 + p1) / 2, yc) if n > 1 else (p0 + 400, yc + 400)
        old = [q for q in pos if q.get('key') == (d, L)]
        if old: old[0]['cnt'] += n; pn = old[0]['n']
        else:
            pn = str(nxt[0]); nxt[0] += 1
            pos.append(dict(n=pn, d=d, L=L, cnt=n, note=('низ' if key.startswith('bot') else 'верх') + ', между поз.1', key=(d, L)))
        S.note(pn, org, tg, l2='ш.200', arrow='oblique')                    # analog: note on the line linking first and last bar
    notes(FX[num], 340000.0, 0, [
        'Общие указания см. лист 1. Данный лист читать совместно с листами 3.2 и 3.8.',
        'Дополнительные стержни укладывать в одном уровне с основной арматурой, посередине шага основных стержней (ш.200 со смещением 100).',
        'Показаны первый и последний стержни каждой зоны; длины стержней - в спецификации (лист 3.8).',
        'Стыки рабочей арматуры внахлестку без сварки, длина нахлеста 71d; в одном сечении стыковать не более 50%.'])
json.dump(pos, open('fm1_pos.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)

notes(*[FX['3.1'], 340000.0], 0, [
    'Общие указания см. лист 1. Схему расположения элементов см. лист 2.1.',
    'Плита днища Фм-1 - монолитная, бетон по общим указаниям, толщина 400 мм, консоль 500 мм за наружную грань стен.',
    'Под плитой выполнить бетонную подготовку (подбетонку) из бетона C8/10 толщиной 100 мм.',
    'Приямок Пр-1 бетонировать совместно с плитой Фм-1.'])
notes(*[FX['3.2'], 340000.0], 0, [
    'Общие указания см. лист 1. Данный лист читать совместно с листами 3.1, 3.3 - 3.8.',
    'Поз. 1 - %%C14 A500C шаг 200 в нижней и верхней сетке в обоих направлениях (основная арматура по толщине плиты 400 мм).',
    'По периметру плиты - П-образная скоба Ск1 %%C14, высота 320 мм (Hплиты - 80), ноги 800 мм, шаг 200.',
    'Сетки фиксировать Ф1 (%%C12, полки 300 мм) с шагом 400х400 в шахматном порядке.',
    'Стыки внахлестку без сварки, длина нахлеста 71d; в одном сечении стыковать не более 50% стержней. Расход в пог.м. с учетом нахлеста.',
    'Защитный слой бетона: низ - 50 мм, верх - 40 мм.'])

ops = [{'t': 'eraseregion', 'win': [113750, 339500, 365700, 370000], 'mode': 'intersect'}] + C.ops + [{'t': 'regen'}]
json.dump(ops, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(ops), 'ops')
