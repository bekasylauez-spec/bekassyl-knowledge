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
    s.dim(a, b, off, vert, txt=txt)

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
FX = {'3.1': 113700.0, '3.2': 155700.0, '3.3': 197700.0, '3.4': 208200.0, '3.5': 250200.0, '3.6': 292200.0, '3.7': 334200.0}
S = frameA3('3.1', FX['3.1'], 'Опалубочный чертеж\\Pфундамента Фм-1')
S.title('Опалубочный чертеж фундамента Фм-1 на отм. -3.700', 1200, FYE + 2600, cx=7375)
slab_plan(S, hatch_walls=True)
plan_axes(S, 'O1', (FXO, FYO, FXE, FYE))
S.chain([0, 4625, 5625], 14125, 15400); S.chain([13125, 14125, 17750], 4625, 4100, vert=True)
S.plevel('O1p', '-4,200', 6200, 12700)
S.section('o11', '1', (2500, FYO - 2600), (2500, 2300))          # 1-1 through the console at wall А
S.section('o12', '2', (3300, 13625), (7200, 13625))              # 2-2 through the pit
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
for a_, b_ in ((FXO, FXO + e), (FXO + e + 200 * nY, FXE)): S.dim(a_, b_, (FYE, FYE + 1000))
dimtxt(S, FXO + e, FXO + e + 200 * nY, (FYE, FYE + 1000), '200x%d=%d' % (nY, 200 * nY))
S.dim(FYO, FYO + e, (FXE, FXE + 1000), vert=True, tx=(FYO - 350, FXE + 1000 - 330))   # short «50» kept off the stamp
S.dim(FYO + e + 200 * nX, FYE, (FXE, FXE + 1000), vert=True)
dimtxt(S, FYO + e, FYO + e + 200 * nX, (FXE, FXE + 1000), '200x%d=%d' % (nX, 200 * nX), vert=True)
S.section('a21', '1', (2500, FYO - 2600), (2500, 2300))
# ===================== 3.3 Разрезы Фм-1 (A3, М 1:25 — все обозначения 25) =====================
frame(FX['3.3'], 340000.0, 25, 'Разрезы фундамента Фм-1', '3.3', 'A3')
# --- 1-1 армирование (edge at axis А), top-left
K = Sheet(FX['3.3'] + 2600, 340000.0 + 9700, 25); K.cx, K.cy = 400, -3900
K.avoid_y = [-3700, -4100, -4200]; K.avoid_x = [0]
K.title('Разрез 1-1 (Армирование)', -700, -2640, cx=440)
XR = 1500
K.pl([(XR, -4100), (-625, -4100), (-625, -3700), (XR, -3700)], closed=False)
K.thin([(XR, -4100), (XR + 60, -3990), (XR - 60, -3810), (XR, -3700)])
K.thin([(-125, -3700), (-125, -3350)]); K.thin([(125, -3700), (125, -3350)])
K.thin([(-200, -3350), (-30, -3350), (0, -3290), (30, -3410), (60, -3350), (200, -3350)])
K.hatch([[(-125, -3700), (125, -3700), (125, -3350), (-125, -3350)]])
K.thin([(-725, -4200), (XR, -4200)]); K.thin([(-725, -4200), (-725, -4100)])
yb1, yt1 = -4100 + CB + 7, -3700 - CT - 7
x_first = -625 + 50
add(t='pl', p=[K.P(x_first, yb1), K.P(XR, yb1)], closed=False, layer='диам14')
add(t='pl', p=[K.P(x_first, yt1), K.P(XR, yt1)], closed=False, layer='диам14')
for i in range(int((XR - x_first) / 200) + 1):
    xx = x_first + 200 * i
    for yy in (yb1 + 14, yt1 - 14): add(t='clone', h='24323', base=[534291, 275556], to=K.P(xx, yy), s=14 / 32.0)
sk = [(x_first + SK_LEG[D0], yb1 - 14), (x_first - 7, yb1 - 14), (x_first - 7, yt1 + 14), (x_first + SK_LEG[D0], yt1 + 14)]
add(t='pl', p=[K.P(*q) for q in sk], closed=False, layer='диам14', color=3)
f1 = [(150, yb1 + 28), (450, yb1 + 28), (450, yt1 - 28), (750, yt1 - 28), (750, yb1 + 28), (1050, yb1 + 28)]
add(t='pl', p=[K.P(*q) for q in f1], closed=False, layer='диам12')
K.chain([-4100, -4100 + CB, -3700 - CT, -3700], -625, -625 - 250, vert=True)
K.dim(-4100, -3700, (-625, -625 - 500), vert=True)
K.chain([-625, -125, 0, 125], -3350, -3350 + 250)          # analog: 125|125 wall to axis + overhang
nn = int((XR - 100 - x_first) / 200)
K.dim(-625, x_first, (-4200, -4200 - 250))
dimtxt(K, x_first, x_first + 200 * nn, (-4200, -4200 - 250), '200x%d=%d' % (nn, 200 * nn))
K.note('1', (XR + 50, -4450), [(XR + 450, -4450)], l2='ш.200', arrow='arrow')
K.note('1', (1000, -3450), [(800, yt1)], l2='ш.200', arrow='oblique')
K.note('1', (1150, -4750), [(1025, yb1 + 14), (825, yb1 + 14)], l2='ш.200', arrow='none')
K.note('Ск1', (-950, -3450), [(x_first - 7, -3900)], arrow='oblique')
K.note('Ф1', (1350, -3200), [(750, -3850)], l2='ш.400х400', arrow='oblique')
K.note('Стена', (450, -3150), [(125, -3500)], l2='условно не показана', arrow='arrow')
K.axis('k21a', 'А', (0, -3200), (0, -4200 - 500 - 300))
for i, (v, z, dn) in enumerate([('-3,700', -3700, 0), ('-4,100', -4100, 1)]): K.level('k21l%d' % i, v, -625, z, down=dn)
# --- 1-1 опалубка, top-right
K1 = Sheet(FX['3.3'] + 7600, 340000.0 + 9700, 25); K1.cx, K1.cy = 600, -3900
K1.avoid_y = [-3700, -4100, -4200]; K1.avoid_x = [0]
K1.title('Разрез 1-1 (опалубка)', -625, -2640, cx=590)
K1.solid((-625, -4100, 1800, -3700)); K1.solid((-125, -3700, 125, -3350))
K1.thin([(1800, -4100), (1860, -3990), (1740, -3810), (1800, -3700)])   # break line (analog)
K1.pl(rect((-725, -4200, 1800, -4100)), layer='Тонкая'); K1.hatch([rect((-725, -4200, 1800, -4100))], pat='AR-CONC', sc=0.4, layer='Бетон штриховка')
K1.axis('k1a', 'А', (0, -3200), (0, -4200 - 500 - 300))
K1.chain([-125, 0, 125], -3350, -3350 + 250)                     # wall to axis 125|125 (analog 3.1)
K1.chain([-725, -625, 0], -4200, -4200 - 250)                   # подбетонка 100 | overhang to axis
K1.chain([-4200, -4100, -3700], -725, -725 - 250, vert=True)
for i, (v, z, dn) in enumerate([('-3,700', -3700, 0), ('-4,100', -4100, 1)]): K1.level('k1l%d' % i, v, -725, z, down=dn)
K1.note('Фм-1', (1300, -3300), [(900, -3700)])
K1.note('Подбетонка C8/10', (1300, -4600), [(900, -4200)], l2='t=100')
# --- 2-2 опалубка (pit), bottom-left
K2 = Sheet(FX['3.3'] - 1700, 340000.0 + 7100, 25); K2.cx, K2.cy = 5100, -3900
K2.avoid_y = [-3700, -4200, -4600, -4700]; K2.avoid_x = []
K2.title('Разрез 2-2 (опалубка)', 3800, -3100, cx=5125)
x0, x1 = 3800, 6450
prof = [(x0, -4100), (pitb[0], -4100), (pitb[0], -4600), (pitb[2], -4600), (pitb[2], -4100), (x1, -4100), (x1, -3700),
        (pit[2], -3700), (pit[2], -4200), (pit[0], -4200), (pit[0], -3700), (x0, -3700)]
K2.pl(prof); K2.hatch([prof])
K2.thin([(x0, -4100), (x0 - 60, -3990), (x0 + 60, -3810), (x0, -3700)]); K2.thin([(x1, -4100), (x1 + 60, -3990), (x1 - 60, -3810), (x1, -3700)])
pb = [(x0, -4100), (pitb[0], -4100), (pitb[0], -4600), (pitb[2], -4600), (pitb[2], -4100), (x1, -4100),
      (x1, -4200), (pitb[2] + 100, -4200), (pitb[2] + 100, -4700), (pitb[0] - 100, -4700), (pitb[0] - 100, -4200), (x0, -4200)]
K2.pl(pb, layer='Тонкая'); K2.hatch([pb], pat='AR-CONC', sc=0.4, layer='Бетон штриховка')   # подбетонка under the pit (analog 2-2)
K2.note('Подбетонка C8/10', (pitb[0] - 900, -5000), [(pitb[0] - 50, -4650)], l2='t=100')
K2.chain([pitb[0], pit[0], pit[2], pitb[2]], -4700, -4700 - 250)
K2.chain([-4700, -4600, -4200, -3700], x1, x1 + 250, vert=True)
K2.dim(-4700, -3700, (x1, x1 + 500), vert=True)
for i, (v, z, dn) in enumerate([('-3,700', -3700, 0), ('-4,200', -4200, 1), ('-4,600', -4600, 1)]):
    K2.level('k2l%d' % i, v, x0, z, down=dn)
K2.note('Пр-1', (pit[2] + 400, -3300), [(pit[2], -3900)])
notes(FX['3.3'], 340000.0, 0, [
    'Разрезы читать совместно с листами 3.1, 3.2.',
    'Защитный слой бетона: низ - 50 мм, верх - 40 мм. Ск1 %%C14, ноги 800 мм.',
    'Армирование приямка Пр-1 - по месту по основной сетке с перепуском 700 мм (%%C14).'], sc=25)

# ===================== 5.3–5.6 доп. арматура (стиль Онкоцентр 3.3–3.6) =====================
Z2 = json.load(open('zones2.json'))
ANCH = lambda d: {10: 500, 12: 600, 14: 700, 16: 800, 18: 850, 20: 950, 22: 1050, 25: 1200, 28: 1300, 32: 1500}[d]   # vault: 09_Таблицы/Анкеровки
pos = [dict(n='1', d=D0, L='пог.м.', cnt=None, note='основная, низ+верх, оба направления')]
nxt = [2]
DOPS = [('3.4', 'bot_x', 'нижней зоны по буквенным осям'), ('3.5', 'top_x', 'верхней зоны по буквенным осям'),
        ('3.6', 'bot_y', 'нижней зоны по цифровым осям'), ('3.7', 'top_y', 'верхней зоны по цифровым осям')]
gx = lambda v: FXO + 50 + 200 * round((v - FXO - 50) / 200.0)             # base bar lines (50 from the edge)
for num, key, nm in DOPS:
    S = frameA3(num, FX[num], 'Схема расположения доп. арматуры\PФм-1 ' + nm)
    S.title('Схема расположения дополнительной арматуры фундамента Фм-1 ' + nm + ' на отм. -3.700', 1200, FYE + 2600, cx=7375)
    slab_plan(S); plan_axes(S, 'D' + num.replace('.', ''), (FXO, FYO, FXE, FYE))
    dr = key[-1]; done = []                                              # (p0, p1, a, b, d, n, L) of the zones
    for z in Z2[key]['zones']:
        d = z['d']; a = ANCH(d)
        lo_, hi_ = ('y0', 'y1') if dr == 'x' else ('x0', 'x1')
        p0 = gx(z[lo_]) + 100; p1 = max(gx(z[hi_]) - 100, gx(z[lo_]) + 100)  # dop bars between base bars
        n = int(round((p1 - p0) / 200.0)) + 1
        if dr == 'x': ea, eb = max(z['x0'] - a, FXO + 50), min(z['x1'] + a, FXE - 50)
        else: ea, eb = max(z['y0'] - a, FYO + 50), min(z['y1'] + a, FYE - 50)
        done.append((p0, p1, ea, eb, d, n, int(eb - ea)))
    obst = [(pitb[0], pitb[2], pitb[1], pitb[3]) if dr == 'y' else (pitb[1], pitb[3], pitb[0], pitb[2])]   # pit outline (p-range, e-range)
    near = lambda r, side: any(q is not r and min(r[3], q[3]) > max(r[2], q[2]) and
                               (0 < (q[0] - r[1] if side > 0 else r[0] - q[1]) < 1600) for q in done + obst)
    for r in done:
        p0, p1, ea, eb, d, n, L = r
        side = -1 if (dr == 'y' and not near(r, -1)) or (dr == 'x' and near(r, 1)) else 1
        if dr == 'x':
            for yy in (p0, p1): add(t='pl', p=[S.P(ea, yy), S.P(eb, yy)], closed=False, layer='диам%d' % d)
            ax = [v for v in AX.values() if ea < v < eb]; pb_ = p1 if side > 0 else p0
            S.chain(sorted({ea, eb} | set(ax[:1])), pb_, pb_ + side * 400)       # length bound to an axis, beside the bar
            if n > 1: dimtxt(S, p0, p1, (eb, eb + 600), '200x%d' % (n - 1), vert=True)
            xc = ea + 200 * int(0.3 * (eb - ea) / 200) + 100; tg = [(xc, p0), (xc, p1)] if n > 1 else [(xc, p0)]
            org = (xc, (p0 + p1) / 2) if (n > 1 and p1 - p0 >= 1200) else (xc, p1 + 500)
        else:
            for xx in (p0, p1): add(t='pl', p=[S.P(xx, ea), S.P(xx, eb)], closed=False, layer='диам%d' % d)
            ay = [v for v in AY.values() if ea < v < eb]; pb_ = p1 if side > 0 else p0
            S.chain(sorted({ea, eb} | set(ay[:1])), pb_, pb_ + side * 400, vert=True)
            if n > 1: dimtxt(S, p0, p1, (eb, eb + 600), '200x%d' % (n - 1))
            yc = ea + 200 * int(0.3 * (eb - ea) / 200) + 100; tg = [(p0, yc), (p1, yc)] if n > 1 else [(p0, yc)]
            org = ((p0 + p1) / 2, yc) if (n > 1 and p1 - p0 >= 1200) else (p1 + 500, yc)
        old = [q for q in pos if q.get('key') == (d, L)]
        if old: old[0]['cnt'] += n; pn = old[0]['n']
        else:
            pn = str(nxt[0]); nxt[0] += 1
            pos.append(dict(n=pn, d=d, L=L, cnt=n, note=('низ' if key.startswith('bot') else 'верх') + ', между поз.1', key=(d, L)))
        S.note(pn, org, tg, l2='ш.200', arrow='oblique')                    # analog: note on the line linking first and last bar
    # analog 3.3/3.5: gap between neighbouring zones dimensioned («200»), on the distribution line of the lower zone
    for r in done:
        for q in done:
            if 0 < q[0] - r[1] <= 400 and min(r[3], q[3]) - max(r[2], q[2]) > 0:
                e_ = min(r[3], q[3]) + 600
                S.dim(r[1], q[0], (min(r[3], q[3]), e_), vert=(dr == 'x'))
    notes(FX[num], 340000.0, 0, [
        'Общие указания см. лист 1.1. Данный лист читать совместно с листами 3.1 - 3.3 и 3.9.',
        'Дополнительные стержни укладывать в одном уровне с основной арматурой, посередине шага основных стержней (ш.200 со смещением 100).',
        'Показаны первый и последний стержни каждой зоны; длины стержней - в спецификации (лист 3.9).',
        'Стыки рабочей арматуры внахлестку без сварки, на скрутках из вязальной проволоки (не менее 3 шт. на стык), длина нахлеста 71d; в одном сечении стыковать не более 50%.',
        'Расход арматуры в погонных метрах приведен с учетом нахлеста.'])
json.dump(pos, open('fm1_pos.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)

notes(*[FX['3.1'], 340000.0], 0, [
    'Общие указания см. лист 1. Схему расположения элементов см. лист 2.1.',
    'Плита днища Фм-1 - монолитная, бетон по общим указаниям, толщина 400 мм, консоль 500 мм за наружную грань стен.',
    'Под плитой выполнить бетонную подготовку (подбетонку) из бетона C8/10 толщиной 100 мм.',
    'Приямок Пр-1 бетонировать совместно с плитой Фм-1.'])
notes(*[FX['3.2'], 340000.0], 0, [
    'Общие указания см. лист 1. Данный лист читать совместно с листами 3.1, 3.3 - 3.9.',
    'Поз. 1 - %%C14 A500C шаг 200 в нижней и верхней сетке в обоих направлениях (основная арматура по толщине плиты 400 мм).',
    'По периметру плиты - П-образная скоба Ск1 %%C14, высота 320 мм (Hплиты - 80), ноги 800 мм, шаг 200.',
    'Сетки фиксировать Ф1 (%%C12, полки 300 мм) с шагом 400х400 в шахматном порядке.',
    'Стыки внахлестку без сварки, длина нахлеста 71d; в одном сечении стыковать не более 50% стержней. Расход в пог.м. с учетом нахлеста.',
    'Защитный слой бетона: низ - 50 мм, верх - 40 мм.'])

ops = [{'t': 'eraseregion', 'win': [113750, 339500, 380000, 370000], 'mode': 'intersect'}, {'t': 'eraseregion', 'win': [590000, 330000, 650000, 380000], 'mode': 'intersect'}] + C.ops + [{'t': 'regen'}]
json.dump(ops, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(ops), 'ops')
